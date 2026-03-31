# 246-group-project-G14
This project aims to provide convenience to commuters who regularly take a specific bus route. Our team redesigned an analog clock to display weather information, the time the user has to leave their house to make the next bus. To do this, we created a config website where the user can type in their address, their bus route, and the weather location they want to be displayed.

For physical assembly of the clock, we soldered an LED matrix to the clock which displays the weather condition through animations and colors. Moreover, we 3D printed a connector to attach a stepper motor to the gears of the clock. Finally, we attached a 7-segment display to the clock to display a countdown until the user needs to leave for their bus.

Using the information from the config website, we implemented various APIs and used Python to design the display of the clock. We used Google Maps API, and a weather API to send data to the Raspberry Pi. On the Pi, we coded the stepper motor to adjust the hands of the clock to display the correct time the user must leave for their bus. Furthermore, we coded frames and animations for the LEDs to display the weather information. 

Ultimately, our clock will provide a helpful and aesthetic way for regular commuters to arrive at their bus stop on time.
