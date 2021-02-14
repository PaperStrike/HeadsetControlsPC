import win32api
import hex_keycodes


class Dispatcher:
    def dispatch(self, press_key, is_long_press):
        target_key_name = self.event_keys[press_key][int(is_long_press)]
        target_vk = vars(hex_keycodes).get('VK_{key_name}'.format(key_name=target_key_name))

        win32api.keybd_event(target_vk, 0, 0, 0)

    def __init__(self, event_keys):
        self.event_keys = event_keys
