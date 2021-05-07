from scipy import sparse
from scipy.sparse.csgraph import shortest_path
from flask import json
import numpy as np
from bidict import bidict
import datetime
import requests
import time
from DataBase import DB
from dateutil import parser as datetimeparser
from os import path

dummyMapList = '''[{"_id": "Dublin", "Server": "localhost:8080", "Connections": [{"City":"Cork", "Time":"2", "Bandwidth":"100"}, {"City":"Belfast", "Time":"3", "Bandwidth":"100"} ]},
                {"_id": "Cork", "Server": "localhost:8081", "Connections": [ {"City":"Dublin", "Time":"2", "Bandwidth":"100"}, {"City":"Limerick", "Time":"1", "Bandwidth":"10"} ]},
                {"_id": "Limerick", "Server": "localhost:8080", "Connections": [{"City":"Belfast", "Time":"2", "Bandwidth":"100"}, {"City":"Cork", "Time":"1", "Bandwidth":"10"} ]},
                {"_id": "Belfast", "Server": "localhost:8081", "Connections": [{"City":"Dublin", "Time":"2", "Bandwidth":"100"}, {"City":"Limerick", "Time":"1", "Bandwidth":"10"} ]}]'''

class Util:
    def __init__(self, i):
        self.file = "transaction_logs_" + str(i) + ".txt"
        self.DistanceMap = None
        self.CapacityMap = None
        self.Cities = None
        self.CitiesToServers = None
        self.MapLatest = None
        self.OwnCities = []
        self.port = None

    def find_shortest_path(self, src, dest):
        # does not need to be recalculated for all

        src = self.Cities.inverse[src]
        dest = self.Cities.inverse[dest]
        a, pr = shortest_path(self.DistanceMap, directed=False, return_predecessors=True)
        path = [dest]
        k = dest
        while pr[src, k] != -9999:
            path.append(pr[src, k])
            k = pr[src, k]
        if path[-1] == src:
            path = path[::-1]
            res = [(self.Cities[path[0]], self.Cities[path[1]], a[path[0], path[1]])]
            for i in range(len(path)-2):
                res.append((self.Cities[path[i+1]], self.Cities[path[i+2]], res[-1][2] + a[path[i+1], path[i+2]]))
            return res
        else:
            return np.zeros(1, int)

    def parse_map_cities_servers(self, map):
        if map is None:
            map_json = json.loads(dummyMapList)
        else:
            map_json = [json.loads(doc) for doc in map]

        cityIndex = bidict({})
        cityToServerIndex = {}

        i = 0
        for m  in map_json:
            cityIndex[i] = m['name']
            cityToServerIndex[m["name"]] = m["server"]
            i+=1

        distanceMatrix = sparse.csr_matrix(np.zeros((len(cityIndex), len(cityIndex))))
        capacityMatrix = sparse.csr_matrix(np.zeros((len(cityIndex), len(cityIndex))))

        for m in map_json:
            currentIndex = cityIndex.inverse[m["name"]]
            connections = m["connections"]
            for connection in connections:
                targetIndex = cityIndex.inverse[connection["name"]]
                distanceMatrix[currentIndex, targetIndex] = connection["time"]
                capacityMatrix[currentIndex, targetIndex] = connection["bandwidth"]
        # todo: replace datetime now with fetched 'last updated at'
        self.DistanceMap = distanceMatrix
        self.CapacityMap = capacityMatrix
        self.Cities = cityIndex
        self.CitiesToServers = cityToServerIndex
        OwnCities = []
        for cit in self.CitiesToServers:
            if str.split(self.CitiesToServers[cit], ':')[1] == str(self.port):
                OwnCities.append(cit)
        # todo: replace datetime now with fetched 'last updated at'
        self.MapLatest = datetime.datetime.now()
        self.OwnCities = OwnCities

        return distanceMatrix, capacityMatrix, cityIndex, cityToServerIndex, datetime.datetime.now(), OwnCities

    def find_db_bookings(self):
        # list of bookings at a server
        # todo implementation
        raise NotImplemented

    def find_cities(self):
        # find available cities, indices in distance matrix, servers responsible
        # todo implementation
        raise NotImplemented

    def valid_trip(self, uid, time):
        # check no journey booked at time
        # todo implementation
        return True

    def find_db_journey(self, jid):
        # list servers responsible
        # todo implementation
        return [1, 1]

    def try_book(self, src, dest, uid, jid, time):
        # book if allowed return 0, if invalid return 1, if denied return 2
        # todo implementation
        if not self.valid_trip(uid, time):
            return 1
        return 0

    def book_transaction(self, jid, trips, transaction_status, db):
        mapp = db.get_map()
        self.parse_map_cities_servers(mapp)
        if trips is not None:
            for trip in trips:
                if trip["From"] not in self.OwnCities:
                    return {'message': 'City moved'}, 400

        # no need for follower log file, but it helps when restarting if leader logged commit but new booking request
        # comes in before leader retransmit
        TransLogFile = self.file
        log = dict()
        log["Leader"] = False
        log["JID"] = jid
        log["Type"] = "book"
        log["Trips"] = trips
        log["Status"] = "prepared"
        if transaction_status == "prepared":
            print("prepared state")
            # todo actually check for timeouts
            timeout_start = time.perf_counter()
            for trip in trips:
                db.trip_r_acquire(jid)
                # todo check if links at capacity
                load = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])["Capacity"]
                # # after or: Jid was used before, retry transaction
                # if jid not in db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])["JID"]:
                #     db.trip_r_release(jid)
                #     log["Status"] = "abort"
                #     if path.isfile(TransLogFile):
                #         with open(TransLogFile, "a") as fp:
                #             fp.write(',\n' + json.dumps(log))
                #     else:
                #         with open(TransLogFile, "w") as fp:
                #             fp.write(json.dumps(log))
                #     return {'message': 'Retry'}, 400
                if load >= self.CapacityMap[self.Cities.inverse[trip["From"]], self.Cities.inverse[trip["To"]]]:
                    print("load is higher")
                    db.trip_r_release(jid)
                    log["Status"] = "abort"
                    if path.isfile(TransLogFile):
                        with open(TransLogFile, "a") as fp:
                            fp.write(',\n' + json.dumps(log))
                    else:
                        with open(TransLogFile, "w") as fp:
                            fp.write(json.dumps(log))
                    return {'message': 'Link at capacity'}, 400


            # print("write lock")
            # # TODO: check write lock
            # db.trip_w_acquire(jid)
            # print("write lock II")


            load = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])["Capacity"]
            if load >= self.CapacityMap[self.Cities.inverse[trip["From"]], self.Cities.inverse[trip["To"]]]:
                db.trip_w_release(jid)
                log["Status"] = "abort"
                if path.isfile(TransLogFile):
                    with open(TransLogFile, "a") as fp:
                        fp.write(',\n' + json.dumps(log))
                else:
                    with open(TransLogFile, "w") as fp:
                        fp.write(json.dumps(log))
                return {'message': 'Link at capacity'}, 400

            log["Status"] = "commit"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200

        elif transaction_status == "commit":
            print("getTripsByLinkAndTime id = 0")
            exsitingTrips = db.getTripsByLinkAndTime(trips[0]["From"], trips[0]["To"], trips[0]["At"])
            print(jid)
            print(exsitingTrips)
            if jid not in exsitingTrips["JID"]:
                cou = 0
                for trip in trips:
                    print("counter="+str(cou))
                    print(trip)
                    trp = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])
                    update=False
                    if trp["Capacity"] !=0:
                        update = True

                    trp["Capacity"] = trp["Capacity"] + 1


                    trp["From"]=trip["From"]
                    trp["To"] = trip["To"]
                    trp["At"] = trip["At"]
                    print("trp:")
                    print(trp)
                    if update:
                        trp["JID"] =jid
                        db.updateTrip(trp)
                    else:
                        trp["JID"] =[jid]
                        db.addTrip(trp)

            db.trip_w_release(jid)
            log["Status"] = "complete"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200

        elif transaction_status == "abort":
            db.trip_w_release(jid)
            log["Status"] = "abort"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200
        else:
            return {'message': 'transaction_status should be one of prepared, commit or abort'}, 400

    def try_delete(self, uid, jid):
        # delete whole journey if deleted return 0, if no journey with id = jid return 1, if denied return 2
        # todo implementation
        trips = self.find_db_journey(jid)
        if not trips:
            return 1
        #using trips do delete transaction
        success = True
        if success:
            return 0
        else:
            return 2

    def cancel_transaction(self, jid, trips, transaction_status, db):
        mapp = db.get_map()
        self.parse_map_cities_servers(mapp)
        if trips is not None:
            for trip in trips:
                if trip["From"] not in self.OwnCities:
                    return {'message': 'City moved'}, 400

        # no need for follower log file, but it helps when restarting if leader logged commit but new booking request
        # comes in before leader retransmit
        TransLogFile = self.file
        log = dict()
        log["Leader"] = False
        log["JID"] = jid
        log["Type"] = "Cancel"
        log["Trips"] = trips
        log["Status"] = "prepared"
        if transaction_status == "prepared":
            print("prepared state")
            # todo actually check for timeouts
            timeout_start = time.perf_counter()
            for trip in trips:
                db.trip_r_acquire(jid)
                load = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])["Capacity"]
                if 0 >= self.CapacityMap[self.Cities.inverse[trip["From"]], self.Cities.inverse[trip["To"]]] - load:
                    db.trip_r_release(jid)
                    log["Status"] = "abort"
                    if path.isfile(TransLogFile):
                        with open(TransLogFile, "a") as fp:
                            fp.write(',\n' + json.dumps(log))
                    else:
                        with open(TransLogFile, "w") as fp:
                            fp.write(json.dumps(log))
                    return {'message': 'capacity cannot be less than zero'}, 400

            # print("write lock")
            # # TODO: check write lock
            # db.trip_w_acquire(jid)
            # print("write lock II")

            load = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])["Capacity"]
            if 0 >= self.CapacityMap[self.self.inverse[trip["From"]], self.Cities.inverse[trip[1]]] - load:
                db.trip_w_release(jid)
                log["Status"] = "abort"
                if path.isfile(TransLogFile):
                    with open(TransLogFile, "a") as fp:
                        fp.write(',\n' + json.dumps(log))
                else:
                    with open(TransLogFile, "w") as fp:
                        fp.write(json.dumps(log))
                return {'message': 'capacity cannot be less than zero'}, 400

            log["Status"] = "commit"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200

        elif transaction_status == "commit":
            print("getTripsByLinkAndTime id = 0")
            exsitingTrips = db.getTripsByLinkAndTime(trips[0]["From"], trips[0]["To"], trips[0]["At"])
            print(jid)
            print(exsitingTrips)
            if jid in exsitingTrips["JID"]:
                cou = 0
                for trip in trips:
                    print("counter=" + str(cou))
                    print(trip)
                    trp = db.getTripsByLinkAndTime(trip["From"], trip["To"], trip["At"])
                    trp["Capacity"] = trp["Capacity"] - 1
                    trp["JID"] = trp["JID"].remove(jid)
                    DB.deleteTrip(trp)
            db.trip_w_release(jid)
            log["Status"] = "complete"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200

        elif transaction_status == "abort":
            db.trip_w_release(jid)
            log["Status"] = "abort"
            if path.isfile(TransLogFile):
                with open(TransLogFile, "a") as fp:
                    fp.write(',\n' + json.dumps(log))
            else:
                with open(TransLogFile, "w") as fp:
                    fp.write(json.dumps(log))
            return {'message': 'Ok'}, 200
        else:
            return {'message': 'transaction_status should be one of prepared, commit or abort'}, 400


    def leader_transaction_message(self, trips, start_time, jid, type, status):
        resps = []
        if isinstance(start_time, str):
            start_time = datetimeparser.parse(start_time, fuzzy_with_tokens=True)
        for city in trips:
            trip_start_time = start_time
            delta = datetime.timedelta(hours=city[3])
            trip_start_time = trip_start_time[0] + delta
            data = dict()
            data["JID"] = jid
            data["Type"] = type
            data["Status"] = status
            # todo do all trips in 1 request where server is same
            data["Trips"] = json.dumps([
                {"From": city[1], "To": city[2], "At": trip_start_time.strftime("%m/%d/%Y, %H:%M:%S")}])
            # todo start requests async
            res = requests.post("http://" + city[0] + "/transaction", data=data, json=json.dumps(data), timeout=20)
            resps.append((city[0], city[1], city[2], city[3], res))
        return resps

    def round_to_timeslot(self, time):
        time.second = 0
        if time.minute == 30 or time.minute == 00:
            return time
        if time.minute > 30:
            time.minute = 30
            return time
        if time.minute < 30:
            time.minute = 0
            return time

    # return a list of trips in dictionaries format
    def dictionary_trips(self, jid, start_time,trips):
        resps = []
        if isinstance(start_time, str):
            start_time = datetimeparser.parse(start_time, fuzzy_with_tokens=True)
        for city in trips:
            trip_start_time = start_time
            delta = datetime.timedelta(hours=city[3])
            trip_start_time = trip_start_time[0] + delta
            data = {"From": city[1], "To": city[2], "At": trip_start_time.strftime("%m/%d/%Y, %H:%M:%S")}
            resps.append(data)
        return resps
