	mongo -port 27002 << EOF
rs.secondaryOk()
quit()
EOF