from flask import Flask, jsonify, json
from flask_restful import Api, Resource, reqparse
import Utils
import uuid
import argparse
from DataBase import DB
import datetime
from dateutil import parser as datetimeparser
import time
from os import path

from Map import Map

app = Flask(__name__)
api = Api(app)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-s", "--server", default="localhost:8080")
arg_parser.add_argument("-db", "--database", default="localhost:27020")
arg_parser.add_argument("-dbr", "--database_replicas", default=2)

arg_parser.add_argument("-gdb", "--globaldb", default="localhost:27119")
arg_parser.add_argument("-gdbr", "--global_database_replicas", default=2)

arg_parser.add_argument("-mdb", "--mapdb", default="localhost:27001")
arg_parser.add_argument("-mdbr", "--map_database_replicas", default=2)

arg_parser.add_argument("-i", "--serverid", default="0")
args = arg_parser.parse_args()

TransactionTimeout = 8

OwnUrl = args.server
DbUrl = args.database
MapUrl = args.globaldb
ServerId = int(args.serverid)
# PortBaseServer = 8080
# PortBaseTripDb = 27020
PortJourneyDb = str.split(args.globaldb, ':')[1]
# PortServer = PortBaseServer + ServerId
# PortTripDb = PortBaseTripDb + ServerId
PortServer = int(str.split(args.server, ':')[1])
PortTripDb = int(str.split(args.database, ':')[1])
PortMapDb = int(str.split(args.mapdb, ':')[1])


# TransLogFile = "../TransactionLogs/transaction_logs_" + str(ServerId) + ".txt"
TransLogFile = "transaction_logs_" + str(ServerId) + ".txt"

TripReps = [(str.split(args.database, ':')[0], int(str.split(args.database, ':')[1]) + index*10) for index in
            range(int(args.database_replicas)+1)]
JourneyReps = [(str.split(args.globaldb, ':')[0], int(str.split(args.globaldb, ':')[1]) + index*10) for index in
               range(int(args.global_database_replicas)+1)]
# todo fetch map first, pass to map parser
Util = Utils.Util(ServerId)
Util.port = PortServer

db = DB(str.split(args.server, ':')[0], PortTripDb,
    str.split(args.globaldb, ':')[0],int(str.split(args.globaldb, ':')[1]),
    str.split(args.mapdb, ':')[0],int(str.split(args.mapdb, ':')[1]),
     TripReps, JourneyReps)
mappp=db.get_map()
print(mappp)
DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(mappp)


class Book(Resource):
    def get(self):
        global db
        # fetch users bookings
        parser = reqparse.RequestParser()
        parser.add_argument('UID', required=True)
        args = parser.parse_args()
        # find all bookings for given UID
        uid = args['UID']
        result = json.dumps(db.getByUUID(uid))
        return result, 200

    def post(self):
        global DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, MapUrl, OwnCities, db
        # todo task to find update timestamp
        # new_update_time = DB.getMapUpdateTime()
        new_update_time = MapLatest
        parser = reqparse.RequestParser()
        parser.add_argument('Source', location='form')
        parser.add_argument('Destination', location='form')
        # user ID
        parser.add_argument('UID', location='form')
        # time of departure
        parser.add_argument('At', location='form')
        args = parser.parse_args()

        # can put all states into 1 big nested loop, might need for failover
        jid = str(uuid.uuid4())
        # todo check that Source, Destination in Map
        cities = Util.find_shortest_path(args['Source'], args['Destination'])
        # todo wait for task to find update time to finish
        # if MapLatest < new_update_time:
        
        mapp = db.get_map()
        print(mapp)
        DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(mapp)
            # hops [(From, To, Duration)]
        cities = Util.find_shortest_path(args['Source'], args['Destination'])
        # [(Url, From, To, Duration)]
        city_contacts = [(CitiesToServers[city[0]], city[0], city[1], city[2]) for city in cities]
        # trips dealt with locally
        own_trips = [city_tuple for city_tuple in city_contacts if city_tuple[1] in OwnCities]
        # trips dealt by other servers
        follower_trips = [city_tuple for city_tuple in city_contacts if city_tuple[1] not in OwnCities]

        start_time = datetimeparser.parse(args['At'], fuzzy_with_tokens=True)
        
        # PREPARED
        state = "prepared"
        journey = dict()
        journey["JID"] = jid
        journey["Trips"] = city_contacts
        journey["Cities"] = [city_tuple[0] for city_tuple in cities] + [cities[-1][1]]
        journey["StartTime"] = start_time[0].strftime("%m/%d/%Y, %H:%M:%S")
        journey["Times"] = [start_time[0].strftime("%m/%d/%Y, %H:%M:%S")] + \
                           [(start_time[0] + datetime.timedelta(hours=t)).strftime("%m/%d/%Y, %H:%M:%S")
                            for (_, _, _, t) in city_contacts]
        log = dict()
        log["Leader"] = True
        log["JID"] = jid
        log["UID"] = args['UID']
        log["Type"] = "book"
        log["Trips"] = json.dumps(city_contacts)
        log["Status"] = "prepared"
        log["Followers"] = [city_tuple[0] for city_tuple in cities] + [cities[-1][1]]
        log["Journey"] = journey
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))
        # todo actually check for timeouts
        timeout_start = time.perf_counter()

        # send all followers "prepared" message
        prepared_resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)

        '''failed = [response for response in prepared_resps if response[4].text == "Link at capacity"]
        if failed:
            state = "abort"
            # at least 1 link is at capacity
            # send all followers "abort" message
            # don't necessarily need to make sure all followers notified, worst case followers timeout
            while failed:
                resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)
                failed = [response for response in resps if response[4].status_code != 200]
                if [response for response in prepared_resps if response[4].text == "Link at capacity"]:
                    # ABORT
                    # todo send abort message to all followers
                    # Journey denied because link is at capacity
                    log["Status"] = state
                    if path.isfile(TransLogFile):
                        with open(TransLogFile, "a") as fp:
                            fp.write(',\n' + json.dumps(log))
                    else:
                        with open(TransLogFile, "w") as fp:
                            fp.write(json.dumps(log))
                    return {'message': "Journey denied."}, 503'''

        # so far so good
        failed = [res for res in prepared_resps if res[4].status_code != 200]
        if failed:
            wait_timer = 0.0001
            # at least 1 server could not book
            # send all followers "abort" message
            while failed:
                # not really necessary
                time.sleep(wait_timer)
                resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)
                if [response for response in prepared_resps if response[4].text == "Link at capacity"]:
                    # ABORT
                    state = "abort"
                    resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)
                    # Journey denied because link is at capacity
                    log["Status"] = "abort"
                    if path.isfile(TransLogFile):
                        with open(TransLogFile, "a") as fp:
                            fp.write(',\n' + json.dumps(log))
                    else:
                        with open(TransLogFile, "w") as fp:
                            fp.write(json.dumps(log))
                    return {'message': "Journey denied."}, 503
                wait_timer += 1
                failed = [response for response in resps if response[4].status_code != 200 and
                          response[4].text != "Link at capacity"]

        dictTrips = Util.dictionary_trips(jid, start_time,own_trips)
        tmsg,serverRsp = Util.book_transaction(jid, dictTrips, state, db)
        print("server prepared state response")
        print(tmsg)
        print(serverRsp)
        if serverRsp==400:
            return {'message': "Journey denied."}, 503

        # by the time we're here no aborts
        # COMMIT
        state = "commit"
        log["Status"] = state
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))

        # dict_trips = json.dumps([
        #         {"From": city[1], "To": city[2], "At": trip_start_time.strftime("%m/%d/%Y, %H:%M:%S")}])
        
        print("In server")
        print("state"+str(state))
        resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)
        failed = [response for response in resps if response[4].status_code != 200]

        print("!!!!!!")
        print(journey)
        print(args['UID'])
        db.addJourney(args['UID'], journey)
        dictTrips = Util.dictionary_trips(jid, start_time,own_trips)
        Util.book_transaction(jid, dictTrips, state, db)


      
        while failed:
            # send all followers "commit" message
            resps = Util.leader_transaction_message(follower_trips, start_time, jid, "book", state)
            failed = [response for response in resps if response[4].status_code != 200]


        # COMLETE
        state = "complete"
        log["Status"] = state
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))
        return {'message': "Journey booked successfully."}, 201

    def delete(self):
        global DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, MapUrl, OwnCities, db
        # todo task to find update timestamp
        # new_update_time = DB.getMapUpdateTime()
        new_update_time = MapLatest

        parser = reqparse.RequestParser()
        # user ID
        parser.add_argument('UID', required=True)
        # journey ID
        parser.add_argument('JID', required=True)
        args = parser.parse_args()


        mapp = db.get_map()
        print(mapp)
        DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(mapp)
        # hops [(From, To, Duration)]
        cities = db.getByJourneyID(args['JID'])["cities"]
        # [(Url, From, To, Duration)]
        city_contacts = [(CitiesToServers[city[0]], city[0], city[1], city[2]) for city in cities]
        # trips dealt with locally
        own_trips = [city_tuple for city_tuple in city_contacts if city_tuple[1] in OwnCities]
        # trips dealt by other servers
        follower_trips = [city_tuple for city_tuple in city_contacts if city_tuple[1] not in OwnCities]

        start_time = datetimeparser.parse(args['At'], fuzzy_with_tokens=True)

        # PREPARED
        state = "prepared"
        journey = dict()
        journey["JID"] = args['JID']
        journey["Trips"] = city_contacts
        journey["Cities"] = [city_tuple[0] for city_tuple in cities] + [cities[-1][1]]

        log = dict()
        log["Leader"] = True
        log["JID"] = args['JID']
        log["UID"] = args['UID']
        log["Type"] = "book"
        log["Trips"] = json.dumps(city_contacts)
        log["Status"] = "prepared"
        log["Followers"] = [city_tuple[0] for city_tuple in cities] + [cities[-1][1]]
        log["Journey"] = journey
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))
        # todo actually check for timeouts
        timeout_start = time.perf_counter()

        # send all followers "prepared" message
        prepared_resps = Util.leader_transaction_message(follower_trips, " ", args['JID'], "cancel", state)

        # so far so good
        failed = [res for res in prepared_resps if res[4].status_code != 200]
        if failed:
            wait_timer = 0.0001
            # at least 1 server could not book
            # send all followers "abort" message
            while failed:
                # not really necessary
                time.sleep(wait_timer)
                resps = Util.leader_transaction_message(follower_trips, " ", args['JID'], "cancel", state)
                if [response for response in prepared_resps if response[4].text == "capacity cannot be less than zero"]:
                    # ABORT
                    state = "abort"
                    resps = Util.leader_transaction_message(follower_trips, " ", args['JID'], "cancel", state)
                    # Journey denied because link is at capacity
                    log["Status"] = "abort"
                    if path.isfile(TransLogFile):
                        with open(TransLogFile, "a") as fp:
                            fp.write(',\n' + json.dumps(log))
                    else:
                        with open(TransLogFile, "w") as fp:
                            fp.write(json.dumps(log))
                    return {'message': "cancel denied."}, 503
                wait_timer += 1
                failed = [response for response in resps if response[4].status_code != 200 and
                          response[4].text != "capacity cannot be less than zero"]

        dictTrips = Util.dictionary_trips(args['JID'], "", own_trips)
        tmsg, serverRsp = Util.cancel_transaction(args['JID'], dictTrips, state, db)
        print("server prepared state response")
        print(tmsg)
        print(serverRsp)
        if serverRsp == 400:
            return {'message': "cancel denied."}, 503

        # by the time we're here no aborts
        # COMMIT
        state = "commit"
        log["Status"] = state
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))

        # dict_trips = json.dumps([
        #         {"From": city[1], "To": city[2], "At": trip_start_time.strftime("%m/%d/%Y, %H:%M:%S")}])

        print("In server")
        print("state" + str(state))
        resps = Util.leader_transaction_message(follower_trips, start_time, args['JID'], "cancel", state)
        failed = [response for response in resps if response[4].status_code != 200]

        print("!!!!!!")
        print(journey)
        print(args['UID'])
        db.addJourney(args['UID'], journey)
        dictTrips = Util.dictionary_trips(jid, start_time, own_trips)
        Util.book_transaction(jid, dictTrips, state, db)

        while failed:
            # send all followers "commit" message
            resps = Util.leader_transaction_message(follower_trips, start_time, args['JID'], "cancel", state)
            failed = [response for response in resps if response[4].status_code != 200]

        # COMLETE
        state = "complete"
        log["Status"] = state
        if path.isfile(TransLogFile):
            with open(TransLogFile, "a") as fp:
                fp.write(',\n' + json.dumps(log))
        else:
            with open(TransLogFile, "w") as fp:
                fp.write(json.dumps(log))
        return {'message': "Journey deleted successfully."}, 204


class Transaction(Resource):
    # internal endpoint for server to server communication
    def post(self):
        global DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, MapUrl, OwnCities, db
        # todo: change next line to fetch request from real DB
        mapp = db.get_map()
        print(mapp)

        DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(mapp)
        parser = reqparse.RequestParser()
        # Journey ID (string)
        parser.add_argument('JID', required=True, location=['form', 'json'])
        # Type: book, cancel (string)
        parser.add_argument('Type', required=True, location=['form', 'json'])
        # Status: prepared, commit, abort (string)
        parser.add_argument('Status', required=True, location=['form', 'json'])
        # Trips: a list of tuples of (link, timeslot)
        parser.add_argument('Trips', location=['form', 'json'])
        args = parser.parse_args()

        jid = args['JID']
        transaction_type = args['Type']
        transaction_status = args['Status']
        trips = json.loads(args['Trips'])
        if transaction_type == "book":
            print("transaction..........")
            return Util.book_transaction(jid, trips, transaction_status, db)

    def delete(self):
        global DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, MapUrl, OwnCities, db
        # todo: change next line to fetch request from real DB
        mapp = db.get_map()
        print(mapp)

        DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(mapp)
        parser = reqparse.RequestParser()
        # Journey ID (string)
        parser.add_argument('JID', required=True, location=['form', 'json'])
        # Type: book, cancel (string)
        parser.add_argument('Type', required=True, location=['form', 'json'])
        # Status: prepared, commit, abort (string)
        parser.add_argument('Status', required=True, location=['form', 'json'])
        # Trips: a list of tuples of (link, timeslot)
        parser.add_argument('Trips', location=['form', 'json'])
        args = parser.parse_args()

        jid = args['JID']
        transaction_type = args['Type']
        transaction_status = args['Status']
        trips = json.loads(args['Trips'])
        if transaction_type == "cancel":
            return Util.cancel_transaction(jid, trips, transaction_status, db)

api.add_resource(Book, '/book')
api.add_resource(Map, '/map')
api.add_resource(Transaction, '/transaction')


if __name__ == '__main__':
    for cit in CitiesToServers:
        if str.split(CitiesToServers[cit], ':')[1] == str(PortServer):
            OwnCities.append(cit)

    # if OurCities:
        # todo: recover transactions
        # todo: recover own database
    if path.isfile(TransLogFile):
        # need to do recovery
        finished = [] # completed or aborted journey transactions
        commit = [] # transactions in commit state
        prepared = [] # transactions in prepared state
        file_object = open(TransLogFile, "r")
        content = file_object.read()
        file_object.close()
        logs = json.loads("[" + content + "]")[::-1]
        for log in logs:
            if log["Leader"]:
                if log["Status"] == "complete" or log["Status"] == "abort":
                    finished.append(log["JID"])
                elif log["Status"] == "prepared" and log["JID"] not in finished:
                    failed = json.loads(log["Trips"])
                    failed = [city_tuple for city_tuple in failed if city_tuple[1] not in OwnCities]
                    while failed:
                        # send all followers "commit" message
                        resps = Util.leader_transaction_message(failed, log["Journey"]["StartTime"], log["JID"], log["Type"], "abort")
                        failed = [response for response in resps if response[4].status_code != 200]
                        log["Status"] = "abort"
                        if path.isfile(TransLogFile):
                            with open(TransLogFile, "a") as fp:
                                fp.write(',\n' + json.dumps(log))
                        else:
                            with open(TransLogFile, "w") as fp:
                                fp.write(json.dumps(log))
                        finished.append(log["JID"])
                elif log["Status"] == "commit" and log["JID"] not in finished:
                    failed = json.loads(log["Trips"])
                    own_trips = [city_tuple for city_tuple in failed if city_tuple[1] in OwnCities]
                    failed = [city_tuple for city_tuple in failed if city_tuple[1] not in OwnCities]
                    db.addJourney(log['UID'], log["Journey"])
                    for trip in own_trips:
                        trp = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])
                        trp["Capacity"] = trp["Capacity"] + 1
                        trp["JID"] = trp["JID"] + [log["JID"]]
                        DB.addTrip(trp)
                    while failed:
                        # send all followers "commit" message
                        resps = Util.leader_transaction_message(failed, log["Journey"]["StartTime"], log["JID"], log["Type"], "commit")
                        failed = [response for response in resps if response[4].status_code != 200]
                    finished.append(log["JID"])
                else:
                    print()
            else:
                if log["Status"] == "complete" or log["Status"] == "abort":
                    finished.append(log["JID"])
                elif log["Status"] == "commit" and log["JID"] not in finished:
                    if log["JID"] not in db.getTripsByLinkAndTime(log["Trips"][0]["From"], log["Trips"][0]["To"], log["Trips"][0]["At"])["JID"]:
                        for trip in log["Trips"]:
                            trp = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])
                            trp["Capacity"] = trp["Capacity"] + 1
                            trp["JID"] = trp["JID"] + log["JID"]
                            DB.addTrip(trp)
                    finished.append(log["JID"])
                else:
                    # do nothing if Status is prepared or start, timeout should take care of it
                    print()
    app.run(host=str.split(args.server, ':')[0], port=str.split(args.server, ':')[1])
