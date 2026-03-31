import board
import neopixel
import time

class LEDControl:
    # LEDs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 45, 44, 43, 42, 41, 40, 39, 38, 46, 47, 48, 49, 50, 56, 57, 58, 59, 60, 61, 62, 63, 51, 52, 53, 54, 55, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 101, 100, 99, 98, 97, 106, 105, 104, 103, 102, 96, 95, 94, 93, 92, 91, 0]

    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D21, 106, auto_write=False)
    
    def display(self, frame):
        for i in range(len(frame)):
            colour = frame[i]
            self.pixels[i] = (colour.r, colour.g, colour.b)
        self.pixels.show()

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
    