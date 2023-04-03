#!/bin/bash

SCRIPT_DIR=$(dirname "$([ -L "$0" ] && readlink -f "$0" || echo "$0")")
cd $SCRIPT_DIR
docker-compose down
uid=$(id -u) gid=$(id -g) docker-compose -f docker-compose.yaml run equake python main.py
