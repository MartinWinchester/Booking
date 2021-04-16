import json
import os
import sys, pymongo
from pymongo import MongoClient
import datetime
import argparse
from bson import json_util

client = pymongo.MongoClient('127.0.0.1', 27017)

def addTrip(trip):
	mongo_collection = client['Journey']['Trips']
	mongo_collection.insert_many(trip)

def getByJourneyID(id):
	mongo_collection = client['Journey']['Trips']
	trips = mongo_collection.find({'JourneyID': id})
	json_docs = []
	for trip in trips:
		json_doc = json.dumps(trip, default=json_util.default)
		json_docs.append(json_doc)
	return json_docs

def getByUUID(id):
	mongo_collection = client['Journey']['Trips']
	trips = mongo_collection.find({'UUID': id})
	json_docs = []
	for trip in trips:
		json_doc = json.dumps(trip, default=json_util.default)
		json_docs.append(json_doc)
	return json_docs

def getByCityAndTime(city,time):
	mongo_collection = client['Journey']['Trips']
	trips = mongo_collection.find({"$and": [{"Source": city}, {"Leave at": time}]})
	json_docs = []
	for trip in trips:
		json_doc = json.dumps(trip, default=json_util.default)
		json_docs.append(json_doc)
	return json_docs