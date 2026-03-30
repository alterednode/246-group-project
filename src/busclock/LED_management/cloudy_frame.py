import time
from RGB import RGB,blank_frame
from display import display

class CloudyAnimation:
        def cloud_frame(self):
                frame = blank_frame()
                for i in range(num_leds):
                    frame[i]=RGB(60,60,90)
                return frame
def cloud_animation(self):
        while True:
            frame = self.cloud_frame()
            display(frame)


      