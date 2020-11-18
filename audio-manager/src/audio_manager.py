import simpleaudio as sa
import time

wave_obj = sa.WaveObject.from_wave_file("./audio/one.wav")
print(wave_obj)
while True:
    print("Playing...")
    play_obj = wave_obj.play()
    print(play_obj)
    play_obj.wait_done()
    time.sleep(2)
