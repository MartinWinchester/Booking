#!/usr/bin/env bash
#rm -rf data conf log
mkdir data conf log
mkdir data/rs1 data/rs2 data/rs3
mkdir conf/rs1 conf/rs2 conf/rs3 &&touch conf/rs1/rs1.cfg conf/rs2/rs2.cfg conf/rs3/rs3.cfg
touch log/rs1.log log/rs2.log log/rs3.log


if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "logpath=$(pwd)/log/rs1.log
	dbpath = $(pwd)/data/rs1
	journal=true
	port=27001
	replSet=rs
	logappend=true
	fork = true " > conf/rs1/rs1.cfg

	echo "logpath=$(pwd)/log/rs2.log
	dbpath=$(pwd)/data/rs2
	journal=true
	port=27002
	replSet=rs
	logappend=true
	fork = true " > conf/rs2/rs2.cfg

	echo "logpath=$(pwd)/log/rs3.log
	dbpath=$(pwd)/data/rs3
	journal=true
	port=27003
	replSet=rs
	logappend=true
	fork = true " > conf/rs3/rs3.cfg

	mongod -f conf/rs1/rs1.cfg &&
	mongod -f conf/rs2/rs2.cfg &&
	mongod -f conf/rs3/rs3.cfg
	mongo -port 27001 << EOF
	rs.initiate( {
	   _id : "rs",
	   members: [
		  { _id: 0, host: "127.0.0.1:27001" },
		  { _id: 1, host: "127.0.0.1:27002" },
		  { _id: 2, host: "127.0.0.1:27003" }
	   ]
	})
	cfg = rs.conf()
	cfg.members[0].priority = 2
	cfg.members[1].priority = 1
	cfg.members[2].priority = 1
	rs.reconfig(cfg)
EOF

	mongo -port 27002 <<EOF
	rs.secondaryOk()
	quit()
EOF

	mongo -port 27003 <<EOF
	rs.secondaryOk()
	quit()
EOF
elif [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ]; then
	base="$(pwd)"
	echo "$base"
	base="${base:2}"
	echo "$base"

	echo "logpath=$base/log/rs1.log
dbpath=$base/data/rs1
journal=true
port=27001
replSet=rs
logappend=true" > conf/rs1/rs1.cfg

	echo "logpath=$base/log/rs2.log
dbpath=$base/data/rs2
journal=true
port=27002
replSet=rs
logappend=true" > conf/rs2/rs2.cfg

	echo "logpath=$base/log/rs3.log
dbpath=$base/data/rs3
journal=true
port=27003
replSet=rs
logappend=true" > conf/rs3/rs3.cfg

	cat conf/rs1/rs1.cfg
	start mongod -f conf/rs1/rs1.cfg
	start mongod -f conf/rs2/rs2.cfg
	start mongod -f conf/rs3/rs3.cfg
	ready=$(netstat -a | grep ":2700" | grep -c "LISTENING")
	echo $ready
	while [ $ready -lt 3 ]
	do
		ready=$(netstat -a | grep ":2700" | grep -c "LISTENING")
		echo $ready
	done

	mongo -port 27001 & << EOF
rs.initiate( {
   _id : "rs",
   members: [
	  { _id: 0, host: "localhost:27001" },
	  { _id: 1, host: "localhost:27002" },
	  { _id: 2, host: "localhost:27003" }
   ]
})
cfg = rs.conf()
cfg.members[0].priority = 2
cfg.members[1].priority = 1
cfg.members[2].priority = 1
rs.reconfig(cfg)
EOF

	mongo -port 27002 & <<EOF
rs.secondaryOk()
quit()
EOF

	mongo -port 27003 & <<EOF
rs.secondaryOk()
quit()
EOF
fi
