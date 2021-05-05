mongo -port 27001 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27002 <<EOF
use admin
db.shutdownServer()
quit()
EOF
mongo -port 27003 <<EOF
use admin
db.shutdownServer()
quit()
EOF