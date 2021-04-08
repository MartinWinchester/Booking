import json
import os
from pymongo import MongoClient
import datetime




jfile = open('secrets.json')

data = json.load(jfile)

user_nm = data["db_user"]
user_psswrd = data["db_pass"]

client = MongoClient("mongodb+srv://" + user_nm + ":" + user_psswrd + "@cluster0.gqnq7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# This command creates a new database on your cluster called gettingStarted. The variable db points to your new database.
db = client.gettingStarted

# This command creates a new collection in your gettingStarted database called people. The variable people points to your new collection.
people = db.people

print(people)