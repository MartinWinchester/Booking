#!/usr/bin/env bash
rm -rf TripDB$1 && mkdir TripDB$1 && cd TripDB$1
mkdir data conf log
cd data && mkdir rs1 rs2 rs3 && cd ..
cd conf && mkdir rs1 rs2 rs3 &&touch rs1/rs1.cfg rs2/rs2.cfg rs3/rs3.cfg && cd ..
cd log && touch rs1.log rs2.log rs3.log && cd ..

if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "logpath=$(pwd)/log/rs1.log
	dbpath = $(pwd)/data/rs1  
	journal=true                                             
	port=2702$1                                               
	replSet=rs                                               
	logappend=true                                           
	fork = true " > conf/rs1/rs1.cfg

	echo "logpath=$(pwd)/log/rs2.log
	dbpath=$(pwd)/data/rs2 
	journal=true                                             
	port=2703$1                                               
	replSet=rs                           
	logappend=true                                           
	fork = true " > conf/rs2/rs2.cfg

	echo "logpath=$(pwd)/log/rs3.log
	dbpath=$(pwd)/data/rs3  
	journal=true                                             
	port=2704$1                                              
	replSet=rs                                               
	logappend=true                                           
	fork = true " > conf/rs3/rs3.cfg

	mongod -f conf/rs1/rs1.cfg &&
	mongod -f conf/rs2/rs2.cfg &&
	mongod -f conf/rs3/rs3.cfg
	mongo -port 2702$1 << EOF
	rs.initiate( {
	   _id : "rs",
	   members: [
		  { _id: 0, host: "127.0.0.1:2702$1" },
		  { _id: 1, host: "127.0.0.1:2703$1" },
		  { _id: 2, host: "127.0.0.1:2704$1" }
	   ]
	})
EOF

	mongo -port 2703$1 <<EOF
	rs.secondaryOk()
	quit()
EOF

	mongo -port 2704$1 <<EOF
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
	port=2702$1                                               
	replSet=rs                                               
	logappend=true" > conf/rs1/rs1.cfg

	echo "logpath=$base/log/rs2.log
	dbpath=$base/data/rs2 
	journal=true                                             
	port=2703$1                                               
	replSet=rs                           
	logappend=true" > conf/rs2/rs2.cfg

	echo "logpath=$base/log/rs3.log
	dbpath=$base/data/rs3  
	journal=true                                             
	port=2704$1                                              
	replSet=rs                                               
	logappend=true" > conf/rs3/rs3.cfg

	start mongod -f conf/rs1/rs1.cfg
	mongo -port 2702$1 & << EOF
	rs.initiate( {
	   _id : "rs",
	   members: [
		  { _id: 0, host: "127.0.0.1:2702$1" },
		  { _id: 1, host: "127.0.0.1:2703$1" },
		  { _id: 2, host: "127.0.0.1:2704$1" }
	   ]
	})
EOF

	start mongod -f conf/rs2/rs2.cfg 
	mongo -port 273$1 & <<EOF
	rs.secondaryOk()
	quit()
EOF

	start mongod -f conf/rs3/rs3.cfg
	mongo -port 2704$1 & <<EOF
	rs.secondaryOk()
	quit()
EOF
fi
cd ..