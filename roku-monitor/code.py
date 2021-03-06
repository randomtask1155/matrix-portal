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
    try:
        data = NETWORK.fetch_data(requestURI,json_path=[{'status', 'name', 'events'}])
    except:
        scrollError("getRokuStatus error communicating with hqserver")
        return
    #print(data)
    jdata = json.loads(data)
    if len(jdata) < 2:
        print(data)
        scrollError("no rokus found in data")
        return
    for r in jdata[1]['events']:
        props = r.split(':')
        if len(props) < 3:
            print(rs)
            scrollError("unable to decode roku properties")
            return
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


def scrollError(err):
    GROUP[6].text = ""
    GROUP[5].text = err
    resetXY(GROUP)
    GROUP[0].x = -64
    GROUP[0].y = -32
    DISPLAY.refresh()
    scrollGroup(GROUP[5])


def scrollRoku(g, name, app):
    resetXY(g)
    addImageToGRoup(g, 'img/tv.bmp')
    g[5].text = name
    g[6].text = app
    DISPLAY.refresh()
    time.sleep(0.5)
    scrollALlGroups(g)
    resetXY(g)

def scrollGroup(g):
    l = len(g.text)
    for i in range(math.ceil((l*5))):
        g.x = g.x - 1
        time.sleep(.2)

def scrollALlGroups(g):
    l5 = len(g[5].text)
    l6 = len(g[6].text)
    length = 0
    if l5 > l6:
        length = math.ceil(l5 *5)
    else:
        length = math.ceil(l6 * 5)
    for i in range(length):
        g[0].x = g[0].x - 1
        g[5].x = g[5].x - 1
        g[6].x = g[6].x - 1
        time.sleep(0.2)


def resetXY(g):
    g[0].x = zeroStart[0]
    g[0].y = zeroStart[1]
    g[5].x = fiveStart[0]
    g[5].y = fiveStart[1]
    g[6].x = sixStart[0]
    g[6].y = sixStart[1]

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
#scrollError("testing error scrolling now")


try:
    NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
    NETWORK.connect()
except:
    while True:
        scrollError("wifi connect failed")
        time.sleep(3)
getRokuStatus()

interval=10
while True:
    getRokuStatus()
    foundRokuDevices = {}
    isRokuInUse = False
    
    for k in rokuDevices:
        if rokuDevices[k] != 'Roku':
            foundRokuDevices[k] = rokuDevices[k]
            isRokuInUse = True
            
    if isRokuInUse:
        for i in range(interval):
            for k in foundRokuDevices:
                scrollRoku(GROUP,k, foundRokuDevices[k])
            time.sleep(1)            
    else:
        for i in range(interval):
            playSplash(GROUP)
            time.sleep(0.5)
            continue
