#! /bin/bash

# build von-network containers
./von-network/manage build
./von-network/manage start

# start indy tails server container
./indy-tails-server/docker/manage up

# wait until von-network is ready
sleep 20 

# curl genesis file and save content to txt file
genesis=$(curl  http://localhost:9000/genesis)
echo "$genesis" > "network-files/von_network.txt"

# build first ACA-Py
docker-compose up -d

# get tails url from indy tails server
echo "TAILS_URL=$(curl -s localhost:4044/api/tunnels | jq -r '.tunnels[] | select(.name|IN("command_line")) | .public_url')" > .env 

# build second agent with matching tails server URL
docker-compose -f docker-compose.second.yml up 

# attach to logs 
docker-compose logs -f -t

exit 0
