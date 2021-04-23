# Booking




## Set up sharding

* Router (mongos) 3+
* Config Server 3
* Shard (replica set) 3

For demo, run all the mongo instances on localhost

**port summary:**

config1(port: 27018) config2(port: 27028) config3(port: 27038)

mongos1(port: 27019) mongos2(port: 27029) mongos3(port: 27039)

Shard1(port: 27001) Shard1(port: 27021) Shard1(port: 27031)

Shard2(port: 27002) Shard2(port: 27022) Shard2(port: 27032)

Shard3(port: 27003) Shard3(port: 27023) Shard3(port: 27033)
