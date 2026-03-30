import time
 
num_leds = 106
class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class WeatherAnimation:
   
   def blank_frame(self):
        return [RGB(0,0,0) for _ in range(num_leds)]
    def animation_off(self):
        frame = self.blank_frame()
        return frame



    
