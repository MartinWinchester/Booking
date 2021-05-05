from flask import Flask, jsonify, json
from flask_restful import Api, Resource, reqparse
import Utils
import uuid
import argparse
from DataBase import DB
from dateutil import parser as datetimeparser
import time

from Map import Map

app = Flask(__name__)
api = Api(app)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-s", "--server", default="localhost:8080")
arg_parser.add_argument("-db", "--database", default="localhost:27020")
arg_parser.add_argument("-dbr", "--database_replicas", default=2)
arg_parser.add_argument("-gdb", "--globaldb", default="localhost:37019")
arg_parser.add_argument("-gdbr", "--global_database_replicas", default=2)
arg_parser.add_argument("-i", "--serverid", default="0")
args = arg_parser.parse_args()

TransactionTimeout = 8

OwnUrl = args.server
DbUrl = args.database
MapUrl = args.globaldb
ServerId = int(args.serverid)
PortBaseServer = 8080
PortBaseTripDb = 27020
PortJourneyDb = str.split(args.globaldb, ':')[1]
PortServer = PortBaseServer + ServerId
PortTripDb = PortBaseTripDb + ServerId
TransLogFile = "../TransactionLogs/transaction_logs_" + str(ServerId) + ".txt"
TripReps = [(str.split(args.database, ':')[0], int(str.split(args.database, ':')[1]) + index) for index in
            range(int(args.database_replicas)+1)]
JourneyReps = [(str.split(args.globaldb, ':')[0], int(str.split(args.globaldb, ':')[1]) + index) for index in
               range(int(args.global_database_replicas)+1)]
# todo fetch map first, pass to map parser
Util = Utils.Util()
Util.port = PortServer
DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(None)
db = DB(str.split(args.server, ':')[0], PortTripDb, str.split(args.globaldb, ':')[0],
        int(str.split(args.globaldb, ':')[1]), TripReps, JourneyReps)


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

        jid = str(uuid.uuid4())
        # todo check that Source, Destination in Map
        cities = Util.find_shortest_path(args['Source'], args['Destination'])
        # todo wait for task to find update time to finish
        if MapLatest < new_update_time:
            # todo: change next line to fetch request from real DB
            map = None
            DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, OwnCities = Util.parse_map_cities_servers(map)
            cities = Util.find_shortest_path(args['Source'], args['Destination'])
        city_contacts = [(CitiesToServers[city[0]], city[0], city[1], city[2]) for city in cities]
        own_trips = [city_tuple for city_tuple in city_contacts if city_tuple[1] in OwnCities]
        city_contacts = [city_tuple for city_tuple in city_contacts if city_tuple[1] not in OwnCities]
        # todo Log "prepared" to log file with JID, city_contacts
        start_time = datetimeparser.parse(args['At'], fuzzy_with_tokens=True)
        # todo actually check for timeouts
        timeout_start = time.perf_counter()

        prepared_resps = []
        # send all followers "prepared" message
        prepared_resps = Util.leader_transaction_message(city_contacts, start_time, jid, "book", "prepared")

        failed = [response for response in prepared_resps if response[4].text == "Link at capacity"]
        if failed:
            # at least 1 link is at capacity
            # send all followers "abort" message
            # don't necessarily need to make sure all followers notified, worst case followers timeout
            while failed:
                resps = Util.leader_transaction_message(city_contacts, start_time, jid, "book", "abort")
                failed = [response for response in resps if response[4].status_code != 200]
            # Journey denied because link is at capacity
            return {'message': "Journey denied."}, 503

        # so far so good
        failed = [res for res in prepared_resps if res[4].status_code != 200]
        if failed:
            wait_timer = 0.0001
            # at least 1 server could not book
            # send all followers "abort" message
            while failed:
                # not really necessary
                time.sleep(wait_timer)
                resps = Util.leader_transaction_message(city_contacts, start_time, jid, "book", "prepared")
                if [response for response in prepared_resps if response[4].text == "Link at capacity"]:
                    # Journey denied because link is at capacity
                    return {'message': "Journey denied."}, 503
                wait_timer += 1
                failed = [response for response in resps if response[4].status_code != 200]

        # by the time we're here no aborts
        # todo log commit
        # todo insert into journeys

        # todo commit own_trips
        failed = city_contacts
        while failed:
            # send all followers "commit" message
            resps = Util.leader_transaction_message(city_contacts, start_time, jid, "book", "commit")
            failed = [response for response in resps if response[4].status_code != 200]

        # todo log complete
        return {'message': "Journey booked successfully."}, 201

    def delete(self):
        parser = reqparse.RequestParser()
        # user ID
        parser.add_argument('UID', required=True)
        # journey ID
        parser.add_argument('JID', required=True)
        args = parser.parse_args()

        result = Util.try_delete(args['UID'], args['JID'])

        if result == 0:
            return {'message': 'Journey deleted successfully.'}, 204
        if result == 1:
            return {'message': 'Journey not found.'}, 404
        if result == 2:
            return {'message': "Operation failed. Try again."}, 503


class Transaction(Resource):
    # internal endpoint for server to server communication
    def post(self):
        global DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest, MapUrl, OwnCities, db
        # todo: change next line to fetch request from real DB
        mapp = None
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
        if trips is not None:
            for trip in trips:
                if trip["From"] not in OwnCities:
                    return {'message': 'City moved'}, 400

        # no need for follower log file, but it helps when restarting if leader logged commit but new booking request
        # comes in before leader retransmit

        if transaction_status == "prepared":
            # todo actually check for timeouts
            timeout_start = time.perf_counter()
            for trip in trips:
                # todo read lock DB
                # todo check if links at capacity
                load = db.getByCityAndTime(trip[0], trip[3])["Capacity"]
                # after or: Jid was used before, retry transaction
                if jid not in db.getByCityAndTime(trip[0], trip[3])["JID"]:
                    return {'message': 'Retry'}, 400
                if load >= CapacityMap[Util.Cities.inverse[trip[0]], Util.Cities.inverse[trip[1]]]:
                    # todo write lock DB
                    return {'message': 'Link at capacity'}, 400
            return {'message': 'Ok'}, 200

        elif transaction_status == "commit":
            # todo trip with supplied jid had already been added to DB
            if jid not in db.getByCityAndTime(trip[0], trip[3])["JID"]:
                for trip in trips:
                    DB.addTrip(trip)
            return {'message': 'Ok'}, 200

        elif transaction_status == "abort":
            return {'message': 'Ok'}, 200
            # todo release DB lock
        else:
            return {'message': 'transaction_status should be one of prepared, commit or abort'}, 400


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

    app.run(host=str.split(args.server, ':')[0], port=str.split(args.server, ':')[1])
