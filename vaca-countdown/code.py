import board
import busio
import math
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
getTimeSuccess = False
vacationDate=1623474000

def setClock():
    try:
        DATETIME, UTC_OFFSET = update_time(TIMEZONE)
        return True
    except:
        GROUP[6].text = "time ERR"
        time.sleep(10)
        return False

def parse_time(timestring, is_dst=-1):
    """ Given a string of the format YYYY-MM-DDTHH:MM:SS.SS-HH:MM (and
        optionally a DST flag), convert to and return an equivalent
        time.struct_time (strptime() isn't available here). Calling function
        can use time.mktime() on result if epoch seconds is needed instead.
        Time string is assumed local time; UTC offset is ignored. If seconds
        value includes a decimal fraction it's ignored.
    """
    date_time = timestring.split('T')        # Separate into date and time
    year_month_day = date_time[0].split('-') # Separate time into Y/M/D
    hour_minute_second = date_time[1].split('+')[0].split('-')[0].split(':')
    return time.struct_time(int(year_month_day[0]),
                            int(year_month_day[1]),
                            int(year_month_day[2]),
                            int(hour_minute_second[0]),
                            int(hour_minute_second[1]),
                            int(hour_minute_second[2].split('.')[0]),
                            -1, -1, is_dst)


def update_time(timezone=None):
    """ Update system date/time from WorldTimeAPI public server;
        no account required. Pass in time zone string
        (http://worldtimeapi.org/api/timezone for list)
        or None to use IP geolocation. Returns current local time as a
        time.struct_time and UTC offset as string. This may throw an
        exception on fetch_data() - it is NOT CAUGHT HERE, should be
        handled in the calling code because different behaviors may be
        needed in different situations (e.g. reschedule for later).
    """
    if timezone: # Use timezone api
        time_url = 'http://worldtimeapi.org/api/timezone/' + timezone
    else: # Use IP geolocation
        time_url = 'http://worldtimeapi.org/api/ip'

    time_data = NETWORK.fetch_data(time_url,
                                   json_path=[['datetime'], ['dst'],
                                              ['utc_offset']])
    time_struct = parse_time(time_data[0], time_data[1])
    RTC().datetime = time_struct
    return time_struct, time_data[2]

def addImageToGRoup(g, f):
    BITMAP = displayio.OnDiskBitmap(open(f, 'rb'))
    TILE_GRID = displayio.TileGrid(BITMAP,
                                   pixel_shader=displayio.ColorConverter(),)
    TILE_GRID.x = g.x
    TILE_GRID.y = g.y
    GROUP[0] = TILE_GRID
    #g.x = (DISPLAY.width - g.bounding_box[2] + 1) // 2
    #g.y = DISPLAY.height // 2 - 1


def treeBreeze(g):
    for x in range(1):
        addImageToGRoup(g, 'img/palm-trees-' + str(x+1) + '.bmp')
        DISPLAY.refresh()
        time.sleep(0.2)
    addImageToGRoup(g, 'img/palm-trees-0.bmp')




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
    FILENAME = 'img/palm-trees-0.bmp'
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
GROUP.append(adafruit_display_text.label.Label(SMALL_FONT, color=0xD04901,
                                               text='99.9%', y=-99))
# Element 6 is the current time
GROUP.append(adafruit_display_text.label.Label(LARGE_FONT, color=0x808080,
                                               text='12:00', y=-99))
GROUP[5].text = "Aulani"
GROUP[5].y = 5
GROUP[5].x = 20
GROUP[6].text = "0 Days"
GROUP[6].y = 26
GROUP[6].x = 9
DISPLAY.show(GROUP)

NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
NETWORK.connect()

interval=0.5
iterationCount=(interval + (1 - interval) ) * 3600
count=iterationCount
while True:
    if getTimeSuccess == False:
        getTimeSuccess = setClock()
    if count >= iterationCount:
        NOW = time.time()
        GROUP[6].text = str(math.ceil( (vacationDate - int(time.time()) ) / 60 / 60 / 24)) + " Days"
        DISPLAY.refresh()
        count = 0
    count = count + 1
    treeBreeze(GROUP[0])
    time.sleep(interval)
