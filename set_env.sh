#!/usr/bin/env bash
export $(cat .env | xargs)

export USER_ID=$(id -u);
export GROUP_ID=$(id -g);
export CONTAINER_HOST_IP=docker-host;

# DEFAULT WEBHUB AND NODES CONFIGURATIONS
export NUMBER_OF_WEBDRIVER_NODES=${NUMBER_OF_WEBDRIVER_NODES:-0}
export NUMBER_OF_WEBDRIVER_PER_NODE=1 # Do not increase this.
export WEBDRIVER_PORT=5901
export GRID_TIMEOUT=300 # second = 5 minutes
export GRID_MAX_SESSION=$(( $NUMBER_OF_WEBDRIVER_NODES * $NUMBER_OF_WEBDRIVER_PER_NODE * 5))