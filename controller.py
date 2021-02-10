# import sys
import timeit
import sounddevice as sd
from media_controls import dispatch_event

SAMPLE_RATE = 44100  # Sample rate for our input stream
BLOCK_SIZE = 40  # Number of samples before we trigger a processing callback
LONG_PRESS_DURATION_THRESHOLD = 0.8  # Number of seconds button should be held to register long press

AMOUNT_VALID_BLOCKS = 20

# CAPTURE_THRESHOLDS = [-0.6, 0.6]

# thresholds or press_values: [
#    press_amount, # initial
#    total_amount / amount_counted / press_amount, # average
#    largest_amount # largest
# ]
BUTTON_D_THRESHOLDS = [1.24, 1.17, 1.66]
BUTTON_B_THRESHOLDS = [0.77, 0.95, 1.57]
BUTTON_C_THRESHOLDS = [0.72, 0.88, 0.96]
NORMAL_THRESHOLD = 0.6

RECOVER_DURATION_THRESHOLD = 0.15
# RECOVER_DEVIATION_THRESHOLD = 0.001
RECOVER_FACTOR = 0.003


class HeadsetButtonController:
    def process_frames(self, in_data, _frames, _time, _status):
        # for x in in_data:
        #     if x[0] < CAPTURE_THRESHOLDS[0] or CAPTURE_THRESHOLDS[1] < x[0]:
        #         return

        diff_list = [(x[1] - x[0]) for x in in_data]

        # max_diff = max(diff_list)
        # min_diff = min(diff_list)
        # max_abs_diff = max(abs(max_diff), abs(min_diff))
        # deviation = max_diff - min_diff

        amount = sum([x if x > 0 else 0 for x in diff_list])

        # mean = sum(diff_list) / len(diff_list)
        # deviation_sum = 0
        # all_fit = True
        # for x in diff_list:
        #     if x < 0:
        #         all_fit = False
        #         break
        # if all_fit:
        #     deviation_sum = sum(abs(x - mean) for x in diff_list) * max_diff

        # diff_sum = sum(diff_list)
        # if diff_sum >= 0:
        #     sys.stdout.write("\r+%f" % sum(diff_list))
        #     sys.stdout.flush()
        # else:
        #     sys.stdout.write("\r%f" % sum(diff_list))
        #     sys.stdout.flush()
        # return

        if self.is_pressing:
            press_duration = timeit.default_timer() - self.press_time

            is_long_press = press_duration >= LONG_PRESS_DURATION_THRESHOLD

            if amount < self.press_amount * RECOVER_FACTOR:

                if self.recover_time == 0:
                    self.recover_time = timeit.default_timer()
                elif RECOVER_DURATION_THRESHOLD <= timeit.default_timer() - self.recover_time:
                    self.is_pressing = False
                    self.recover_time = 0
                    self.press_time = 0

                    self.generate_press_values()
                    print("%f %f %f %f" % (
                        self.press_values[0],
                        self.press_values[1],
                        self.press_values[2],
                        press_duration
                    ))

            else:
                self.recover_time = timeit.default_timer()

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
                    # if self.press_deviation_sum <= 0:
                    #     self.press_deviation_sum += 1
                    # else:
                    #     self.press_deviation_sum = deviation_sum
                    if self.amount_counted < AMOUNT_VALID_BLOCKS:
                        self.total_amount += amount
                        # self.total_deviation_sum += deviation_sum
                        self.amount_counted += 1
                        if self.largest_amount < amount:
                            self.largest_amount = amount
                    # if self.largest_deviation_sum < deviation_sum:
                    #     self.largest_deviation_sum = deviation_sum
                    # if self.smallest_deviation_sum > deviation_sum:
                    #     self.smallest_deviation_sum = deviation_sum

        else:
            if amount > NORMAL_THRESHOLD:
                self.is_pressing = True
                self.is_fired = False

                # self.press_deviation_sum = deviation_sum
                # self.total_deviation_sum = deviation_sum
                # self.largest_deviation_sum = deviation_sum
                # self.smallest_deviation_sum = deviation_sum

                self.press_amount = 0
                # self.press_deviation = deviation
                self.amount_counted = 0
                self.total_amount = amount
                self.largest_amount = amount
                self.press_values = [0]

                self.press_time = timeit.default_timer()

    def generate_press_values(self):
        if self.press_values[0] != 0:
            return
        self.press_values = [
            self.press_amount,
            self.total_amount / self.amount_counted / self.press_amount,
            self.largest_amount
        ]

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
        self.press_values = [0]

        self.press_time = 0
        self.recover_time = 0
