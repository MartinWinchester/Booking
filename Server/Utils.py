from scipy.sparse.csgraph import shortest_path
import numpy as np


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
