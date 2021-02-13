import argparse
import logging.handlers
from threading import Event

from controller import HeadsetButtonController

parser = argparse.ArgumentParser(description='Start headset controls.')
parser.add_argument('-l', '--log', action='store_true', help='save log to file.')

args = parser.parse_args()

logLevel = logging.DEBUG
logFileName = 'debug.log'
logFileMaxBytes = 4 * 1024
logToFile = args.log

logHandlers = [logging.StreamHandler()]
if logToFile:
    logFileHandler = logging.handlers.RotatingFileHandler(
        filename=logFileName,
        maxBytes=logFileMaxBytes,
        backupCount=1,
        encoding='utf-8'
    )
    logHandlers.append(logFileHandler)

# noinspection PyArgumentList
logging.basicConfig(
    handlers=logHandlers,
    format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logLevel
)
logging.info('Started.')

controller = HeadsetButtonController()

while True:
    Event().wait()
