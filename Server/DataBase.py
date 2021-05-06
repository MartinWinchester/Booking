import json
import os
import sys
import pymongo
from pymongo import MongoClient
import datetime
import argparse
from bson import json_util
import time
from readerwriterlock import rwlock

class DB:
	# todo AddJourney, GetTripsByUUID
	# todo add func to check if DB available and if not replace with a replica, check before all operations
	# todo add func to get LastUpdatedAt timestamp
	def __init__(self, trip_host, trip_port, journey_host, journey_port, map_host, map_port,trip_alts=None, journey_alts=None,map_alts=None):
		# host: string, port: int
		# alts: list of forwarding info to replicas
		self.trip_alts = trip_alts
		self.journey_alts = journey_alts
		self.trip_lock_r = None
		self.trip_lock_w = None
		self.trips_client = MongoClient(trip_host, trip_port)
		self.journeys_client = MongoClient(journey_host, journey_port)
		self.map_client = MongoClient(map_host, map_port)

	def addTrip(self, trip):
		mongo_collection = self.trips_client['Trips']['Trips']
		mongo_collection.insert_many(trip)

	def deleteJourney(self, uid ,jid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		mongo_collection.update_one({'UUID': uid}, {'$pull': {'Journeys': {'JourneyID': jid}}})

	def addJourney(self, uid ,journey):
		mongo_collection = self.journeys_client['Journey']['Journey']
		updated = mongo_collection.update_one({'UUID': uid}, {'$push': {'Journeys': journey}})
		if updated.matched_count == 0:
			data = {"UUID":uid,"Journeys":[journey]}
			mongo_collection.insert_one(data)


	def getByJourneyID(self, jid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		trips = mongo_collection.find({'JourneyID': jid})
		json_docs = []
		for trip in trips:
			json_doc = json.dumps(trip, default=json_util.default)
			json_docs.append(json_doc)
		return json_docs

	def getByUUID(self, uid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		trips = mongo_collection.find({'UUID': uid})
		json_docs = []
		for trip in trips:
			json_doc = json.dumps(trip, default=json_util.default)
			json_docs.append(json_doc)
		return json_docs

	def getTripsByLinkAndTime(self, source, destination, time):
		mongo_collection = self.trips_client['Trips']['Trips']
		trips = mongo_collection.find({"$and": [{"Source": source}, {"Destination":destination}, {"Leave at": time}]})
		json_docs = []
		for trip in trips:
			json_doc = json.dumps(trip, default=json_util.default)
			json_docs.append(json_doc)
		return json_docs

	def trip_r_acquire(self, jid):
		while 1:
			try:
				if jid in self.trip_lock_r:
					return
			except:
				print()
			if self.trip_lock_w is None:
				if self.trip_lock_r is None:
					self.trip_lock_r = [jid]
				else:
					self.trip_lock_r.append(jid)
				return
			time.sleep(1)

	def trip_w_acquire(self, jid):
		while 1:
			if self.trip_lock_w == jid:
				return 1
			if self.trip_lock_w is None and self.trip_lock_r is None:
				self.trip_lock_w = jid
				return 0
			time.sleep(1)

	def trip_r_release(self, jid):
		try:
			self.trip_lock_r.remove(jid)
		except:
			return

	def trip_w_release(self, jid):
		if self.trip_lock_w == jid:
			self.trip_lock_w = None
		try:
			self.trip_lock_r.remove(jid)
			return 0
		except:
			return 1



	def get_map(self):
		mongo_client = self.map_client
		# This command creates a new database.
		db = mongo_client.Map
		# This command creates a new collection in your database called Cities.
		cities_collection = db.Cities
		data = cities_collection.find()
		json_docs = [json.dumps(doc, default=json_util.default) for doc in data]
		return json_docs
