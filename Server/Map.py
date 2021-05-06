import numpy as np
import json
import os
import sys, pymongo
import ast
sys.path.append('../Clients')
from bson import json_util
import json
from flask import Flask, jsonify, json
from flask_restful import Api, Resource, reqparse
from CityBuilderClient import expandMap


def parse_json(data):
    return json.loads(json_util.dumps(data))
# Put to initialize, Post to update and Get to list
# curl -X POST -d "UID=0" -d "City=Mayo" -d "Incoming=[(Galway, 10, 10)]"  -d "Outgoing=[(Galway, 50, 10)]" localhost:8080/map
# ALL parameters are strings! need to convert if I need something else
class Map(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        # This is the name of the database to be created
        parser.add_argument('DatabaseName', required=True)

        # This is the path to the json files used to add the base cities.
        parser.add_argument('NodesPath', required=True)

        # Host and Port of mongo_client to be used for this Database.
        parser.add_argument('Host', required=True)
        parser.add_argument('ReplicaSetName', required=True)

        args = parser.parse_args()

        files=[]
        path = args['NodesPath']
        for file in os.listdir(path):
            	files.append(os.path.join(path, file))
        nodes=[]

        for filename in files:
            if filename.endswith('.json'):
                with open(filename) as f:
                    data = json.load(f)
                    nodes.append(data)

        if nodes == []:
            return {'message': "Cannot find specified json files in the location specified."}, 404


        port = int(args['Port'])

        mongo_client = pymongo.MongoClient(args['Host'], port)
        # mongo_client = pymongo.MongoClient(args['Host'], replicaSet = args['ReplicaSetName'])

        # This command creates a new database.
        databaseName = args['DatabaseName']
        db = mongo_client[databaseName]
    	# This command creates a new collection in your database called Cities.
        cities_collection = db.Cities

    	# This deletes everything in the database because we initialize the map from scratch :)!
        cities_collection.delete_many({})
        cities_collection.insert_many(nodes)

        # Change this message based on a condition
        return {'message': "Database initialized successfully."}, 200

    def get(self):
        parser = reqparse.RequestParser()
        # This is the name of the database to be created
        parser.add_argument('DatabaseName', required=True)

        # Host and Port of mongo_client to be used for this Database.
        parser.add_argument('Host', required=True)
        parser.add_argument('Port', required=True)
        parser.add_argument('City', required = True)
        args = parser.parse_args()
        ## Port is an int! Convert the string to an int
        port = int(args['Port'])

        mongo_client = pymongo.MongoClient(args['Host'], port)

        # This command creates a new database.
        databaseName = args['DatabaseName']
        db = mongo_client[databaseName]
    	# This command creates a new collection in your database called Cities.
        cities_collection = db.Cities
        data = parse_json(cities_collection.find_one({ "name": args['City']}))
        return {'message': data}, 200

    def post(self):
        parser = reqparse.RequestParser()
        # This is the name of the database to be created
        parser.add_argument('DatabaseName', required=True)

        # Host and Port of mongo_client to be used for this Database.
        parser.add_argument('Host', required=True)
        parser.add_argument('Port', required=True)
        parser.add_argument('City', required = True)
        parser.add_argument('Server', required=True)
        parser.add_argument('Incoming', required = True)
        parser.add_argument('Outgoing', required=True)

        args = parser.parse_args()
        port = int(args['Port'])
        incoming = ast.literal_eval(args['Incoming'])
        outgoing = ast.literal_eval(args['Outgoing'])
        mongo_client = pymongo.MongoClient(args['Host'], port)
        expandMap(mongo_client, args['DatabaseName'] , args['City'], args['Server'],incoming,outgoing )
