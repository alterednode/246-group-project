import time
from RGB import RGB,blank_frame
from display import display

class SnowAnimation:
 def snow_frame(self,step):
    if step ==1:
        frame = blank_frame()
        frame[6]=RGB(255,255,255)
        frame[2]=RGB(255,255,255)
        frame[11]=RGB(255,255,255)
        frame[22]=RGB(255,255,255)
        frame[18]=RGB(255,255,255)
        frame[25]=RGB(255,255,255)
        return frame
    
    elif step ==2:
        frame = blank_frame()

        frame[30]=RGB(255,255,255)
        frame[19]=RGB(255,255,255)
        frame[20]=RGB(255,255,255)
        frame[43]=RGB(255,255,255)
        frame[39]=RGB(255,255,255)
        frame[48]=RGB(255,255,255)
        return frame
    
    elif step ==3:
        frame = blank_frame()
        frame[8]=RGB(255,255,255)
        frame[14]=RGB(255,255,255)
        frame[3]=RGB(255,255,255)
        frame[17]=RGB(255,255,255)
        frame[23]=RGB(255,255,255)
       


        frame[70]=RGB(255,255,255)
        frame[41]=RGB(255,255,255)
        frame[45]=RGB(255,255,255)
        frame[62]=RGB(255,255,255)
        frame[57]=RGB(255,255,255)
        frame[65]=RGB(255,255,255)
        return frame
    elif step ==4:
        frame = blank_frame()
       frame[32]=RGB(255,255,255)
        frame[42]=RGB(255,255,255)
        frame[40]=RGB(255,255,255)
        frame[50]=RGB(255,255,255)
        frame[44]=RGB(255,255,255)

        frame[84]=RGB(255,255,255)
        frame[59]=RGB(255,255,255)
        frame[63]=RGB(255,255,255)
        frame[87]=RGB(255,255,255)
        frame[80]=RGB(255,255,255)
        frame[78]=RGB(255,255,255)
        return frame
    elif step ==5:
        frame = blank_frame()
        frame[71]=RGB(255,255,255)
        frame[62]=RGB(255,255,255)
        frame[57]=RGB(255,255,255)
        frame[66]=RGB(255,255,255)
        frame[88]=RGB(255,255,255)

        frame[104]=RGB(255,255,255)
        frame[59]=RGB(255,255,255)
        frame[63]=RGB(255,255,255)
        frame[87]=RGB(255,255,255)
        frame[80]=RGB(255,255,255)
        frame[78]=RGB(255,255,255)

        return frame
    elif step ==6:
        frame = blank_frame()
        frame[85]=RGB(255,255,255)
        frame[87]=RGB(255,255,255)
        frame[81]=RGB(255,255,255)
        frame[77]=RGB(255,255,255)
        return frame
    elif step==7:
        frame = blank_frame()
        frame[105]=RGB(255,255,255)
        frame[101]=RGB(255,255,255)
        frame[92]=RGB(255,255,255)
        return frame
    

#snow animation 
    def snow_animation(self):
        while True:
            for(step) in range(1,7):
                frame = self.snow_frame(step)
                display(frame)
                time.sleep(0.5)
             

