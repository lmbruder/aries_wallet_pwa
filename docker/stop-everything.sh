#! /bin/bash

# shuts down second acapy
docker-compose -f docker-compose.second.yml down

# shuts down acapy
docker-compose stop

# shuts down indy-tails server
./indy-tails-server/docker/manage stop

# shuts down network
./von-network/manage stop

exit 0
