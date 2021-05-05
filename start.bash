#!/usr/bin/env bash
echo "Starting Map DB (replica)"
cd SetupShardingAndReplica/replica/
./replica.bash
echo "Starting Journey DB (sharding)"
cd ../sharding
./shard.bash
cd ..
python ./Server/Server.py > server_logs.txt 2>&1
