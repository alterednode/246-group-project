import time
from RGB import RGB, num_leds
from ..electronics.LEDs import LEDControl

class CloudyAnimation:
    def __init__(self):
          self.leds = LEDControl()

    def cloud_frame(self):
            frame = blank_frame()
            for i in range(num_leds):
                frame[i]=RGB(60,60,90)
            return frame
    def cloud_animation(self):
            while True:
                frame = self.cloud_frame()
                self.leds.display(frame)

if __name__ == "__main__":
    ani = CloudyAnimation
    ani.cloud_animation()
      