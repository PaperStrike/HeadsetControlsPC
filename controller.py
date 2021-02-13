import timeit
import logging
import sounddevice as sd
from event_dispatcher import dispatch_event

SAMPLE_RATE = 44100  # Sample rate for our input stream
BLOCK_SIZE = 40  # Number of samples before we trigger a processing callback
LONG_PRESS_DURATION_THRESHOLD = 0.6  # Number of seconds button should be held to register long press

AMOUNT_VALID_BLOCKS = 20  # Number of blocks we used to count average and largest amount

# diff: channel_2 - channel_1 in a sample
# amount: sum of positive diffs in a block
#
# thresholds & press_values: [
#    press_amount,
#    total_amount / amount_counted / press_amount,
#    largest_amount
# ]
BUTTON_D_THRESHOLDS = [1.24, 1.17, 1.66]
BUTTON_B_THRESHOLDS = [0.78, 0.96, 0.81]
BUTTON_C_THRESHOLDS = [0.72, 0.88, 0.74]
NORMAL_THRESHOLD = 0.6

RELEASE_DURATION_THRESHOLD = 0.2  # Number of seconds diff should be within normal to register button release
RELEASE_DIFF_THRESHOLD = 0.01  # Max diff of button releasing


class HeadsetButtonController:
    def process_frames(self, indata, _frames, _time, _status):
        diff_list = [(x[1] - x[0]) for x in indata]

        amount = sum([x if x > 0 else 0 for x in diff_list])

        if self.is_pressing:
            press_duration = timeit.default_timer() - self.press_time

            is_long_press = press_duration >= LONG_PRESS_DURATION_THRESHOLD

            if all([abs(x) < RELEASE_DIFF_THRESHOLD for x in diff_list]):
                if self.recover_time == 0:
                    self.recover_time = timeit.default_timer()
                elif RELEASE_DURATION_THRESHOLD <= timeit.default_timer() - self.recover_time:
                    self.is_pressing = False
                    self.recover_time = 0
                    self.press_time = 0

                    self.generate_press_values()
                    logging.info('%f %f %f %f' % (
                        self.press_values[0],
                        self.press_values[1],
                        self.press_values[2],
                        press_duration
                    ))

            else:
                self.recover_time = 0

            if not self.is_fired:
                if not self.is_pressing or is_long_press:
                    self.is_fired = True

                    if not self.is_fit_press_values(thresholds=BUTTON_D_THRESHOLDS):
                        press_key = 'A'
                    elif not self.is_fit_press_values(thresholds=BUTTON_B_THRESHOLDS):
                        press_key = 'D'
                    elif not self.is_fit_press_values(thresholds=BUTTON_C_THRESHOLDS):
                        press_key = 'B'
                    else:
                        press_key = 'C'

                    dispatch_event(press_key=press_key, is_long_press=is_long_press)

                else:
                    if self.press_amount == 0:
                        self.press_amount = 1
                    elif self.press_amount == 1:
                        self.press_amount = amount
                    if self.amount_counted < AMOUNT_VALID_BLOCKS:
                        self.total_amount += amount
                        self.amount_counted += 1
                        if self.largest_amount < amount:
                            self.largest_amount = amount

        else:
            if amount > NORMAL_THRESHOLD:
                self.is_pressing = True
                self.is_fired = False

                self.press_amount = 0
                self.amount_counted = 0
                self.total_amount = amount
                self.largest_amount = amount
                self.press_values.clear()

                self.press_time = timeit.default_timer()

    def generate_press_values(self):
        if self.press_values:
            return
        self.press_values.extend((
            self.press_amount,
            self.total_amount / self.amount_counted / self.press_amount,
            self.largest_amount
        ))

    def is_fit_press_values(self, thresholds):
        self.generate_press_values()
        for index in range(len(thresholds)):
            if self.press_values[index] > thresholds[index]:
                return False
        return True

    def __init__(self):
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=2,
            callback=self.process_frames
        )
        self.stream.start()

        self.is_pressing = False
        self.is_fired = False

        self.press_amount = 0
        self.amount_counted = 0
        self.total_amount = 0
        self.largest_amount = 0
        self.press_values = []

        self.press_time = 0
        self.recover_time = 0
