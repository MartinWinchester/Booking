# kill all running containers
docker kill $(docker ps -q)
# build (only once)
docker build -t server:latest .
# run, will port-forward to different ports
docker run -p 8080:8080 server:latest

# start interactive bash shell in container
# winpty docker run -it server:latest bash