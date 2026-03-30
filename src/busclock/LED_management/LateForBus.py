from RGB import RGB,blank_frame,num_leds
from display import display
import time
def lateForBus_frame(self):
        frame= blank_frame()
        for i in range(num_leds):
            frame[i]=RGB(100,3,3)
        return frame
def lateForBus_animation(self):
    while True:
        frame = self.lateForBus_frame()
        display(frame)
        time.sleep(0.5)
        display(blank_frame())
        time.sleep(0.5)