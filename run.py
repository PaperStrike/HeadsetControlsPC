import argparse
import json
import logging.handlers
from threading import Event

from controller import HeadsetButtonController
from event_dispatcher import Dispatcher

# Command line argument parsing.
argParser = argparse.ArgumentParser(description='Start headset controls.')
argParser.add_argument('-l', '--log', action='store_true', help='save log to file.')

args = argParser.parse_args()

# Load Settings.
settingsFile = 'settings.json'
settings = json.load(open(settingsFile, 'r'))

# Log tuning.
logToFile = args.log
logSettings = settings['log']
logFileSettings = logSettings['file']

logHandlers = [logging.StreamHandler()]
if logToFile:
    logFileHandler = logging.handlers.RotatingFileHandler(
        filename=logFileSettings['name'],
        maxBytes=logFileSettings['max-bytes'],
        backupCount=logFileSettings['backup-count'],
        encoding=logFileSettings['encoding']
    )
    logHandlers.append(logFileHandler)

# noinspection PyArgumentList
logging.basicConfig(
    handlers=logHandlers,
    format=logSettings['format'],
    datefmt=logSettings['date-format'],
    level=getattr(logging, logSettings['level'].upper(), 0)
)
logging.info('Started.')

# Main
dispatcher = Dispatcher(settings['event-keys'])
controller = HeadsetButtonController(
    long_press_seconds=settings['long-press-seconds'],
    event_dispatcher=dispatcher
)

Event().wait()
