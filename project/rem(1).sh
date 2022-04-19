#!/bin/sh
if [ $(docker inspect -f '{{.State.Running}}' act8001) = "true" ]; then
docker exec act8001 ./stop.sh;
docker stop act8001;
docker rm act8001;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8002) = "true" ]; then
docker exec act8002 ./stop.sh;
docker stop act8002;
docker rm act8002;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8003) = "true" ]; then
docker exec act8003 ./stop.sh;
docker stop act8003;
docker rm act8003;
fi