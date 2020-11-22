# Balena Audio POC

This repo presents a simple POC of a [MAX98357A I2S Amplifier](https://www.adafruit.com/product/3006) configured with a Raspberry Pi 3 running on Balena.
 
 This is built as a standalone container, based around SimpleAudio, with project audio files pre-included. These can be played via a simple MQTT interface. Audio can also be stopped on the same interface. 
 
 Project audio files should be stored in `audio` dir, alongside the main `audio_manager.py` program.
 
 ### Wiring
 The diagram below shows the RPi header with the connections to the MAX98357A I2S Amplifier breakout board.
 
```
          .___.
      --1-|O X|--2-/-Vin
      --3-|O O|--4-
      --5-|O O|--6-/-GND
      --7-|O O|--8-
      --9-|O O|-10-
      -11-|O O|-12-/-BCLK
      -13-|O O|-14-
      -15-|O O|-16-
      -17-|O O|-18-
      -19-|O O|-20-
      -21-|O O|-22-
      -23-|O O|-24-
      -25-|O O|-26-
      -27-|O O|-28-
      -29-|O O|-30-
      -31-|O O|-32-
      -33-|O O|-34-
 LRC-/-35-|O O|-36-
      -37-|O O|-38-
GAIN-/-39-|O O|-40-/-DIN
          '---'
        RPi Header
```
In this case, the GAIN pin is connected to a Ground, this provides 12dB of gain. Gain can be tweaked as per table below:

| | |
|---|---|
| 100K resistor is connected between GAIN and GND  | 15dB |
| GAIN connected to GND  | 12dB |
| GAIN is not connected to anything  | 9dB |
| GAIN is connected to VIN  | 6dB |
| 100K resistor is connected between GAIN and VIN  | 3dB |

Note, distrotion was experienced when testing at 15dB.

### Balena Settings

In either `Fleet Configuration` or `Device Configuration` in the Balena Project dashboard, the following settings need to be applied.

* `Define DT parameters` must be set to `"i2c_arm=on","spi=on","audio=off"`
* Under `Custom configuration variables`,  add `BALENA_HOST_CONFIG_dtoverlay` with `hifiberry-dac`

### MQTT Protocol

The MQTT topics that the Audio Container is subscribed to are customisable at runtime but the defaults are:

* Play topic: `audio/play`
* Stop topic: `audio/stop`

The play topic is used to trigger playback of a `<filename>` from the `audio` directory and it takes a JSON message as follows:

```json
{
    'file': <filename>
}
```

The stop topic will imediately stop any playback that is running and it requires no payload.

### Logs

Audio Container logs can be viewed by ssh'ing to a device and running:

```bash
$ tail -f /data/audio.log
```

### Demo

This POC contains example `.wav` files and in `scripts` there is a basic python script that will cycle through each of these files and request playback via MQTT.

After pushing the POC to a Balena device, run the following (replace host with device hostname) from a python3 environment on the same network:

```bash
$ pip install -r demo_requirements.txt
$ python audio_demo.py -mqtt_host bda395a.local 
```