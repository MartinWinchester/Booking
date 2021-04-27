## mongodb replica set up 

-> Create folders /config, /log, /data 
-> Edit config/rs{N}

dbpath=/data/rs{N}        
logpath=log/rs1.log   
journal=true                                             
port=2700{N}                                               
replSet=rs                                               
logappend=true                                           
fork = true  

-> create instances by running 
mongod --config {CONFIG_PATH}

-> Enter into one of the instance 
mongo -port 27001
rs.initiate()
-> add  nodes
rs.add("localhost:27002")
rs.add("localhost:27003")
-> set priority 
cfg = rs.conf()
cfg.members[0].priority = 2
cfg.members[1].priority = 1
cfg.members[2].priority = 1   
rs.reconfig(cfg)
-> set the other nodes
mongo -port 27002
rs.secondaryOk()
rs.status()



## set r/w priority
-> prefer to read from seconday
db.setReadPreference(ReadPreference.secondaryPreferred());
-> only read from secondary
db.setReadPreference(ReadPreference.secondary());



## test if data is replicated
PRIMARY
use test
db.createCollection('user')
db.user.insert({'name':'james'})

SECONDARY
use test
show collections
db.user.find()

## monitor node failure
mongod -f /config/rs1.conf --shutdown 

## check replica status
-> check oplog 
rs.printReplicationInfo()
-> check synchronization status
rs.printSlaveReplciationInfo()
