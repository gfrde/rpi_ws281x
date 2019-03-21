"""

tries to use the telegram bot, if a token file "telegram.token' is found in local dir or in /etc


for using telegram, install the bot via pip:
    pip install python-telegram-bot

"""

import sys

sys.path.append('../python')

import os
import time
import SocketServer
import SimpleHTTPServer
import logging

from neopixel import *

PORT = 8080
telegramToken = None
telegramTask = None
searchTelegramToken = [
    './telegram.token',
    '/etc/telegram.token'
]

# LED strip configuration:
LED_COUNT = 444  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_RGBW

strip = None

strips = {
    0: {'name': 'tv', 'factor': 1.0},
    10: {'name': 'space', 'factor': 0.5},
    60: {'name': 'space', 'factor': 1.0},
    180: {'name': 'couch', 'factor': 1.0},
    240: {'name': 'wall', 'factor': 1.0},
    300: {'name': 'read', 'factor': 1.0},
}


#def Color(red, green, blue, white=0):
#    """Convert the provided red, green, blue color to a 24-bit color value.
#    Each color component should be a value 0-255 where 0 is the lowest intensity
#    and 255 is the highest intensity.
#    """
#    return (white << 24) | (red << 16) | (green << 8) | blue


def factorizeByteWise(v, factor):
    blue = int((v & 0xff) * factor)
    green = int(((v >> 8) & 0xff) * factor)
    red = int(((v >> 16) & 0xff) * factor)
    white = int(((v >> 24) & 0xff) * factor)
    return Color(red, green, blue, white)


def addByteWise(v, r, g, b, w):
    blue = int((v & 0xff) + b)
    green = int(((v >> 8) & 0xff) + g)
    red = int(((v >> 16) & 0xff) + r)
    white = int(((v >> 24) & 0xff) + w)

    blue = min(255, blue)
    blue = max(0, blue)

    green = min(255, green)
    green = max(0, green)

    red = min(255, red)
    red = max(0, red)

    white = min(255, white)
    white = max(0, white)

    return Color(red, green, blue, white)


std = Color(255, 255, 255, 255)
stripColor = {}

for c in strips:
    val = strips[c]
    v = {
        'factor': val['factor'],
        'color': std
    }
    stripColor[c] = v


def colorSet(currentColorSetting):
    logging.info('setting color')
    """Wipe color across display a pixel at a time."""
    current = currentColorSetting[0]['color']
    current = factorizeByteWise(current, currentColorSetting[0]['factor'])

    for i in range(strip.numPixels()):
        if i in stripColor:
            current = currentColorSetting[i]['color']
            current = factorizeByteWise(current, currentColorSetting[i]['factor'])

        # print(' %5d: %s' % (i, str(current)))
        if not strip is None:
            strip.setPixelColor(i, current)
    if not strip is None:
        strip.show()


# Define functions which animate LEDs in various ways.
def colorWipe(color, wait_ms=0):
    print('wiping color')
    if strip is None:
        logging.warn('STRIP is None')
        return

    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)

        if i % 2 == 0:
            strip.show()
            time.sleep(wait_ms / 1000.0)

    strip.show()


def ledOn():
    colorSet(stripColor)


def ledOff():
    colorWipe(Color(0, 0, 0, 0))


def ledRed():
    logging.info('ledRed')
    for c in stripColor:
        stripColor[c]['color'] = Color(255,0,0,0)
    colorSet(stripColor)


def ledRedMore():
    logging.info('ledRedMore')
    for c in stripColor:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 25, 0, 0, 0)
    colorSet(stripColor)


def ledRedLess():
    logging.info('ledRedLess')
    for c in stripColor:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], -25, 0, 0, 0)
    colorSet(stripColor)


def ledGreen():
    logging.info('ledGreen')
    for c in stripColor:
        stripColor[c]['color'] = Color(0,255,0,0)
    colorSet(stripColor)


def ledGreenMore():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, 25, 0, 0)
    colorSet(stripColor)


def ledGreenLess():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, -25, 0, 0)
    colorSet(stripColor)


def ledBlue():
    logging.info('ledBlue')
    for c in stripColor:
        stripColor[c]['color'] = Color(0,0,255,0)
    colorSet(stripColor)


def ledBlueMore():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, 0, 25, 0)
    colorSet(stripColor)


def ledBlueLess():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, 0, -25, 0)
    colorSet(stripColor)


def ledWhiteMore():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, 0, 0, 25)
    colorSet(stripColor)


def ledWhiteLess():
    for c in strips:
        stripColor[c]['color'] = addByteWise(stripColor[c]['color'], 0, 0, 0, -25)
    colorSet(stripColor)


def ledBright():
    for c in strips:
        stripColor[c]['factor'] += 0.1
        if stripColor[c]['factor'] > 1:
            stripColor[c]['factor'] = 1.0
    colorSet(stripColor)


def ledDarker():
    for c in strips:
        stripColor[c]['factor'] -= 0.1
        if stripColor[c]['factor'] < 0:
            stripColor[c]['factor'] = 0.0
    colorSet(stripColor)


def ledCold():
    for c in strips:
        stripColor[c]['color'] = Color(255, 255, 255, 0)
    colorSet(stripColor)


def ledWarm():
    for c in strips:
        stripColor[c]['color'] = Color(0, 0, 0, 255)
    colorSet(stripColor)


def ledAll():
    for c in strips:
        stripColor[c]['color'] = Color(255, 255, 255, 255)
    colorSet(stripColor)


class LedHttpServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        print "GET request %s" % (self.path)

        cmd = self.path[1:]
        res = 'ignored'
        if cmd in commands:
            res = cmd + ' - ok'
            commands[cmd]['fct']()
        # if self.path == '/on':
        #     ledOn()
        #     res = 'OK'
        # elif self.path == '/off':
        #     ledOff()
        #     res = 'OK'
        # elif self.path == '/up':
        #     ledBright()
        #     res = 'OK'
        # elif self.path == '/down':
        #     ledDarker()
        #     res = 'OK'
        # elif self.path == '/warm':
        #     ledWarm()
        #     res = 'OK'
        # elif self.path == '/cold':
        #     ledCold()
        #     res = 'OK'
        # elif self.path == '/all':
        #     ledAll()
        #     res = 'OK'

        s = """<html><body>
        <div>Result: RESULT</div>
        <br/>
        COMMANDS
        <br/>
        </body></html>
        """

        ordered = []
        for c in commands:
            ordered.append(commands[c])

        ordered.sort(key=lambda x: x['order'])

        cmdList = ''
        for v in ordered:
            if v['key'].startswith('empty'):
                cmdList += '<br/>'
            cmdList += '<a href="/%s">%s</a><br/>' % (v['key'], v['name'],)

        self._set_headers()
        # self.wfile.write(b'<html><body></body></html>')
        self.wfile.write(bytearray(s.replace('RESULT', res).replace('COMMANDS', cmdList)))
        pass


commands = {
    'on':  {'name': 'An', 'order': 1, 'fct': ledOn},
    'off': {'name': 'Aus', 'order': 2, 'fct': ledOff},

    'empty_1': {'name': '', 'order': 4},

    'up':  {'name': 'Heller', 'order': 5, 'fct': ledBright},
    'down': {'name': 'Dunkler', 'order': 6, 'fct': ledDarker},

    'empty_9': {'name': '', 'order': 9},

    'warm': {'name': 'Warm', 'order': 10, 'fct': ledWarm},
    'cold': {'name': 'Kalt', 'order': 11, 'fct': ledCold},
    'all':  {'name': 'Alle', 'order': 12, 'fct': ledAll},

    'empty_19': {'name': '', 'order': 19},

    'red+': {'name': 'Red Up', 'order': 20, 'fct': ledRedMore},
    'redp': {'name': 'Red Up', 'order': 20, 'fct': ledRedMore},
    'red-': {'name': 'Red Down', 'order': 21, 'fct': ledRedLess},
    'redm': {'name': 'Red Down', 'order': 21, 'fct': ledRedLess},

    'green+': {'name': 'Green Up', 'order': 30, 'fct': ledGreenMore},
    'greenp': {'name': 'Green Up', 'order': 30, 'fct': ledGreenMore},
    'green-': {'name': 'Green Down', 'order': 31, 'fct': ledGreenLess},
    'greenm': {'name': 'Green Down', 'order': 31, 'fct': ledGreenLess},

    'blue+': {'name': 'Blue Up', 'order': 40, 'fct': ledBlueMore},
    'bluep': {'name': 'Blue Up', 'order': 40, 'fct': ledBlueMore},
    'blue-': {'name': 'Blue Down', 'order': 41, 'fct': ledBlueLess},
    'bluem': {'name': 'Blue Down', 'order': 41, 'fct': ledBlueLess},

    'empty_49': {'name': '', 'order': 49},

    'white+': {'name': 'White Up', 'order': 50, 'fct': ledWhiteMore},
    'whitep': {'name': 'White Up', 'order': 50, 'fct': ledWhiteMore},
    'white-': {'name': 'White Down', 'order': 51, 'fct': ledWhiteLess},
    'whitem': {'name': 'White Down', 'order': 51, 'fct': ledWhiteLess},

    'empty_59': {'name': '', 'order': 59},

    'red': {'name': 'Red', 'order': 60, 'fct': ledRed},
    'green': {'name': 'Green', 'order': 61, 'fct': ledGreen},
    'blue': {'name': 'Blue', 'order': 62, 'fct': ledBlue},

}

for c in commands:
    commands[c]['key'] = c


def initAll():
    global strip
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                              LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()


def hello(bot, update):
    logging.info('telegram command: %s' % (update.message.text,) )
    cmd = update.message.text[1:]
    res = 'ignored'
    if cmd in commands:
        res = 'ok'
        commands[cmd]['fct']()
    update.message.reply_text(
        'Hello {} - command {} -> {}'.format(update.message.from_user.first_name, cmd, res))


def initTelegram():
    global telegramToken
    global telegramTask

    src = None
    logging.info('searching for telegram token: %s' % (searchTelegramToken,) )
    for f in searchTelegramToken:
        if os.path.exists(f):
            src = f
            break

    if src is not None:
        with open(src, 'r') as fd:
            for line in fd:
                line = line.strip()
                if len(line) < 20:
                    continue
                if line[0] == '#':
                    continue

                telegramToken = line
                logging.info('found token for telegram')

    cmds = []
    for c in commands:
        if 'fct' not in commands[c]:
            continue
        cmds.append(c)

    if telegramToken is not None:
        from telegram.ext import Updater, CommandHandler
        updater = Updater(token=telegramToken)
        updater.dispatcher.add_handler(CommandHandler(cmds, hello))

        updater.start_polling(poll_interval=5)
        telegramTask = updater
    else:
        logging.info('no telegram token found --> no handling of messages')


def run():
    # Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    Handler = LedHttpServer

    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "serving at port", PORT
    httpd.serve_forever()
    logging.info('HTTP task killed')


# Main program logic follows:
if __name__ == '__main__':
    # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    initAll()
    initTelegram()

    ledOff()
    run()
    #colorSet(None, stripColor)

    if telegramTask is not None:
        logging.info('stopping telegram task')
        telegramTask.stop()

    pass
