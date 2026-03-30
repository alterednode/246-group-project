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
            frame[15]=RGB(0,0,100)
            frame[23]=RGB(0,0,100)
            return frame
    
        elif step ==2:
            frame = blank_frame()

            frame[5]=RGB(0,0,100)

            frame[40]=RGB(0,0,100)
            frame[31]=RGB(0,0,100)
            frame[60]=RGB(0,0,100)
            frame[49]=RGB(0,0,100)
            frame[45]=RGB(0,0,100)
            return frame
    
        elif step ==3:
            frame = blank_frame()
            frame[29]=RGB(0,0,100)
            frame[1]=RGB(0,0,100)
            frame[14]=RGB(0,0,100)
            frame[22]=RGB(0,0,100)
            frame[25]=RGB(0,0,100)

            frame[57]=RGB(0,0,100)
            frame[70]=RGB(0,0,100)
            frame[97]=RGB(0,0,100)
            frame[65]=RGB(0,0,100)
            frame[87]=RGB(0,0,100)
            return frame
        elif step ==4:
            frame = blank_frame()
            frame[68]=RGB(0,0,100)
            frame[39]=RGB(0,0,100)
            frame[60]=RGB(0,0,100)
            frame[44]=RGB(0,0,100)
            frame[48]=RGB(0,0,100)

            frame[81]=RGB(0,0,100)
            frame[84]=RGB(0,0,100)
            frame[77]=RGB(0,0,100)
            frame[101]=RGB(0,0,100)
            return frame
        elif step ==5:
            frame = blank_frame()
            frame[3]=RGB(0,0,100)
            frame[7]=RGB(0,0,100)
            frame[11]=RGB(0,0,100)
            frame[15]=RGB(0,0,100)
            frame[23]=RGB(0,0,100)

            frame[82]=RGB(0,0,100)
            frame[56]=RGB(0,0,100)
            frame[97]=RGB(0,0,100)
            frame[63]=RGB(0,0,100)
            frame[65]=RGB(0,0,100)

            frame[92]=RGB(0,0,100)
            frame[103]=RGB(0,0,100)
        elif step ==6:
            frame=blank_frame()
            frame[40]=RGB(0,0,100)
            frame[31]=RGB(0,0,100)
            frame[60]=RGB(0,0,100)
            frame[49]=RGB(0,0,100)
            frame[45]=RGB(0,0,100)

            frame[102]=RGB(0,0,100)
            frame[80]=RGB(0,0,100)
            frame[100]=RGB(0,0,100)
            return frame
        elif step ==7:
            frame=blank_frame()
            frame[57]=RGB(0,0,100)
            frame[70]=RGB(0,0,100)
            frame[97]=RGB(0,0,100)
            frame[66]=RGB(0,0,100)
            frame[87]=RGB(0,0,100)
#rain animation
    def rain_animation(self):
        while True:
            for(step) in range(1,7):
                frame = self.rain_frame(step)
                display(frame)
                time.sleep(0.2)
    
