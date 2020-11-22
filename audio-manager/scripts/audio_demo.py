import time
import logging
import argparse
import paho.mqtt.client as mqtt
import os
import json


parser = argparse.ArgumentParser(description='Audio Manager Test')

parser.add_argument('-mqtt_host', default='127.0.0.1', help='IP Address of MQTT Broker')
parser.add_argument('-mqtt_port', default=1883, type=int, help='Port used by MQTT Broker')

args = parser.parse_args()

logging.basicConfig(level='INFO',
                    format='%(asctime)s %(levelname)-8s %(message)s')

client = mqtt.Client()
client.connect(host=args.mqtt_host, port=args.mqtt_port)
play_topic = 'audio/play'

logging.info("This script will exercise the Audio Manager class...")
time.sleep(1)

audio_file_list = os.listdir('../src/audio/')

for file in audio_file_list:
    audio_msg = { 'file': file }
    logging.info(f'Sending command to {play_topic}:\n{json.dumps(audio_msg, indent=4)}')
    client.publish(play_topic, json.dumps(audio_msg))
    time.sleep(3)

