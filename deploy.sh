#!/usr/bin/env bash

if [ "$DEPLOY_START_NETWORK_PSK" -eq "" ]; then
    echo "Warning: \$DEPLOY_START_NETWORK_PSK not set."
fi
if [ "$DEPLOY_ROBOT_NETWORK_PSK" -eq "" ]; then
    echo "Warning: \$DEPLOY_ROBOT_NETWORK_PSK not set."
fi

start_network=$(networksetup -getairportnetwork en0 | cut -d ' ' -f 4)
robot_network=1418

echo "Connecting to $robot_network..."
networksetup -setairportnetwork en0 $robot_network $DEPLOY_ROBOT_NETWORK_PSK
python3 robot/robot.py deploy
echo "Reconnecting to $start_network..."
networksetup -setairportnetwork en0 $start_network $DEPLOY_START_NETWORK_PSK
