from scipy import sparse
from scipy.sparse.csgraph import shortest_path
from flask import json
import numpy as np
from bidict import bidict
from datetime import datetime

dummyMapList = '''[{"_id": "Dublin", "Server": "URL:0", "Connections": [{"City":"Cork", "Time":"2", "Bandwidth":"100"}, {"City":"Belfast", "Time":"3", "Bandwidth":"100"} ]},
                {"_id": "Cork", "Server": "URL:1", "Connections": [ {"City":"Dublin", "Time":"2", "Bandwidth":"100"}, {"City":"Limerick", "Time":"1", "Bandwidth":"10"} ]},
                {"_id": "Limerick", "Server": "URL:2", "Connections": [{"City":"Belfast", "Time":"2", "Bandwidth":"100"}, {"City":"Cork", "Time":"1", "Bandwidth":"10"} ]},
                {"_id": "Belfast", "Server": "URL:3", "Connections": [{"City":"Dublin", "Time":"2", "Bandwidth":"100"}, {"City":"Limerick", "Time":"1", "Bandwidth":"10"} ]}]'''


def find_shortest_path(src, dest, source="Dummy"):
    map = fetch_distance_matrix(source)
    # does not need to be recalculated for all
    _, pr = shortest_path(map, directed=False, return_predecessors=True)
    path = [dest]
    k = dest
    while pr[src, k] != -9999:
        path.append(pr[src, k])
        k = pr[src, k]
    if path[-1] == src:
        return path[::-1]
    else:
        return np.zeros(1, int)


def parse_map_cities_servers(mapUrl):
    # todo: replace next line with fetch request from real DB
    map_json = json.loads(dummyMapList)
    cityIndex = bidict({})
    cityToServerIndex = {}
    for i in range(len(map_json)):
        cityIndex[i] = map_json[i]["_id"]
        cityToServerIndex[map_json[i]["_id"]] = map_json[i]["Server"]
    distanceMatrix = sparse.csr_matrix(np.zeros((len(cityIndex), len(cityIndex))))
    capacityMatrix = sparse.csr_matrix(np.zeros((len(cityIndex), len(cityIndex))))
    for i in range(len(map_json)):
        currentIndex = cityIndex.inverse[map_json[i]["_id"]]
        connections = map_json[i]["Connections"]
        for connection in connections:
            targetIndex = cityIndex.inverse[connection["City"]]
            distanceMatrix[currentIndex, targetIndex] = connection["Time"]
            capacityMatrix[currentIndex, targetIndex] = connection["Bandwidth"]
    # todo: replace datetime now with fetched 'last updated at'
    return distanceMatrix, capacityMatrix, cityIndex, cityToServerIndex, datetime.now()


def fetch_distance_matrix(source):
    if source == "Dummy":
        return np.array([[1, 1, 0],
                         [1, 1, 1],
                         [0, 1, 1]])
    raise NotImplemented


def find_db_bookings():
    # list of bookings at a server
    # todo implementation
    raise NotImplemented


def find_cities():
    # find available cities, indices in distance matrix, servers responsible
    # todo implementation
    raise NotImplemented


def valid_trip(uid, time):
    # check no journey booked at time
    # todo implementation
    return True


def find_db_journey(jid):
    # list servers responsible
    # todo implementation
    return [1, 1]


def try_book(src, dest, uid, jid, time):
    # book if allowed return 0, if invalid return 1, if denied return 2
    # todo implementation
    if ~valid_trip(uid, time):
        return 1
    return 0


def try_delete(uid, jid):
    # delete whole journey if deleted return 0, if no journey with id = jid return 1, if denied return 2
    # todo implementation
    trips = find_db_journey(jid)
    if not trips:
        return 1
    #using trips do delete transaction
    success = True
    if success:
        return 0
    else:
        return 2
