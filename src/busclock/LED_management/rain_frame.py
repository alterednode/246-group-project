import time
from RGB import RGB,blank_frame
from display import display
 
 class RainAnimation:
    def rain_frame(self, step): 
        if step ==1:
            frame = blank_frame()
            frame[3]=RGB(0,0,100)
            frame[7]=RGB(0,0,100)
            frame[11]=RGB(0,0,100)
            frame[18]=RGB(0,0,100)
            frame[22]=RGB(0,0,100)
            frame[30]=RGB(0,0,100)
            return frame
    
        elif step ==2:
            frame = blank_frame()

            frame[19]=RGB(0,0,100)
            frame[29]=RGB(0,0,100)
            frame[54]=RGB(0,0,100)
            frame[40]=RGB(0,0,100)
            frame[27]=RGB(0,0,100)
            frame[69]=RGB(0,0,100)
            return frame
    
        elif step ==3:
            frame = blank_frame()
            frame[42]=RGB(0,0,100)
            frame[71]=RGB(0,0,100)
            frame[95]=RGB(0,0,100)
            frame[55]=RGB(0,0,100)
            frame[49]=RGB(0,0,100)
            frame[83]=RGB(0,0,100)
            return frame
        elif step ==4:
            frame = blank_frame()
            frame[51]=RGB(0,0,100)
            frame[81]=RGB(0,0,100)
            frame[94]=RGB(0,0,100)
            frame[73]=RGB(0,0,100)
            frame[98]=RGB(0,0,100)
            return frame
        elif step ==5:
            frame = blank_frame()
            frame[80]=RGB(0,0,100)
            frame[100]=RGB(0,0,100)
            frame[76]=RGB(0,0,100)
#rain animation
    def rain_animation(self):
        while True:
            for(step) in range(1,5):
                frame = self.rain_frame(step)
                display(frame)
                time.sleep(0.2)
    
