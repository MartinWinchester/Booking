mongo -port 27018 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27028 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27038 <<EOF
use admin
db.shutdownServer()
quit()
EOF

mongo -port 27011 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27012 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27013 <<EOF
use admin
db.shutdownServer()
quit()
EOF

mongo -port 27021 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27022 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27023 <<EOF
use admin
db.shutdownServer()
quit()
EOF

mongo -port 27031 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27032 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27033 <<EOF
use admin
db.shutdownServer()
quit()
EOF


mongo -port 27019 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27029 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27039 <<EOF
use admin
db.shutdownServer()
quit()
EOF