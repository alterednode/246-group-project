import board
import neopixel
import time

class LEDControl:
    LEDs = []

    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D21, 106, auto_write=False)
    
    def display(self, frame):
        for i in frame:
            pixels[i] = (0, 0, 0)

if __name__ == "__main__":
    pixels = neopixel.NeoPixel(board.D21, 106, auto_write=False)
    try:
        while(1):
            for i in range(105):
                # pixels.fill((0, 0, 0))
                pixels[i] = (0, 0, 50)
                pixels[i + 1] = (50, 0, 0)
                pixels.show()
                time.sleep(0.05)
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        exit(1)
    