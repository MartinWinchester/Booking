# build (only once)
docker build -t client:latest -f DockerfileUser .
# run, will port-forward to different ports
docker run --network="host" client:latest
