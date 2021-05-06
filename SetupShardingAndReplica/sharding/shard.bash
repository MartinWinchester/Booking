rm -rf mongo1 mongo2 mongo3
mkdir mongo1 
cd mongo1 && mkdir data conf log
cd data && mkdir shard1 shard2 shard3 config && cd ..
cd conf && touch config.conf mongos.conf shard1.conf shard2.conf shard3.conf && cd ..
cd log && touch config.log mongos.log shard1.log shard2.log shard3.log && cd ..
cd ..
cp -r mongo1 mongo2 && cp -r mongo1 mongo3

if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  echo "net:
    port: 27118  
    bindIp: 0.0.0.0  
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/config.log
storage:
    dbPath: $(pwd)/mongo1/data/config
    journal:
        enabled: true 
processManagement:
    fork: true
replication:
    replSetName: configs
sharding:
    clusterRole: configsvr
#security: 
    #  keyFile: D:\tool\mongodbmy\mongo\mongodb-keyfile.file
    #  authorization: enabled" >> mongo1/conf/config.conf


  echo "systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/mongos.log
net:
    port: 27119 
    bindIp: 0.0.0.0
setParameter:
    enableLocalhostAuthBypass: false
sharding:
    configDB: configs/127.0.0.1:27118,127.0.0.1:27128,127.0.0.1:27138" >> mongo1/conf/mongos.conf

  echo "net:
    port: 27111
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/shard1.log
storage:
    dbPath: $(pwd)/mongo1/data/shard1  
    journal:
      enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard1  
sharding:
    clusterRole: shardsvr " >> mongo1/conf/shard1.conf

  echo "net:
    port: 27112
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/shard2.log
storage:
    dbPath: $(pwd)/mongo1/data/shard2
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard2
sharding:
    clusterRole: shardsvr " >> mongo1/conf/shard2.conf

  echo "net:
    port: 27113
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/shard3.log
storage:
    dbPath: $(pwd)/mongo1/data/shard3
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard3
sharding:
    clusterRole: shardsvr " >> mongo1/conf/shard3.conf

  echo "net:
    port: 27128  
    bindIp: 0.0.0.0  
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo2/log/config.log
storage:
    dbPath: $(pwd)/mongo2/data/config
    journal:
        enabled: true 
processManagement:
    fork: true
replication:
    replSetName: configs
sharding:
    clusterRole: configsvr
#security: 
    #  keyFile: D:\tool\mongodbmy\mongo\mongodb-keyfile.file
    #  authorization: enabled" >> mongo2/conf/config.conf


  echo "systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo2/log/mongos.log
net:
    port: 27129 
    bindIp: 0.0.0.0
setParameter:
    enableLocalhostAuthBypass: false
sharding:
    configDB: configs/127.0.0.1:27118,127.0.0.1:27128,127.0.0.1:27138" >> mongo2/conf/mongos.conf

  echo "net:
    port: 27121
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo2/log/shard1.log
storage:
    dbPath: $(pwd)/mongo2/data/shard1  
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard1  
sharding:
    clusterRole: shardsvr " >> mongo2/conf/shard1.conf

  echo "net:
    port: 27122
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo2/log/shard2.log
storage:
    dbPath: $(pwd)/mongo2/data/shard2
    journal:
      enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard2
sharding:
    clusterRole: shardsvr " >> mongo2/conf/shard2.conf

  echo "net:
    port: 27123
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo2/log/shard3.log
storage:
    dbPath: $(pwd)/mongo2/data/shard3
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard3
sharding:
    clusterRole: shardsvr " >> mongo2/conf/shard3.conf

  echo "net:
    port: 27138  
    bindIp: 0.0.0.0  
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo3/log/config.log
storage:
    dbPath: $(pwd)/mongo3/data/config
    journal:
      enabled: true 
processManagement:
    fork: true
replication:
    replSetName: configs
sharding:
    clusterRole: configsvr
#security: 
    #  keyFile: D:\tool\mongodbmy\mongo\mongodb-keyfile.file
    #  authorization: enabled" >> mongo3/conf/config.conf


  echo "systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo3/log/mongos.log
net:
    port: 27139 
    bindIp: 0.0.0.0
setParameter:
    enableLocalhostAuthBypass: false
sharding:
    configDB: configs/127.0.0.1:27118,127.0.0.1:27128,127.0.0.1:27138" >> mongo3/conf/mongos.conf

  echo "net:
    port: 27131
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo3/log/shard1.log
storage:
    dbPath: $(pwd)/mongo3/data/shard1  
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard1  
sharding:
    clusterRole: shardsvr " >> mongo3/conf/shard1.conf

  echo "net:
    port: 27132
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo3/log/shard2.log
storage:
    dbPath: $(pwd)/mongo3/data/shard2
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard2
sharding:
    clusterRole: shardsvr " >> mongo3/conf/shard2.conf

  echo "net:
    port: 27133
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo3/log/shard3.log
storage:
    dbPath: $(pwd)/mongo3/data/shard3
    journal:
        enabled: true
processManagement:
    fork: true
replication:
    replSetName: shard3
sharding:
    clusterRole: shardsvr " >> mongo3/conf/shard3.conf



  mongod -f mongo1/conf/config.conf &&
  mongod -f mongo2/conf/config.conf &&
  mongod -f mongo3/conf/config.conf
  mongo -port 27118 << EOF
  rs.initiate({   
    _id : "configs",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27118" },         
          {_id : 1, host : "127.0.0.1:27128" },         
          {_id : 2, host : "127.0.0.1:27138" }     
      ]  })

  quit()
EOF

  mongo -port 27128 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongo -port 27138 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard1.conf &&
  mongod -f mongo2/conf/shard1.conf &&
  mongod -f mongo3/conf/shard1.conf
  mongo -port 27111 << EOF
  rs.initiate( { _id : "shard1",members : [
  {_id : 0, host : "127.0.0.1:27111"},
  {_id : 1, host : "127.0.0.1:27121"},
  {_id : 2, host : "127.0.0.1:27131"}
  ]});
  quit() 
EOF

  mongo -port 27121 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongo -port 27131 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard2.conf &&
  mongod -f mongo2/conf/shard2.conf &&
  mongod -f mongo3/conf/shard2.conf
  mongo -port 27112 << EOF
  rs.initiate({ _id : "shard2",members : [
  {_id : 0, host : "127.0.0.1:27112"},
  {_id : 1, host : "127.0.0.1:27122"},
  {_id : 2, host : "127.0.0.1:27132"}
  ]})
  quit()
EOF

  mongo -port 27122 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongo -port 27132 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard3.conf &&
  mongod -f mongo2/conf/shard3.conf &&
  mongod -f mongo3/conf/shard3.conf
  mongo -port 27113 << EOF
  rs.initiate({   
    _id : "shard3",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27113" },         
          {_id : 1, host : "127.0.0.1:27123" },         
          {_id : 2, host : "127.0.0.1:27133" }     
      ]  })

  quit()
EOF
fi
  mongo -port 27123 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongo -port 27133 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongos -f mongo1/conf/mongos.conf --fork
  mongo --port 27119 << EOF
  use admin;
  sh.addShard("shard1/127.0.0.1:27111,127.0.0.1:27121,127.0.0.1:27131");
  sh.addShard("shard2/127.0.0.1:27112,127.0.0.1:27122,127.0.0.1:27132");
  sh.addShard("shard3/127.0.0.1:27113,127.0.0.1:27123,127.0.0.1:27133");
  quit() 
EOF