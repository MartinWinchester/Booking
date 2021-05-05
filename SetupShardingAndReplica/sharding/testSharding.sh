mongo --port 27019 << EOF
use config
db.setting.save({"_id":"chunksize","value":1})
use testdb;
sh.enableSharding("testdb")
use testdb;
db.createCollection("user");
db.user.createIndex({"name":"hashed"}) 
sh.shardCollection( "testdb.user", { "name" : "hashed" } ) 
for(i=1;i<=3000;i++){db.user.insert({"id":i,"name":"zzx"+i})} 
sh.status()
EOF
