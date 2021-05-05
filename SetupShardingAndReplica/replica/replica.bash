#!/usr/bin/env bash
rm -rf data conf log
mkdir data conf log
cd data && mkdir rs1 rs2 rs3 && cd ..
cd conf && mkdir rs1 rs2 rs3 &&touch rs1/rs1.cfg rs2/rs2.cfg rs3/rs3.cfg && cd ..
cd log && touch rs1.log rs2.log rs3.log && cd ..


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

	start mongod -f conf/rs1/rs1.cfg
	mongo -port 27001 & << EOF
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

	start mongod -f conf/rs2/rs2.cfg 
	mongo -port 27002 & <<EOF
	rs.secondaryOk()
	quit()
EOF

	start mongod -f conf/rs3/rs3.cfg
	mongo -port 27003 & <<EOF
	rs.secondaryOk()
	quit()
EOF
fi