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
if [ $(docker inspect -f '{{.State.Running}}' act8004) = "true" ]; then
docker exec act8004 ./stop.sh;
docker stop act8004;
docker rm act8004;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8005) = "true" ]; then
docker exec act8005 ./stop.sh;
docker stop act8005;
docker rm act8005;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8007) = "true" ]; then
docker exec act8007 ./stop.sh;
docker stop act8007;
docker rm act8007;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8008) = "true" ]; then
docker exec act8008./stop.sh;
docker stop act8008;
docker rm act8008;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8009) = "true" ]; then
docker exec act8009 ./stop.sh;
docker stop act8009;
docker rm act8009;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8010) = "true" ]; then
docker exec act8010 ./stop.sh;
docker stop act80010;
docker rm act8010;
fi
if [ $(docker inspect -f '{{.State.Running}}' act8006) = "true" ]; then
docker exec act8006 ./stop.sh;
docker stop act8006;
docker rm act8006;
fi

docker stop act8001;
docker rm act8001;
docker stop act8002;
docker rm act8002;
docker stop act8003;
docker rm act8003;
docker stop act8004;
docker rm act8004;
docker stop act8005;
docker rm act8005;
docker stop act8006;
docker rm act8006;
docker stop act8007;
docker rm act8007;
docker stop act8008;
docker rm act8008;
docker stop act8009;
docker rm act8009;
docker stop act8010;
docker rm act8010;

