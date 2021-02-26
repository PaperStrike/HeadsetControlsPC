"""Keyboard support for headset controls.

Reflects changes in Python to key events in platform.
Besides, register keyboard shortcuts.

"""

from queue import Queue
import logging
import sys
from threading import Thread, Timer
from typing import Optional, Any

import keyboard

from trrsheadset import controller
from trrsheadset.controller import (
    Listener as ControllerListener,
)


_message_queue = Queue()


def _send_message(identifier, message: Optional[Any] = None):
    _message_queue.put((identifier, message))


CONTROLLER_SETTINGS = {
    'long-press-timeout': 0.4,
    'double-press-timeout': 0.4,
    'event-keys': {
        'A': [
            'play/pause media',
            'play/pause media',
            'volume mute'
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

_last_press = {
    'key': '',
    'time': 0.,
}
_controller_listener: Optional[ControllerListener] = None


# noinspection PyUnusedLocal
def _controller_callback(
        settings,
        press_key: str,
        press_time: float
) -> None:
    event_keys: dict[str, list[str]] = settings['event-keys']
    double_press_timeout: float = settings['double-press-timeout']
    long_press_timeout: float = settings['long-press-timeout']

    last_press_key = _last_press['key']
    if (last_press_key
            and len(event_keys[last_press_key]) > 2
            and press_time - _last_press['time']
            <= double_press_timeout):
        _send_message(
            'controller',
            event_keys[last_press_key][2])

    else:
        matched_keys = event_keys[press_key]

        def dispatcher():
            nonlocal press_key
            is_long_press: bool = not long_press_listener[1]['fired']

            _send_message(
                'controller',
                matched_keys[int(is_long_press)])

        long_press_listener = controller.add_listener(
            event_type='release',
            callback=lambda *args: None,
            options={
                'keys': [press_key],
                'once': True
            }
        )

        Timer(
            interval=long_press_timeout,
            function=dispatcher
        ).start()

    _last_press['key'] = press_key
    _last_press['time'] = press_time


def register_controller(settings):
    global _controller_listener
    if _controller_listener is not None:
        raise Exception('Controller has already been registered.')
    _controller_listener = controller.add_listener(
        event_type='press',
        callback=lambda *args: _controller_callback(settings, *args),
        options={}
    )


def unregister_controller():
    global _controller_listener
    if _controller_listener is None:
        raise Exception('Controller has not been registered yet.')
    controller.remove_listener('hold', _controller_listener)
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


def _hotkey_callback(settings):
    listeners = []

    def cleanup():
        while listeners:
            keyboard.remove_hotkey(listeners.pop())

    def dispatch(arg):
        _send_message('hotkey', arg)
        cleanup()

    for action_name, key_name in settings['bindings'].items():
        if not key_name:
            continue
        listeners.append(keyboard.add_hotkey(
            hotkey=key_name,
            callback=dispatch,
            args=(action_name,),
            suppress=True
        ))

    Timer(interval=settings['timeout'], function=cleanup).start()


def register_hotkey(settings):
    global _hotkey_listener
    if _hotkey_listener is not None:
        raise Exception('Hotkey has already been registered.')
    _hotkey_listener = keyboard.add_hotkey(
        hotkey=settings['appetizer'],
        callback=lambda: _hotkey_callback(settings),
        suppress=bool(settings['suppress'])
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
        use_hotkey: bool = False,
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
