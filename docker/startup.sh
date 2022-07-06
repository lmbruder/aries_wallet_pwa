#! /bin/bash

# start von-network containers
./von-network/manage start

# start indy tails server container
./indy-tails-server/docker/manage start

# start first ACA-Py
docker-compose start

# get tails url from indy tails server
echo "TAILS_URL=$(curl -s localhost:4044/api/tunnels | jq -r '.tunnels[] | select(.name|IN("command_line")) | .public_url')" > .env 

# build second agent with matching tails server URL
docker-compose -f docker-compose.second.yml up 

# attach to logs 
docker-compose logs -f -t

exit 0
