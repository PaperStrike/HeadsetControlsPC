"""Parse signals from headset button.

Distinguish button press and release event from normal voice
by comparing the two channels of the microphone.

"""

import sounddevice as sd
import timeit
import logging

from typing import List, Callable, Tuple

SAMPLE_RATE = 4410  # Sample rate for our input stream
BLOCK_SIZE = 21  # Number of samples before we trigger a processing callback

# diff: result of channel_2 - channel_1 in a sample
# amount: sum of positive diffs in a block

# Number of blocks we used to count average and largest amount
AMOUNT_VALID_BLOCKS = 3

# thresholds & press_values: (
#    total_amount / amount_counted,
#    largest_amount
# )
Threshold = float
Thresholds = Tuple[Threshold, ...]
BUTTON_D_THRESHOLDS: Thresholds = (0.46, 0.47)
BUTTON_B_THRESHOLDS: Thresholds = (0.35, 0.37)
BUTTON_C_THRESHOLDS: Thresholds = (0.30, 0.34)
NORMAL_THRESHOLD: Threshold = 0.3

# Max abs(diff) of button releasing
RELEASE_DIFF_THRESHOLD = 0.008
# Number of seconds diff should be within normal to register button release
RELEASE_SECONDS = 0.2

# Number of seconds button should be held to register long press.
LONG_PRESS_SECONDS = 0.6

status = {
    'is_pressing': False,
    'is_fired': False,

    'amount_counted': 0,
    'total_amount': 0.0,
    'largest_amount': 0.0,

    'press_key': '',
    'press_time': 0.0,
    'recover_time': 0.0
}

Listener = Callable[[str, bool], None]
_listeners: List[Listener] = []


def add_listener(listener: Listener):
    _listeners.append(listener)
    return listener


def remove_listener(listener: Listener):
    _listeners.remove(listener)


def _within_thresholds(values: Thresholds, thresholds: Thresholds):
    return all(values[i] <= max_val for i, max_val in enumerate(thresholds))


def _generate_press_key():
    if status['press_key']:
        return

    press_values: Thresholds = (
        status['total_amount'] / status['amount_counted'],
        status['largest_amount']
    )

    if not _within_thresholds(press_values, BUTTON_D_THRESHOLDS):
        status['press_key'] = 'A'
    elif not _within_thresholds(press_values, BUTTON_B_THRESHOLDS):
        status['press_key'] = 'D'
    elif not _within_thresholds(press_values, BUTTON_C_THRESHOLDS):
        status['press_key'] = 'B'
    else:
        status['press_key'] = 'C'


# noinspection PyUnusedLocal
def process_frames(indata, frames, time, stream_status):
    del frames, time, stream_status  # Unused.
    diff_list = [(x[1] - x[0]) for x in indata]

    amount = sum(x if x > 0 else 0 for x in diff_list)

    if status['is_pressing']:
        current_time = timeit.default_timer()

        press_seconds = status['recover_time'] - status['press_time']

        if all(abs(x) < RELEASE_DIFF_THRESHOLD for x in diff_list):
            if status['recover_time'] == 0.0:
                status['recover_time'] = current_time
            elif RELEASE_SECONDS <= current_time - status['recover_time']:
                status['is_pressing'] = False
                status['recover_time'] = 0.0
                status['press_time'] = 0

                _generate_press_key()

                logging.info('{0:.4f} {1:.4f} - {2:.3f} - {3}'.format(
                    status['total_amount'] / status['amount_counted'],
                    status['largest_amount'],
                    press_seconds,
                    status['press_key']
                ))

        else:
            status['recover_time'] = 0.0

        if not status['is_fired']:
            is_long_press = LONG_PRESS_SECONDS <= press_seconds

            if not status['is_pressing'] or is_long_press:
                status['is_fired'] = True

                _generate_press_key()

                for listener in _listeners:
                    listener(
                        status['press_key'],
                        is_long_press
                    )

            elif status['amount_counted'] < AMOUNT_VALID_BLOCKS:
                status['total_amount'] += amount
                status['amount_counted'] += 1
                if status['largest_amount'] < amount:
                    status['largest_amount'] = amount

    else:
        if amount > NORMAL_THRESHOLD:
            status['is_pressing'] = True
            status['is_fired'] = False

            status['amount_counted'] = 0
            status['total_amount'] = 0.0
            status['largest_amount'] = 0.0

            status['press_key'] = ''
            status['press_time'] = timeit.default_timer()
            status['recover_time'] = 0.0


stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    channels=2,
    callback=process_frames
)
