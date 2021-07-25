import board
import busio
import math
import json
from rtc import RTC
from digitalio import DigitalInOut
import time

from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_bitmap_font import bitmap_font
import adafruit_display_text.label
import displayio
import adafruit_lis3dh

try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

BITPLANES = 6
TIMEZONE = secrets['timezone']
requestURI = secrets['uri']
rokuDevices = {}


def getRokuStatus():
    data = NETWORK.fetch_data(requestURI,json_path=[{'status', 'name', 'events'}])
    #print(data)
    jdata = json.loads(data)
    if len(jdata) < 2:
        print(data)
        print("no rokus found in data")
        raise
    for r in jdata[1]['events']:
        props = r.split(':')
        if len(props) < 3:
            print(rs)
            print("unable to decode roku properties")
            raise
        rokuDevices[props[0]] = props[2]

def addImageToGRoup(g, f):
    BITMAP = displayio.OnDiskBitmap(open(f, 'rb'))
    TILE_GRID = displayio.TileGrid(BITMAP,
                                   pixel_shader=displayio.ColorConverter(),)
    TILE_GRID.x = g.x
    TILE_GRID.y = g.y
    GROUP[0] = TILE_GRID
    #g.x = (DISPLAY.width - g.bounding_box[2] + 1) // 2
    #g.y = DISPLAY.height // 2 - 1

def playSplash(g):
    g[0].x = zeroStart[0]
    g[0].y = zeroStart[1]
    GROUP[5].text = ""
    GROUP[6].text = ""
    
    for i in range(4):
        addImageToGRoup(g, 'img/tv-guy.bmp')
        DISPLAY.refresh()
        time.sleep(0.5)
        addImageToGRoup(g, 'img/tv-guy-1.bmp')
        DISPLAY.refresh()
        time.sleep(0.5)
    addImageToGRoup(g, 'img/tv-guy.bmp')
    DISPLAY.refresh()
    



    
def scrollRoku(g, name, app):
    g[0].x = zeroStart[0]
    g[0].y = zeroStart[1]
    g[5].x = fiveStart[0]
    g[5].y = fiveStart[1]
    g[6].x = sixStart[0]
    g[6].y = sixStart[1]
    addImageToGRoup(g, 'img/tv.bmp')
    g[5].text = name 
    g[6].text = app
    DISPLAY.refresh()
    time.sleep(0.5)
    for i in range(64):
        g[0].x = g[0].x - 1
        g[5].x = g[5].x - 1
        g[6].x = g[6].x - 1
        time.sleep(0.2)



MATRIX = Matrix(bit_depth=BITPLANES)
DISPLAY = MATRIX.display

LARGE_FONT = bitmap_font.load_font('/fonts/helvB12.bdf')
SMALL_FONT = bitmap_font.load_font('/fonts/helvR10.bdf')
SYMBOL_FONT = bitmap_font.load_font('/fonts/6x10.bdf')
LARGE_FONT.load_glyphs('0123456789:')
SMALL_FONT.load_glyphs('0123456789:/.%')
SYMBOL_FONT.load_glyphs('\u21A5\u21A7')

GROUP = displayio.Group(max_size=10)
try:
    FILENAME = 'img/tv.bmp'
    BITMAP = displayio.OnDiskBitmap(open(FILENAME, 'rb'))
    TILE_GRID = displayio.TileGrid(BITMAP,
                                   pixel_shader=displayio.ColorConverter(),)
    GROUP.append(TILE_GRID)
except:
    GROUP.append(adafruit_display_text.label.Label(SMALL_FONT, color=0xFF0000,
                                                   text='AWOO'))
    GROUP[0].x = (DISPLAY.width - GROUP[0].bounding_box[2] + 1) // 2
    GROUP[0].y = DISPLAY.height // 2 - 1
for i in range(4):
    GROUP.append(adafruit_display_text.label.Label(SMALL_FONT, color=0,
                                                   text='99.9%', y=-99))
# Element 5 is the moon percentage (on top of the outline labels)
GROUP.append(adafruit_display_text.label.Label(SMALL_FONT, color=0x808080,
                                               text='99.9%', y=-99))
# Element 6 is the current time
GROUP.append(adafruit_display_text.label.Label(LARGE_FONT, color=0xD04901,
                                               text='12:00', y=-99))
                                               
zeroStart = [GROUP[0].x, GROUP[0].y]
fiveStart = [30, 10]
sixStart = [31, 22]

#GROUP[5].text = "Family_Room"
GROUP[5].x = fiveStart[0]
GROUP[5].y = fiveStart[1]

#GROUP[6].text = "roku"
GROUP[6].x = sixStart[0]
GROUP[6].y = sixStart[1]
DISPLAY.show(GROUP)
playSplash(GROUP)



NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
NETWORK.connect()
getRokuStatus()
#print(rokuDevices)
##print(rokus[1]['events'])

interval=3
#iterationCount=(interval + (1 - interval) ) * 3600
#count=iterationCount
while True:
    #playSplash(GROUP)
    getRokuStatus()
    isRokuInUse = False
    for k in rokuDevices:
        if rokuDevices[k] != 'Roku':
            scrollRoku(GROUP, k, rokuDevices[k])
            isRokuInUse = True
    if not isRokuInUse:
        playSplash(GROUP)
    #if getTimeSuccess == False:
    #    getTimeSuccess = setClock()
    #if count >= iterationCount:
    #    NOW = time.time()
    #    GROUP[6].text = str(math.ceil( (vacationDate - int(time.time()) ) / 60 / 60 / 24)) + " Days"
    #    DISPLAY.refresh()
    #    count = 0
    #count = count + 1
    #treeBreeze(GROUP[0])
    time.sleep(interval)

