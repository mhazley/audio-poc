import simpleaudio as sa
import time
import logging
import argparse
import paho.mqtt.client as mqtt
import json
import signal
from pathlib import Path
from threading import Thread


class AudioManager:
    """
    A SimpleAudio wrapper with an MQTT interface.
    Audio files must be stored in 'audio' directory alongside this file.
    """

    FILE_KEY = 'file'
    AUDIO_PATH = './audio/'
    STOP_WAIT = 0.35    # When stopping audio, we need to wait ~300ms for the PCM device to be ready again

    def __init__(self, mqtt_host: str = '127.0.0.1', mqtt_port: int = 1883, play_topic: str = 'audio/play',
                 stop_topic: str = 'audio/stop'):
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_subscribe = self._on_subscribe
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port

        self._play_topic = play_topic
        self._stop_topic = stop_topic

        self._wave_obj = None
        self._play_obj = None

    def run(self):
        self._client.connect(host=self._mqtt_host, port=self._mqtt_port)
        self._client.subscribe(topic=self._play_topic)
        self._client.subscribe(topic=self._stop_topic)

        self._client.loop_forever()

    def stop(self):
        # stop audio
        self._client.disconnect()

    def _play_audio(self, file_path: str):
        logging.debug(f"Starting audio thread for {file_path}")
        self._wave_obj = sa.WaveObject.from_wave_file(file_path)
        self._play_obj = self._wave_obj.play()
        self._play_obj.wait_done()
        logging.debug("Audio thread complete")

    def _handle_msg(self, topic: str, payload: str):
        if topic == self._play_topic:
            try:
                json_payload = json.loads(payload)
                try:
                    file_name = json_payload[self.FILE_KEY]
                    file_path = f'{self.AUDIO_PATH}{file_name}'
                    if Path(file_path).is_file():

                        if self._play_obj and self._play_obj.is_playing():
                            logging.debug("Stopping already playing audio...")
                            self._play_obj.stop()
                            time.sleep(self.STOP_WAIT)

                        logging.info(f'Playing audio file: {file_path}')
                        t = Thread(target=self._play_audio, args=(file_path,))
                        t.start()
                    else:
                        logging.warning(f'{file_name} does not exist')

                except KeyError:
                    logging.warning(f'Missing {self.FILE_KEY} key in msg')

            except json.JSONDecodeError:
                logging.warning(f'Malformed JSON in msg')
        elif topic == self._stop_topic:
            sa.stop_all()

    # MQTT Callbacks
    def _on_message(self, client, obj, msg):
        logging.debug(f'on_message: Topic: {msg.topic}, Payload: {msg.payload}')
        self._handle_msg(msg.topic, msg.payload)

    @staticmethod
    def _on_connect(client, obj, flags, rc):
        if rc == 0:
            logging.debug('MQTT Connection Successful')
        else:
            logging.warning(f'MQTT Connection Unsucessful: {rc}')

    @staticmethod
    def _on_publish(client, obj, mid):
        logging.debug(f'Published mid: {mid}')

    @staticmethod
    def _on_subscribe(client, obj, mid, granted_qos):
        logging.debug(f'Subscribed: {mid}')


def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        logging.warning("SIGINT, exiting...")
        audio_manager.stop()
        exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='Audio Manager')

    parser.add_argument('-mqtt_host', default='127.0.0.1', help='IP Address of MQTT Broker')
    parser.add_argument('-mqtt_port', default=1883, type=int, help='Port used by MQTT Broker')
    parser.add_argument('-debug_level', default='INFO', help='Logging level')

    args = parser.parse_args()

    logging.basicConfig(level=args.debug_level,
                        format='%(asctime)s %(levelname)-8s %(message)s')

    audio_manager = AudioManager(mqtt_host=args.mqtt_host, mqtt_port=args.mqtt_port)
    audio_manager.run()
