"""Parse signals from headset button.

Distinguish button press and release event from normal voice
by comparing the two channels of the microphone.

"""

import sounddevice as _sd
import logging
from time import perf_counter

from typing import List, Callable, Union, Optional

SAMPLE_RATE: int = 1000  # Sample rate for our input stream
BLOCK_SIZE: int = 10  # Number of samples before a processing callback

# diff: result of channel_2 - channel_1 in a sample
# threshold: diff
Threshold = float
BUTTON_B_THRESHOLD: Threshold = 0.060
BUTTON_C_THRESHOLD: Threshold = 0.022
NORMAL_THRESHOLD: Threshold = 0.015

RELEASE_THRESHOLD: Threshold = 0.035

ListenerCallback = Callable[[str, float], None]
ListenerData = dict[str, Union[list, None, bool, float]]
Listener = tuple[ListenerCallback, ListenerData]

_listeners: dict[str, List[Listener]] = {
    'press': [],
    'release': []
}


def add_listener(
        event_type: str,
        callback: ListenerCallback,
        options: Optional[ListenerData] = None
) -> Listener:
    data: ListenerData = options if options is not None else {}

    if 'keys' not in data:
        data['keys'] = None

    if data.get('once', False):
        data['fired'] = False

        def once_callback(*args):
            nonlocal event_type, listener
            _listeners[event_type].remove(listener)
            callback(*args)
            listener[1]['fired'] = True

        listener = (once_callback, data)
    else:
        listener = (callback, data)

    _listeners[event_type].append(listener)

    return listener


def remove_listener(event_type: str, listener: Listener):
    _listeners[event_type].remove(listener)


def _matched_key(keys: Optional[tuple]):
    return keys is None or _press_key in keys


def _send_event(event_type: str):
    global _press_key, _press_time
    for callback, data in _listeners[event_type]:
        if _matched_key(data['keys']):
            callback(_press_key, _press_time)


# Button status.
_is_pressing: bool = False

_press_diff: float = 0
_max_diff: float = 0

_press_key: str = ''
_press_time: float = 0


def _generate_press_key():
    global _press_key
    global _press_diff, _max_diff

    if _press_key:
        return

    key_value: float = _press_diff

    if key_value <= BUTTON_C_THRESHOLD:
        _press_key = 'C'
    elif key_value <= BUTTON_B_THRESHOLD:
        _press_key = 'B'
    else:
        _press_key = 'A'


# noinspection PyUnusedLocal
def _process_frames(indata, frames, time, stream_status):
    del frames, time, stream_status  # Unused.

    max_diff = max(x[1] - x[0] for x in indata)
    min_sample = min(x[0] for x in indata)

    global _is_pressing
    global _press_diff, _max_diff
    global _press_key, _press_time

    if _is_pressing:
        passed_seconds = perf_counter() - _press_time
        if passed_seconds <= 0.1:
            if _max_diff < max_diff:
                _max_diff = max_diff
        else:
            if not _press_key:
                _generate_press_key()
                _send_event('press')
            if min_sample < -0.36:
                _is_pressing = False
                _send_event('release')

                logging.info('{:.4f} {:.4f} - {:.3f} - {}'.format(
                    _press_diff,
                    _max_diff,
                    passed_seconds,
                    _press_key
                ))

    else:
        if (max_diff > NORMAL_THRESHOLD
                and (min_sample >= -0.5 or all(x[0] > 0.5 for x in indata))):
            _is_pressing = True

            _press_diff = max_diff
            _max_diff = max_diff

            _press_key = ''
            _press_time = perf_counter()


stream = _sd.InputStream(
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    channels=2,
    callback=_process_frames
)
