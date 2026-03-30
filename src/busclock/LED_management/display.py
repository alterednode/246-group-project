from RGB import num_leds
#test display function
def display(frame):
    lit_leds = []
    for i, led in enumerate(frame):
        if led.r != 0 or led.g != 0 or led.b != 0:
            lit_leds.append(i)
    print("Lit LEDs:", lit_leds)# shows which leds are on in the frame



#display function for acutal LEDS 
#pixels = neopixel.NeoPixel(board.D18, num_leds,brightness=0.2, auto_write=False)

#def display(frame):
    #for i, led in enumerate(frame):
        #pixels[i] = (led.r, led.g, led.b)

    #pixels.show()

