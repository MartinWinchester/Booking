from flask import Flask, jsonify, json
from flask_restful import Api, Resource, reqparse
import Utils
import uuid
import argparse
import DataBase
from datetime import datetime

app = Flask(__name__)
api = Api(app)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-s", "--server", default="localhost:8080")
arg_parser.add_argument("-db", "--database", default="localhost:27020")
arg_parser.add_argument("-gdb", "--globaldb", default="localhost:27019")
arg_parser.add_argument("-i", "--serverid", default="0")
args = arg_parser.parse_args()

OwnUrl = args.server
DbUrl = args.database
MapUrl = args.globaldb
ServerId = int(args.serverid)
PortBaseServer = 8080
PortBaseDb = 27020
PortServer = PortBaseServer + ServerId
PortDb = PortBaseDb + ServerId
TransLogFile = "../TransactionLogs/transaction_logs_" + str(ServerId) + ".txt"

DistanceMap, CapacityMap, Cities, CitiesToServers, MapLatest = Utils.parse_map_cities_servers(MapUrl)
OurCities = []


class Book(Resource):
    def get(self):
        # fetch users bookings
        parser = reqparse.RequestParser()
        parser.add_argument('UID', required=True)
        args = parser.parse_args()
        # find all bookings for given UID
        uid = args['UID']
        db = DataBase()
        result = json.dumps(db.getByUUID(uid))
        return result, 200


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Source', required=True)
        parser.add_argument('Destination', required=True)
        # user ID
        parser.add_argument('UID', required=True)
        # time of departure
        parser.add_argument('At', required=True)
        args = parser.parse_args()

        jid = uuid.uuid5()
        # todo: successful result should probably have arrival time, trips in journey, JID
        result = Utils.try_book(args['Source'], args['Destination'], args['UID'], jid, args['At'],)

        if result == 0:
            return {'message': "Journey booked successfully."}, 201
        if result == 1:
            return {'message': "Bad request."}, 409
        if result == 2:
            return {'message': "Journey denied."}, 503

    def delete(self):
        parser = reqparse.RequestParser()
        # user ID
        parser.add_argument('UID', required=True)
        # journey ID
        parser.add_argument('JID', required=True)
        args = parser.parse_args()

        result = Utils.try_delete(args['UID'], args['JID'])

        if result == 0:
            return {'message': 'Journey deleted successfully.'}, 204
        if result == 1:
            return {'message': 'Journey not found.'}, 404
        if result == 2:
            return {'message': "Operation failed. Try again."}, 503


api.add_resource(Book, '/book')

if __name__ == '__main__':
    for city in CitiesToServers:
        if str.split(CitiesToServers[city], ':')[1] == str(PortServer):
            OurCities.append(city)

    # if OurCities:
        # todo: recover transactions
        # todo: recover own database

    app.run(host=str.split(args.server, ':')[0], port=str.split(args.server, ':')[1])