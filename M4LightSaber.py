import board
import time
import neopixel
import digitalio
import busio
import adafruit_lis3dh
import random

try:
    from audiocore import WaveFile
except ImportError:
    from audioio import WaveFile

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

# define constants
COLOR=(0,0,255)
NUM_PIXELS = 131
NEOPIXEL_PIN = board.D5
POWER_PIN = board.D10
SWITCH_PIN = board.D9

# set up audio
audiofiles = ["sounds/LSOn.wav", "sounds/LSOff.wav", "sounds/LightSaberClash1.wav", "sounds/LightSaberClash2.wav",
              "sounds/LightSaberClash3.wav", "sounds/LightSaberClash4.wav"]
audio = AudioOut(board.A0)

# Set up NeoPixels
neopixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_PIXELS, brightness=1)
neopixels.fill((0,0,0))
#neopixels.show()

# Set up on/off button
button = digitalio.DigitalInOut(SWITCH_PIN)
button.switch_to_input(pull=digitalio.Pull.UP)
prevPress = False
on = False
clashNum = 2

# Set up accelerometer on I2C bus, 4G range:
i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_8_G
lis3dh.set_tap(1, 90, time_limit=4, time_latency=50, time_window=255)

enable = digitalio.DigitalInOut(POWER_PIN)
enable.direction = digitalio.Direction.OUTPUT
enable.value = False

redled = digitalio.DigitalInOut(board.D13)
redled.direction = digitalio.Direction.OUTPUT
led = neopixel.NeoPixel(board.NEOPIXEL, 1);
led.brightness = 0.2

redled.value = False
def play_file(filename):
    print("Playing file: " + filename)
    wave_file = open(filename, "rb")
    with WaveFile(wave_file) as wave:
        audio.play(wave)
        while audio.playing:
            pass
        wave_file.close()
    print("Finished")

def lightSaberOn():
    i = 0
    enable.value = True
    wave_file = open(audiofiles[0], "rb")
    redled.value = True
    with WaveFile(wave_file) as wave:
        audio.play(wave)
        while audio.playing:
            neopixels[i] = (0,0,255)
            i = (i + 1) % NUM_PIXELS
        wave_file.close()
    print("Finished")

def lightSaberOff():
    wave_file = open(audiofiles[1], "rb")
    redled.value = False
    i = NUM_PIXELS - 1
    with WaveFile(wave_file) as wave:
        audio.play(wave)
        while audio.playing:
            neopixels[i] = (0,0,0)
            i = (i - 1)
            if i < 0:
                i = 0
        wave_file.close()
    enable.value = False
    print("Finished")

def flashOnClash():
    global clashNum
    wave_file = open(audiofiles[clashNum], "rb")
    with WaveFile(wave_file) as wave:
        audio.play(wave)
        neopixels.fill((255,255,255))
        led.fill((255,255,255))
        while audio.playing:
            neopixels.fill((0,0,255))
            led.fill((0,0,255))
        wave_file.close()
    clashNum = random.randint(2,5)

while True:
    x,y,z = lis3dh.acceleration
    if lis3dh.tapped and on:
        flashOnClash()
    if x > 8 and y < 1 and z < 1:
        led[0] = (255,255,0)
    elif x < 1 and y > 8 and z < 1:
        led[0] = (0,255,255)
    elif x < 1 and y < 1 and z > 8:
        led[0] = (255,0,255)
    else:
        led[0] = (0,0,0)
    if not button.value and not prevPress:
        if not on:
            lightSaberOn()
        else:
            lightSaberOff()
        prevPressfor = True
        on = not on
    elif button.value and prevPress:
        prevPress = False
