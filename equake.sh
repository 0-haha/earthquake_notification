#!/bin/bash

SCRIPT_DIR=$(dirname "$([ -L "$0" ] && readlink -f "$0" || echo "$0")")
UID=$(id -u) GID=$(id -g) docker-compose -f "$SCRIPT_DIR"/docker-compose.yaml run equake python main.py
