import sys
from pathlib import Path
import threading
from time import sleep

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import busclock.LED_management.test as test
from busclock.LED_management.RGB import blank_frame
from busclock.clock_mapping import time_delta_to_steps
from busclock.electronics.motor import MotorControl
from busclock.electronics.LEDs import LEDControl

if __name__ == "__main__":
    # main()

    motor = MotorControl()
    leds = LEDControl()
    current_hour = 12
    current_minute = 0
    led_thread = None
    while(1):
        weather = input("Weather: ")
        time = input("Time: ").split(":")
        led_thread = threading.Thread(target=test.led, args=(weather, leds), kwargs={"duration_seconds": 5.0})
        led_thread.start()

        target_hour = int(time[0])
        target_minute = int(time[1])

        steps = time_delta_to_steps(current_hour, current_minute, target_hour, target_minute)
        motor.step(steps[0] * (1 if steps[1] else -1))


        
    




