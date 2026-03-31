import RPi.GPIO as GPIO
import time

class displayControl:
                            #abcdefg
    number_mapping = {"0": 0b1111110,
                      "1": 0b0110000,
                      "2": 0b1101101,
                      "3": 0b1111001,
                      "4": 0b0110011,
                      "5": 0b1011011,
                      "6": 0b1011111,
                      "7": 0b1110000,
                      "8": 0b1111111,
                      "9": 0b1111011
                      }
    # abcdefg d1 d2 d3 d4
    pins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def __init__(self):
        GPIO.setmode( GPIO.BCM )
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        for digit in self.pins[-3:]:
            GPIO.output(pin, GPIO.HIGH)

    # 4 digit numbers 0-9 
    def displayDigits(self, string):
        for i in range(4):
            pattern = self.number_mapping[string[i]]
            mask = 1
            GPIO.output(self.pins[7 + i], GPIO.LOW)
            for segment in range(7):
                GPIO.output(self.pins[segment], GPIO.HIGH)
            time.sleep(0.01)
            for segment in range(7):
                GPIO.output(self.pins[segment], GPIO.LOW)
            GPIO.output(self.pins[7 + i], GPIO.HIGH)
