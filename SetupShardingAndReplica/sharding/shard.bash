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
    port: 27018  
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
  #  authorization: enabled" > mongo1/conf/config.conf


  echo "systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/mongos.log
  net:
    port: 27019 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo1/conf/mongos.conf

  echo "net:
    port: 27011
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
    port: 27012
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
    port: 27013
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
    port: 27028  
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
    port: 27029 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo2/conf/mongos.conf

  echo "net:
    port: 27021
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
    port: 27022
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
    port: 27023
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
    port: 27038  
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
    port: 27039 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo3/conf/mongos.conf

  echo "net:
    port: 27031
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
    port: 27032
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
    port: 27033
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
  mongo -port 27018 <<EOF
  rs.initiate({   
    _id : "configs",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27018" },         
          {_id : 1, host : "127.0.0.1:27028" },         
          {_id : 2, host : "127.0.0.1:27038" }     
      ]  })

  quit()
EOF
  mongo -port 27028 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27038 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard1.conf &&
  mongod -f mongo2/conf/shard1.conf &&
  mongod -f mongo3/conf/shard1.conf
  mongo -port 27011 << EOF
  rs.initiate(config = { _id : "shard1",members : [
  {_id : 0, host : "127.0.0.1:27011"},
  {_id : 1, host : "127.0.0.1:27021"},
  {_id : 2, host : "127.0.0.1:27031"}
  ]});
  quit() 
EOF
  mongo -port 27021 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27031 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard2.conf &&
  mongod -f mongo2/conf/shard2.conf &&
  mongod -f mongo3/conf/shard2.conf
  mongo -port 27012 <<EOF
  rs.initiate({ _id : "shard2",members : [
  {_id : 0, host : "127.0.0.1:27012"},
  {_id : 1, host : "127.0.0.1:27022"},
  {_id : 2, host : "127.0.0.1:27032"}
  ]})
  quit()
EOF
  mongo -port 27022 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27032 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard3.conf &&
  mongod -f mongo2/conf/shard3.conf &&
  mongod -f mongo3/conf/shard3.conf
  mongo -port 27013 <<EOF
  rs.initiate({   
    _id : "configs",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27013" },         
          {_id : 1, host : "127.0.0.1:27023" },         
          {_id : 2, host : "127.0.0.1:27033" }     
      ]  })

  quit()
EOF
  mongo -port 27023 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27033 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongos -f mongo1/conf/mongos.conf --fork
  mongo --port 27019 << EOF
  use admin;
  sh.addShard("shard1/127.0.0.1:27011,127.0.0.1:27021,127.0.0.1:27031");
  sh.addShard("shard2/127.0.0.1:27012,127.0.0.1:27022,127.0.0.1:27032");
  sh.addShard("shard3/127.0.0.1:27013,127.0.0.1:27023,127.0.0.1:27033");
  quit()
EOF

elif [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ]; then
    base="$(pwd)"
    echo "$base"
    base="${base:2}"
    echo "$base"

  echo "net:
    port: 27018  
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
  #  authorization: enabled" > mongo1/conf/config.conf


  echo "systemLog:
    destination: file
    logAppend: true
    path: $(pwd)/mongo1/log/mongos.log
  net:
    port: 27019 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo1/conf/mongos.conf

  echo "net:
    port: 27011
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
    port: 27012
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
    port: 27013
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
    port: 27028  
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
    port: 27029 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo2/conf/mongos.conf

  echo "net:
    port: 27021
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
    port: 27022
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
    port: 27023
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
    port: 27038  
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
    port: 27039 
    bindIp: 0.0.0.0
  setParameter:
    enableLocalhostAuthBypass: false
  sharding:
    configDB: configs/127.0.0.1:27018,127.0.0.1:27028,127.0.0.1:27038" >> mongo3/conf/mongos.conf

  echo "net:
    port: 27031
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
    port: 27032
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
    port: 27033
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
  mongo -port 27018 <<EOF
  rs.initiate({   
    _id : "configs",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27018" },         
          {_id : 1, host : "127.0.0.1:27028" },         
          {_id : 2, host : "127.0.0.1:27038" }     
      ]  })

  quit()
EOF
  mongo -port 27028 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27038 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard1.conf &&
  mongod -f mongo2/conf/shard1.conf &&
  mongod -f mongo3/conf/shard1.conf
  mongo -port 27011 << EOF
  rs.initiate(config = { _id : "shard1",members : [
  {_id : 0, host : "127.0.0.1:27011"},
  {_id : 1, host : "127.0.0.1:27021"},
  {_id : 2, host : "127.0.0.1:27031"}
  ]});
  quit() 
EOF
  mongo -port 27021 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27031 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard2.conf &&
  mongod -f mongo2/conf/shard2.conf &&
  mongod -f mongo3/conf/shard2.conf
  mongo -port 27012 <<EOF
  rs.initiate({ _id : "shard2",members : [
  {_id : 0, host : "127.0.0.1:27012"},
  {_id : 1, host : "127.0.0.1:27022"},
  {_id : 2, host : "127.0.0.1:27032"}
  ]})
  quit()
EOF
  mongo -port 27022 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27032 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongod -f mongo1/conf/shard3.conf &&
  mongod -f mongo2/conf/shard3.conf &&
  mongod -f mongo3/conf/shard3.conf
  mongo -port 27013 <<EOF
  rs.initiate({   
    _id : "configs",    
    configsvr: true, 
      members : [         
          {_id : 0, host : "127.0.0.1:27013" },         
          {_id : 1, host : "127.0.0.1:27023" },         
          {_id : 2, host : "127.0.0.1:27033" }     
      ]  })

  quit()
EOF
  mongo -port 27023 << EOF
  rs.secondaryOk()
  quit()
EOF
  mongo -port 27033 << EOF
  rs.secondaryOk()
  quit()
EOF

  mongos -f mongo1/conf/mongos.conf --fork
  mongo --port 27019 << EOF
  use admin;
  sh.addShard("shard1/127.0.0.1:27011,127.0.0.1:27021,127.0.0.1:27031");
  sh.addShard("shard2/127.0.0.1:27012,127.0.0.1:27022,127.0.0.1:27032");
  sh.addShard("shard3/127.0.0.1:27013,127.0.0.1:27023,127.0.0.1:27033");
  quit()
EOF