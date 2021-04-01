import numpy as np
import json
import os
import sys, pymongo

def readCommand( argv ):
	import argparse
	parser = argparse.ArgumentParser(description="your script description")

	parser.add_argument('-i','--init',dest='initPath',metavar=('INIT_DIR',' MAP_NAME'),
		help="Initilize map",type=str,nargs=2)
	parser.add_argument('-a','--add',dest='nodeFile',help='Add new node to map from file',
		metavar=('NODE_FILE',' MAP_NAME'),type=str,nargs=2)
	parser.add_argument("-d",'--delete',help="delete node from map",type=str)
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
		initilizeMap(nodes,mapName)
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

def initilizeMap(nodes,mapName):
	mongo_client = pymongo.MongoClient('127.0.0.1', 27017)
	if "map" not in mongo_client.list_database_names():
		print("Database not exist")
	mydb = mongo_client['map']
	mongo_collection = mydb[mapName]
	mongo_collection.delete_many({})
	mongo_collection.insert_many(nodes)


if __name__ == '__main__':
	args = readCommand( sys.argv[1:] ) # Get game components based on input



