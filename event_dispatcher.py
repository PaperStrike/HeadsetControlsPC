import win32api

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1


def dispatch_event(press_key, is_long_press):
    target_vk = {
        'A': [
            VK_MEDIA_PLAY_PAUSE,
            VK_MEDIA_PLAY_PAUSE
        ],
        'D': [
            VK_MEDIA_PLAY_PAUSE,
            VK_MEDIA_PLAY_PAUSE
        ],
        'B': [
            VK_VOLUME_UP,
            VK_MEDIA_NEXT_TRACK
        ],
        'C': [
            VK_VOLUME_DOWN,
            VK_MEDIA_PREV_TRACK
        ]
    }[press_key][int(is_long_press)]

    win32api.keybd_event(target_vk, 0, 0, 0)
