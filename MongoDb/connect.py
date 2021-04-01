# just some sample code that connect to mongoDB atlas and creates a database with one collection and one entry.
from pymongo import MongoClient
import datetime

# TODO: Replace <user> with your username and <password> with your password
client = MongoClient("mongodb+srv://<user>:<password>@cluster0.gqnq7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# This command creates a new database on your cluster called gettingStarted. The variable db points to your new database.
db = client.gettingStarted

# This command creates a new collection in your gettingStarted database called people. The variable people points to your new collection.
people = db.people

personDocument = {
  "name": { "first": "Cata", "last": "Smith" },
  "birth": datetime.datetime(1912, 6, 23),
  "death": datetime.datetime(1954, 6, 7),
  "contribs": [ "Turing machine", "Turing test", "Turingery" ],
  "views": 1250000
}

print(people.insert_one(personDocument))
print(people.find_one({ "name.last": "Smith" }))
