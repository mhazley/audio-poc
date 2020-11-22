#!/bin/bash

python audio_manager.py -mqtt_host 127.0.0.1 -mqtt_port 1883 -debug_level DEBUG > /data/audio.log 2>&1

echo "Will restart..."
sleep 1
exit 1
