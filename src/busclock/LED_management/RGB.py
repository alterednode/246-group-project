import time
 
num_leds = 106
class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
def blank_frame():
    return [RGB(0,0,0) for _ in range(num_leds)]



    
