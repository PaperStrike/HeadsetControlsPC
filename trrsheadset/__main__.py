"""For command line use.

Parse command parameters and start runner immediately.

"""

import argparse
import logging.handlers

from trrsheadset import runner

# Command line argument parsing.
_arg_parser = argparse.ArgumentParser(description='Start headset controls.')
_arg_parser.add_argument(
    '-l', '--log',
    action='store_true',
    help='save log to file.'
)
_arg_parser.add_argument(
    '--no-hotkey',
    action='store_true',
    help='disable hotkeys.'
)

ARGS = _arg_parser.parse_args()

# Log tuning.
LOG_SETTINGS = {
    'file': {
        'name': 'debug.log',
        'max-bytes': 4096,
        'backup-count': 1,
        'encoding': 'utf-8'
    },
    'format':
        '%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.8s] %(message)s',
    'date-format': '%m-%d %H:%M:%S',
    'level': 'debug'
}
LOG_FILE_SETTINGS = LOG_SETTINGS['file']


def main():
    log_handlers = [logging.StreamHandler()]
    if ARGS.log:
        log_handlers.append(logging.handlers.RotatingFileHandler(
            filename=LOG_FILE_SETTINGS['name'],
            maxBytes=LOG_FILE_SETTINGS['max-bytes'],
            backupCount=LOG_FILE_SETTINGS['backup-count'],
            encoding=LOG_FILE_SETTINGS['encoding']
        ))

    # noinspection PyArgumentList
    logging.basicConfig(
        handlers=log_handlers,
        format=LOG_SETTINGS['format'],
        datefmt=LOG_SETTINGS['date-format'],
        level=getattr(logging, LOG_SETTINGS['level'].upper(), 0)
    )

    runner.start(use_hotkey=not ARGS.no_hotkey)


if __name__ == '__main__':
    main()
