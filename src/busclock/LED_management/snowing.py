import time
from RGB import RGB, blank_frame
from ..electronics.LEDs import LEDControl

class SnowAnimation:
    def __init__(self):
        self.leds = LEDControl()

    def snow_frame(self,step):
        if step ==1:
            frame = blank_frame()
            frame[6]=RGB(100,100,100)
            frame[2]=RGB(100,100,100)
            frame[11]=RGB(100,100,100)
            frame[22]=RGB(100,100,100)
            frame[18]=RGB(100,100,100)
            frame[25]=RGB(100,100,100)
            frame[29]=RGB(100,100,100)
            return frame
        
        elif step ==2:
            frame = blank_frame()

            frame[28]=RGB(100,100,100)
            frame[20]=RGB(100,100,100)
            frame[40]=RGB(100,100,100)
            frame[44]=RGB(100,100,100)
            frame[38]=RGB(100,100,100)
            frame[46]=RGB(100,100,100)
            frame[69]=RGB(100,100,100)
            return frame
        
        elif step ==3:
            frame = blank_frame()
            frame[53]=RGB(100,100,100)
            frame[42]=RGB(100,100,100)
            frame[55]=RGB(100,100,100)
            frame[73]=RGB(100,100,100)
            frame[65]=RGB(100,100,100)
            frame[75]=RGB(100,100,100)
            frame[81]=RGB(100,100,100)
            return frame
        elif step ==4:
            frame = blank_frame()
            frame[79]=RGB(100,100,100)
            frame[50]=RGB(100,100,100)
            frame[94]=RGB(100,100,100)
            frame[76]=RGB(100,100,100)
            frame[87]=RGB(100,100,100)
            frame[99]=RGB(100,100,100)
            return frame
        elif step ==5:
            frame = blank_frame()
            frame[106]=RGB(100,100,100)
            frame[80]=RGB(100,100,100)
            frame[93]=RGB(100,100,100)

            return frame
       
#snow animation 
    def snow_animation(self):
        while True:
            for(step) in range(1,5):
                frame = self.snow_frame(step)
                self.leds.display(frame)
                time.sleep(0.5)
             

if __name__ == "__main__":
    ani = SnowAnimation
    ani.snow_animation()