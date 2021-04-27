# Setup Sharding

Router (mongos) 2+
Config Server 3+
Shard (replica set) 

mongo1(127.0.0.1) mongo2(127.0.0.1) mongo3(127.0.0.1)

config1(port: 27018) 
config2(port: 27028) 
config3(port: 27038)

mongos1(port: 27019) 
mongos2(port: 27029) 
mongos3(port: 27039)

Shard1(port: 27001) 
Shard1(port: 27021) 
Shard1(port: 27031)

Shard2(port: 27002) 
Shard2(port: 27022) 
Shard2(port: 27032)

Shard3(port: 27003) 
Shard3(port: 27023) 
Shard3(port: 27033)

## set up file structure

change the dbpath and logpath to corresponding file path

if using Windows, comment fork option

## start config servers
mongod -f <config1_path> &&
mongod -f <config2_path> &&
mongod -f <config3_path>

-> new terminal window
-> connect to one of the config server
`mongo -port 27018`
`config = {   
	_id : "configs",    
	configsvr: true, 
    members : [         
        {_id : 0, host : "127.0.0.1:27018" },         
        {_id : 1, host : "127.0.0.1:27028" },         
        {_id : 2, host : "127.0.0.1:27038" }     
    ]  }`
`rs.initiate(config)`

## start sharding clusters

-> start sharding cluster
mongod -f <shard1_node1_path> &&
mongod -f <shard1_node2_path> &&
mongod -f <shard1_node3_path>
mongo --port 27011
`
rs.initiate(config = { _id : "shard1",members : [
{_id : 0, host : "127.0.0.1:27011"},
{_id : 1, host : "127.0.0.1:27021"},
{_id : 2, host : "127.0.0.1:27031"}
]});`


mongod -f <shard2_node1_path> &&
mongod -f <shard2_node2_path> &&
mongod -f <shard2_node3_path>
mongo -port 27012
`
rs.initiate({ _id : "shard2",members : [
{_id : 0, host : "127.0.0.1:27012"},
{_id : 1, host : "127.0.0.1:27022"},
{_id : 2, host : "127.0.0.1:27032"}
]})`


mongod -f <shard3_node1_path> &&
mongod -f <shard3_node2_path> &&
mongod -f <shard3_node3_path>
mongo --port 27013
`rs.initiate({ _id : "shard3",members : [
{_id : 0, host : "127.0.0.1:27013"},
{_id : 1, host : "127.0.0.1:27023"},
{_id : 2, host : "127.0.0.1:27033"}
]});`



## shart router mongos1 mongos2 mongos3
mongos -f <mongos1_path> --fork &&
mongos -f <mongos2_path> --fork &&
mongos -f <mongos3_path> --fork 
mongo --port 27019


```
use admin;
sh.addShard("shard1/127.0.0.1:27011,127.0.0.1:27021,127.0.0.1:27031");
sh.addShard("shard2/127.0.0.1:27012,127.0.0.1:27022,127.0.0.1:27032");
sh.addShard("shard3/127.0.0.1:27013,127.0.0.1:27023,127.0.0.1:27033");
```










