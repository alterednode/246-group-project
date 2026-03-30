 from RGB import blank_frame
from display import display
from snowing import SnowAnimation
 from sunny import SunnyAnimation
from LateForBus import LateForBusAnimation
from cloudy_frame import CloudyAnimation
 from rain_frame import RainAnimation
 

def led( weather):
    if weather == "snowing":
         snow= SnowAnimation()
         snow.snow_animation()
    elif weather == "raining":
         rain= RainAnimation()
         rain.rain_animation()
    elif weather == "sunny":
         sun= SunnyAnimation()
         sun.sunny_animation()
    elif weather == "late":
         lateForBus= LateForBusAnimation()
         lateForBus.late_for_bus_animation()
     elif weather == "cloudy":
         cloudy= CloudyAnimation()
         cloudy.cloudy_animation()
    elif weather == "off":
         display(blank_frame())
         



    