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
	# todo AddJourney, GetTripsByUID
	# todo add func to check if DB available and if not replace with a replica, check before all operations
	# todo add func to get LastUpdatedAt timestamp
	def __init__(self, trip_host, trip_port, journey_host, journey_port, map_host, map_port,trip_alts=None, journey_alts=None,map_alts=None):
		# host: string, port: int
		# alts: list of forwarding info to replicas
		self.trip_alts = trip_alts
		self.journey_alts = journey_alts
		self.trip_lock_r = None
		self.trip_lock_w = None
		# self.trips_client = MongoClient()
		# self.trips_client = MongoClient(trip_host, trip_port)
		self.journeys_client = MongoClient(journey_host, journey_port)
		# self.map_client = MongoClient(map_host, map_port)
		self.trips_client = MongoClient("localhost:27030", replicaSet="trip0")
		# self.journeys_client = MongoClient("localhost:27119")
		self.map_client = MongoClient("localhost:27001", replicaSet="rs")

	def addTrip(self, trip):
		mongo_collection = self.trips_client['Trips']['Trips']
		mongo_collection.insert_one(trip)

	def updateTrip(self, trip):
		print("UPDATEING TRIP😐!!!!!!!!!")
		print(trip)
		mongo_collection = self.trips_client['Trips']['Trips']
		dbfilter = {"$and": [{"From": trip["From"]}, {"To":trip["To"]}, {"At": trip["At"]}]}
		mongo_collection.update_one(dbfilter,
			{'$push': {'JID': trip["JID"]}, '$set': {'Capacity': trip["Capacity"]}},upsert=True)


	def deleteJourney(self, uid ,jid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		mongo_collection.update_one({'UID': uid}, {'$pull': {'Journeys': {'JID': jid}}})

	def addJourney(self, uid ,journey):
		mongo_collection = self.journeys_client['Journey']['Journey']
		updated = mongo_collection.update_one({'UID': uid}, {'$push': {'Journeys': journey}})
		if updated.matched_count == 0:
			data = {"UID":uid,"Journeys":[journey]}
			mongo_collection.insert_one(data)


	def changeJourneyDatabase(self):
		if self.journey_database == 0:
			self.journeys_client = MongoClient(journey_alts[0])
			self.journey_database = 1
			return True
		if self.journey_database == 1:
			self.journeys_client = MongoClient(journey_alts[1])
			self.journey_database = 2
			return True
		return False


	def getByJourneyID(self, jid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		trips = mongo_collection.find({'JID': jid})
		json_docs = []
		for trip in trips:
			json_doc = json.dumps(trip, default=json_util.default)
			json_docs.append(json_doc)
		return json_docs

	def getByUID(self, uid):
		mongo_collection = self.journeys_client['Journey']['Journey']
		trips = mongo_collection.find({'UID': uid})
		json_docs = []
		for trip in trips:
			json_doc = json.dumps(trip, default=json_util.default)
			json_docs.append(json_doc)
		return json_docs

	def getTripsByLinkAndTime(self, From, To, time):
		mongo_collection = self.trips_client['Trips']['Trips']
		trips = mongo_collection.find_one({"$and": [{"From": From}, {"To":To}, {"At": time}]})
		# json_docs = []
		# for trip in trips:
		# 	json_doc = json.dumps(trip, default=json_util.default)
		# 	json_docs.append(json_doc)
		# return json_docs
		print("^^^^^^^^^getTripsByLinkAndTime^^^^^^^^^^^^")
		if not trips:
			print(0)
			return {"Capacity":0,"JID":[" "]}
		else:
			print(trips['Capacity'])
			return trips

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
