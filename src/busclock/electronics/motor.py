from filecmp import dircmp
import time 
import RPi.GPIO as GPIO

class MotorControl:
    secondsPerStep = 0
    currentShownTime = 0
    # in1, in2, in3, in4
    pins = [18, 23, 24, 25]
    step_count = 4096
    step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]

    motor_step_counter = 0

    def __init__(self):
        GPIO.setmode( GPIO.BCM )
        GPIO.setup(self.pins[0], GPIO.OUT)
        GPIO.setup(self.pins[1], GPIO.OUT)
        GPIO.setup(self.pins[2], GPIO.OUT)
        GPIO.setup(self.pins[3], GPIO.OUT)

        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)

    def step(self, dir):
        if (dir):
            self.motor_step_counter = (self.motor_step_counter + 1) % 8 
        else:
            self.motor_step_counter = (self.motor_step_counter - 1) % 8
        
        for pin in range(0, len(self.pins)):
            GPIO.output(self.pins[pin], self.step_sequence[self.motor_step_counter][pin] )

    def setDisplayedTime(self, time):
        pass
    def addTime(self):
        pass

    def cleanup(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)
        GPIO.cleanup()

if __name__ == "__main__":
    motor = MotorControl()
    dir = 0
    try:
        while(1):
            for i in range(0, 4096):
                motor.step(dir)
                time.sleep(0.002)
            time.sleep(5)
            dir = ~dir
    except KeyboardInterrupt:
        motor.cleanup()
        exit(1)
