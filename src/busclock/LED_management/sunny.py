from RGB import RGB,blank_frame
from display import display
class SunnyAnimation:
    def sun_frame(self):
        frame = blank_frame()
        for i in range(num_leds):
            frame[i]=RGB(100,100,0)
        return frame
    def sun_animation(self):
        while True:
            frame = self.sun_frame()
            display(frame)