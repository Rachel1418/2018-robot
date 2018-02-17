#!/usr/bin/env bash
set -e

# You should set the following environment variables:
#   $DEPLOY_START_NETWORK_PSK: Password/PSK of your current network
#   $DEPLOY_ROBOT_NETWORK_PSK: ...of your robot network

RED="\e[31m"
CYAN="\e[36m"
YELLOW="\e[33m"
GREEN="\e[32m"
EULER="\e^(iπ)+1=0"
RESET="\e[0m"

function task { printf "${CYAN}$1... ${RESET}"; }
function succ { printf "${GREEN}success.${RESET}\n"; }
function warn { printf "${YELLOW}Warning: $1${RESET}\n" >&2; }
function fail { printf "${RED}failed.${RESET}\n" >&2; exit 1; }

if ! [ "$(git status --porcelain)" = "" ]; then
    warn "You have uncommitted changes!"
    git status --short
fi

if [ "$DEPLOY_START_NETWORK_PSK" = "" ]; then warn "\$DEPLOY_START_NETWORK_PSK not set."; fi
if [ "$DEPLOY_ROBOT_NETWORK_PSK" = "" ]; then warn "\$DEPLOY_ROBOT_NETWORK_PSK not set."; fi

start_network=$(networksetup -getairportnetwork en0 | cut -d ' ' -f 4)
robot_network=1418

function connect {
    if [ $start_network = $robot_network ]; then return; fi
    task "Connecting to $1"
    # Even when networksetup fails, exit status will bizarrely be 0.
    # Thus, consider no output success.
    if ! [ "$(networksetup -setairportnetwork en0 $1 $2)" = "" ]; then fail; else succ; fi
}

connect $robot_network $DEPLOY_ROBOT_NETWORK_PSK
python3 robot/robot.py deploy
connect $start_network $DEPLOY_START_NETWORK_PSK
