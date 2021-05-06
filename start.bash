#!/usr/bin/env bash
echo "Starting Map DB (replica)"
cd SetupShardingAndReplica/replica/ && ./replica.bash && cd ../..
echo "Starting Journey DB (sharding)"
cd SetupShardingAndReplica/sharding && ./shard.bash && cd ../..

for i in {0..$1}
do
	echo "Starting Trip DB for server $i"
	./startTripDB.bash $i
	python ./Server/Server.py -s localhost:808$i -db localhost:2702$i -dbr 2 -gdb localhost:27119 -gdbr 2 -i $i > server_logs.txt 2>&1
done