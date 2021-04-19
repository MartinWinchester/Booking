# kill all running containers
docker kill $(docker ps -q)
# remove stopped containers
docker rm $(docker ps -a -q)
# build (only once)
docker build -t server:latest Server
# run, will port-forward to different ports
docker run -d -p 8080:8080 server:latest
# build (only once)
docker build -t client:latest -f Clients/DockerfileUser .
# run, will port-forward to different ports
docker run --network="host" client:latest
