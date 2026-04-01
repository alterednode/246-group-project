import time 
try:
    import RPi.GPIO as GPIO
except ImportError:
    import Mock.GPIO as GPIO

class MotorControl:
    # in1, in2, in3, in4
    pins = [18, 23, 24, 25]
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
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def step(self, steps):
        step = -2 if steps < 0 else 2
        for i in range(abs(steps)):
            self.motor_step_counter = self.motor_step_counter + step
            for pin in range(0, len(self.pins)):
                GPIO.output(self.pins[pin], self.step_sequence[self.motor_step_counter % 8][pin])
            time.sleep(0.002)

    def cleanup(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)
        GPIO.cleanup()

if __name__ == "__main__":
    motor = MotorControl()
    steps = 150
    try:
        motor.step(steps)
    except KeyboardInterrupt:
        motor.cleanup()
        exit(1)
    motor.cleanup()
