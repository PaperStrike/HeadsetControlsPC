"""Keyboard support for headset controls.

Reflects changes in Python to key events in platform.
Besides, register keyboard shortcuts.

"""

import logging
from typing import Callable, Optional, Any

from queue import Queue
import keyboard
import sys
from threading import Thread

from trrsheadset import controller

# Main
_message_queue = Queue()


def _send_message(identifier, message: Optional[Any] = None):
    _message_queue.put((identifier, message))


CONTROLLER_SETTINGS = {
    'event-keys': {
        'A': [
            'play/pause media',
            'play/pause media'
        ],
        'D': [
            'play/pause media',
            'play/pause media'
        ],
        'B': [
            'volume up',
            'next track'
        ],
        'C': [
            'volume down',
            'previous track'
        ]
    }
}

_controller_listener: Optional[Callable[[str, bool], None]] = None


def _controller_callback(controller_settings, press_key, is_long_press):
    event_keys = controller_settings['event-keys']
    target_key = event_keys[press_key][int(is_long_press)]
    _send_message('controller', target_key)


def register_controller(controller_settings):
    global _controller_listener
    if _controller_listener is not None:
        raise Exception('Controller has already been registered.')
    _controller_listener = controller.add_listener(
        lambda *args: _controller_callback(controller_settings, *args)
    )


def unregister_controller():
    global _controller_listener
    if _controller_listener is None:
        raise Exception('Controller has not been registered yet.')
    controller.remove_listener(_controller_listener)
    _controller_listener = None


# Bind hotkeys.
HOTKEY_SETTINGS = {
    'appetizer': 'ctrl+shift+h',
    'suppress': 1,
    'timeout': 1,
    'bindings': {
        'play/pause': 'p',
        'exit': 'e'
    }
}
HOTKEY_BINDINGS = HOTKEY_SETTINGS['bindings']

_hotkey_listener = None


def _hotkey_callback(hotkey_settings):
    listeners = []

    def cleanup():
        while listeners:
            keyboard.remove_hotkey(listeners.pop())

    def dispatch(arg):
        _send_message('hotkey', arg)
        cleanup()

    for action_name, key_name in hotkey_settings['bindings'].items():
        if not key_name:
            continue
        listeners.append(keyboard.add_hotkey(
            hotkey=key_name,
            callback=dispatch,
            args=(action_name,),
            suppress=True
        ))

    keyboard.call_later(cleanup, delay=hotkey_settings['timeout'])


def register_hotkey(hotkey_settings):
    global _hotkey_listener
    if _hotkey_listener is not None:
        raise Exception('Hotkey has already been registered.')
    _hotkey_listener = keyboard.add_hotkey(
        hotkey=hotkey_settings['appetizer'],
        callback=lambda: _hotkey_callback(hotkey_settings),
        suppress=bool(hotkey_settings['suppress'])
    )


def unregister_hotkey():
    global _hotkey_listener
    if _hotkey_listener is None:
        raise Exception('Hotkey has not been registered yet.')
    keyboard.remove_hotkey(_hotkey_listener)
    _hotkey_listener = None


# Messages.
_message_reader_thread: Optional[Thread] = None


def _process_message(identifier, message):
    if identifier == 'controller':
        target_key = message

        keyboard.send(target_key)

    elif identifier == 'hotkey':
        action = message

        if action == 'play/pause':
            if controller.stream.active:
                logging.info('Paused by hotkey.')
                controller.stream.abort()
            else:
                logging.info('Continued by hotkey.')
                controller.stream.start()

        elif action == 'exit':
            logging.info('Terminated by hotkey.')
            sys.exit(0)


def _message_reader():
    while True:
        identifier, message = _message_queue.get()
        if identifier == 'main':
            action = message
            if action == 'stop':
                return
        else:
            _process_message(identifier, message)


def start_reading_messages():
    global _message_reader_thread
    if _message_reader_thread is not None:
        raise Exception('Message reader has already started.')
    _message_reader_thread = Thread(target=_message_reader, name='Messenger')
    _message_reader_thread.start()


def stop_reading_messages():
    global _message_reader_thread
    if _message_reader_thread is None:
        raise Exception('Message reader has not started yet.')
    _send_message('main', 'stop')
    _message_reader_thread = None


# def keep_running():
#     if _message_reader_thread is None:
#         raise Exception('Message reader has not started yet.')
#     _message_reader_thread.join()


def start(
        controller_settings: Optional[dict] = None,
        use_hotkey: bool = True,
        hotkey_settings: Optional[dict] = None
):
    if controller_settings is None:
        controller_settings = CONTROLLER_SETTINGS
    if hotkey_settings is None:
        hotkey_settings = HOTKEY_SETTINGS

    logging.info('Started.')

    register_controller(controller_settings)

    if use_hotkey:
        register_hotkey(hotkey_settings)

    controller.stream.start()

    start_reading_messages()
