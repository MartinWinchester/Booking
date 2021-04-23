import numpy as np
import json
import os
import sys, pymongo
from pymongo import MongoClient

def mongo_client_online():
	return MongoClient("mongodb+srv://<user>:<password>@cluster0.gqnq7.mongodb.net/mapDatabase?retryWrites=true&w=majority")

def mongo_client_local():
 	return pymongo.MongoClient('127.0.0.1', 27017)

def readCommand( argv ):
	import argparse
	parser = argparse.ArgumentParser(description="your script description")

	parser.add_argument('-i','--init',dest='initPath',metavar=('INIT_DIR',' MAP_NAME'),
		help="Initilize map",type=str,nargs=2)
	parser.add_argument('-a','--add',dest='nodeFile',help='Add new node to map from file',
		metavar=('NODE_FILE',' MAP_NAME'),type=str,nargs=2)
	parser.add_argument("-d",'--delete',help="delete node from map",type=str)
	parser.add_argument("-on",'--online',help="Add entries to cluster that is on MongoDB atlas", default = False, type=bool)
	args = parser.parse_args()

	if args.initPath:
		path = args.initPath[0]
		mapName = args.initPath[1]
		files=[]
		for file in os.listdir(path):
			files.append(os.path.join(path, file))
		nodes=[]
		for filename in files:
			if filename.endswith('.json'):
				with open(filename) as f:
					data = json.load(f)
				nodes.append(data)
		if args.online == True:
			initializeMap_online(mongo_client_online(),mapName)
		else:
			initilizeMap(mongo_client_local(),nodes, mapName)

	if args.nodeFile:
		with open(args.nodeFile[0]) as f:
			data = json.load(f)
		addNode(data,args.nodeFile[1])
	if args.delete:
		print("delete a node")

def addNode(node,mapName):
	mongo_client = pymongo.MongoClient('127.0.0.1', 27017)
	mongo_collection = mongo_client['map'][mapName]
	mongo_collection.insert_one(node)

def initilizeMap(mongo_client,nodes,mapName):
	if "map" not in mongo_client.list_database_names():
		print("Database not exist")
	mydb = mongo_client['map']
	mongo_collection = mydb[mapName]
	mongo_collection.delete_many({})
	mongo_collection.insert_many(nodes)

# mongo_client to use, whether online or local
# nodes - cities to be added
# mapName - name of the database containing the mapName
def initializeMap(mongo_client, nodes, mapName):
	# This command creates a new database on your cluster called GlobalMap.
	db = mongo_client.Map
	# This command creates a new collection in your database called Cities.
	cities_collection = db.Cities

	# This deletes everything in the database because we initialize the map from scratch :)!
	cities_collection.delete_many({})
	cities_collection.insert_many(nodes)
	print(cities_collection.find_one({ "name": "Cork" }))


# Args:
# mongo_client to use, whether online or local
# city  - city that we want to add/modify connections too. e.g: Dublin
# server - server responsible for trips from this city. Server is overwritten if a new connection is added to an already existing city!
# incoming - list of incoming connections to this city. e.g Belfast-Dublin and their corresponding data. This is a map of tuples. map[Belfast] = (5,100), map[Limerick] = (6,100)
# outgoing -  list of outgoing connections from this city. e.g Dublin-Cork and their corresponding data. This is also a map of tuples. map[Cork] = (5,100)
# Warning: If Dublin - Limerick connection is added twice, it will be kept as duplicate.
# TODO(catalina): Add date time to another collection .
def addToMap(mongo_client, city, server, incoming, outgoing):
	# Modify outgoing connections first because it's easier.
	# check if city exists already
	# This command creates a new database on your cluster called GlobalMap.
	db = mongo_client.Map
	# This command creates a new collection in your database called Cities.
	cities_collection = db.Cities

	# Handle outgoing connections first.
	if outgoing:
		node = cities_collection.find_one({ "name": city })
		# This is a new city
		to_update = False
		if not node:
			object_outgoing = json_object(city,server, [], outgoing)
			print("new city")
		else:
			# server is overwritten!
			to_update = True
			# This is duplicating informatioN!!!
			object_outgoing = json_object(city, server, node["connections"], outgoing)

		if not to_update:
			cities_collection.insert_one(object_outgoing)
		else:
			cities_collection.update_one({ "name": city }, { "$set": object_outgoing  })

	# handle incoming connections
	if incoming:
		incoming_objects = []
		for key in incoming:
			node = cities_collection.find_one({ "name": key })
			# TODO: abort whole transaction if the incoming is incorrect
			if not node:
				object_incoming = json_object(key, server, [], {city:incoming[key]})
			else:
				object_incoming = json_object(key, node['server'], node["connections"], {city:incoming[key]})
				cities_collection.update_one({ "name": key }, { "$set": object_incoming  })


def json_object(city, server, existing, outcoming):
	objects = []
	for key in outcoming:
		object = {"name": key, "time": outcoming[key][0], "bandwidth": outcoming[key][1]}
		objects.append(object)

	existing.extend(objects)
	data_set = {"name": city, "server": server, "connections": existing}

	json_dump = json.dumps(data_set)
	print(json_dump)
	return json.loads(json_dump)

def callback(session):
	addToMap(mongo_client, "Cluj","URL:5",{"Limerick":(2,5)}, {})

mongo_client = mongo_client_online()

if __name__ == '__main__':
	#args = readCommand( sys.argv[1:] ) # Get game components based on input
	#"Cork":(2,5), "Dublin":(3,10)
	# Step 2: Start a client session.
	# At any given time, you can have at most one open transaction for a session.
	with mongo_client.start_session() as session:
	    # Step 3: Use with_transaction to start a transaction, execute the callback, and commit (or abort on error).
		session.with_transaction(callback)

	db = mongo_client.Map
	cities_collection = db.Cities
	node = cities_collection.find_one({ "name":"Sibiu" })
	print(node)
	node = cities_collection.find_one({ "name":"Limerick" })
	print(node)
