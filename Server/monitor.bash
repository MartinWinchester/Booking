#!/bin/bash
while true; do
	health=$(curl -I localhost:8080/health | grep -c "200 OK")
	echo $health
	if [$health eq 1]
	then
		python Server.py -s localhost:8080 -db localhost:27020 -dbr 2 -gdb localhost:27119 -gdbr 2 -i 0
	fi
	health=$(curl -I localhost:8081/health | grep -c "200 OK")
	echo $health
	if [$health eq 1]
	then
		python Server.py -s localhost:8081 -db localhost:27021 -dbr 2 -gdb localhost:27119 -gdbr 2 -i 1
	fi
	health=$(curl -I localhost:8082/health | grep -c "200 OK")
	echo $health
	if [$health eq 1]
	then
		python Server.py -s localhost:8082 -db localhost:27022 -dbr 2 -gdb localhost:27119 -gdbr 2 -i 2
	fi
done
