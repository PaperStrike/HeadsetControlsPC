from controller import HeadsetButtonController
from threading import Event

controller = HeadsetButtonController()

while True:
    Event().wait()
