import timeit
import logging
import sounddevice as sd

SAMPLE_RATE = 11025  # Sample rate for our input stream
BLOCK_SIZE = 10  # Number of samples before we trigger a processing callback

# diff: result of channel_2 - channel_1 in a sample
# amount: sum of positive diffs in a block
AMOUNT_VALID_BLOCKS = 5  # Number of blocks we used to count average and largest amount

# thresholds & press_values: [
#    press_amount,
#    total_amount / amount_counted,
#    largest_amount
# ]
BUTTON_D_THRESHOLDS = [0.323, 0.373, 0.341]
BUTTON_B_THRESHOLDS = [0.195, 0.226, 0.199]
BUTTON_C_THRESHOLDS = [0.177, 0.207, 0.182]
NORMAL_THRESHOLD = 0.15

RELEASE_DIFF_THRESHOLD = 0.01  # Max abs(diff) of button releasing
RELEASE_SECONDS = 0.2  # Number of seconds diff should be within normal to register button release


class HeadsetButtonController:
    def process_frames(self, indata, _frames, _time, _status):
        diff_list = [(x[1] - x[0]) for x in indata]

        amount = sum([x if x > 0 else 0 for x in diff_list])

        if self.is_pressing:
            press_seconds = timeit.default_timer() - self.press_time

            is_long_press = press_seconds >= self.long_press_seconds

            if all([abs(x) < RELEASE_DIFF_THRESHOLD for x in diff_list]):
                if self.recover_time == 0:
                    self.recover_time = timeit.default_timer()
                elif RELEASE_SECONDS <= timeit.default_timer() - self.recover_time:
                    self.is_pressing = False
                    self.recover_time = 0
                    self.press_time = 0

                    self.generate_press_values()
                    logging.info('%f %f %f %f' % (
                        self.press_values[0],
                        self.press_values[1],
                        self.press_values[2],
                        press_seconds
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

                    self.event_dispatcher.dispatch(press_key=press_key, is_long_press=is_long_press)

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
            self.total_amount / self.amount_counted,
            self.largest_amount
        ))

    def is_fit_press_values(self, thresholds):
        self.generate_press_values()
        for index in range(len(thresholds)):
            if self.press_values[index] > thresholds[index]:
                return False
        return True

    # long_press_seconds: Number of seconds button should be held to register long press
    def __init__(self, long_press_seconds, event_dispatcher):
        self.long_press_seconds = long_press_seconds
        self.event_dispatcher = event_dispatcher
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
