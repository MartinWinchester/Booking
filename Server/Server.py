from flask import Flask, jsonify, json
from flask_restful import Api, Resource, reqparse
import Utils as util
import uuid
from datetime import datetime

app = Flask(__name__)
api = Api(app)


class Book(Resource):
    def get(self):
        # fetch users bookings
        parser = reqparse.RequestParser()
        parser.add_argument('UID', required=True)
        args = parser.parse_args()
        # find all bookings for given UID
        bookings = [
            {'JID': 0, 'Source': "0", 'Destination': "1", "From": datetime(2021, 1, 1, 12, 3), "To": datetime(2021, 1, 1, 13, 3)},
            {'JID': 1, 'Source': "1", 'Destination': "2", "From": datetime(2021, 1, 1, 13, 4), "To": datetime(2021, 1, 1, 14, 4)}]
        resp = json.dumps(bookings)
        return resp, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Source', required=True)
        parser.add_argument('Destination', required=True)
        # user ID
        parser.add_argument('UID', required=True)
        # journey ID
        parser.add_argument('JID', required=True)
        # time of departure
        parser.add_argument('At', required=True)
        args = parser.parse_args()

        # todo: successful result should probably have arrival time, trips in journey, JID
        result = util.try_book(args['Source'], args['Destination'], args['UID'], args['JID'], args['At'],)

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

        result = util.try_delete(args['UID'], args['JID'])

        if result == 0:
            return {'message': 'Journey deleted successfully.'}, 204
        if result == 1:
            return {'message': 'Journey not found.'}, 404
        if result == 2:
            return {'message': "Operation failed. Try again."}, 503

api.add_resource(Book, '/book')

if __name__ == '__main__':
    app.run()
