# World Map
Drivers need to book journeys in a network of nodes and connections (cities and roads). This ReadMe discusses the construction of this network and how to use the various functions available.

## Choosing a database
There are 2 versions of MongoDB that you can use. Either MongoDB atlas or MongoDB as a local database. Using one or the other is fairly simple, as there are 2 functions: mongo_client_online() and mongo_client_local() that distinguish between the 2.  Connecting to MongoDB atlas requires user and password, whereas the local version requires the port to connect to.


## Creating the Map
There are 2 scenarios when creating the map:
* Creating the map from scratch with no nodes available
* Expanding the map with new cities and roads


When you want to create a simple map from scratch, this can be done using JSON files. MongoDB uses documents, so the entire JSON files are added to the database.
-- add command here --

Should you want to expand this map, there's a function called addToMap that can be used! Currently this cannot be run from command line.
