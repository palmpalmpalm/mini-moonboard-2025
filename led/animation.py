# -*- coding: utf-8 -*-
from bibliopixel.colors import COLORS
from bibliopixel import Strip
from bibliopixel.drivers.PiWS281X import PiWS281X
from bibliopixel.drivers.dummy_driver import DriverDummy
from bibliopixel.drivers.SPI.WS2801 import  WS2801
from bibliopixel.drivers.SimPixel import SimPixel
from bibliopixel.drivers.spi_interfaces import SPI_INTERFACES
import string
import json
import time
import random
def hex2rgb(hexcolor):
    h = hexcolor.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)



# FIXME: Describe Layouts 
# FIXME: Delete this
LED_LAYOUT = {
    'nest':[
    # Top panel
    [137, 138, 149, 150, 161, 162, 173, 174, 185, 186, 197],
    [136, 139, 148, 151, 160, 163, 172, 175, 184, 187, 196],
    [135, 140, 147, 152, 159, 164, 171, 176, 183, 188, 195],
    [134, 141, 146, 153, 158, 165, 170, 177, 182, 189, 194],
    [133, 142, 145, 154, 157, 166, 169, 178, 181, 190, 193],
    [132, 143, 144, 155, 156, 167, 168, 179, 180, 191, 192],
    # Middle panel
    [131, 120, 119, 108, 107, 96, 95, 84, 83, 72, 71],
    [130, 121, 118, 109, 106, 97, 94, 85, 82, 73, 70],
    [129, 122, 117, 110, 105, 98, 93, 86, 81, 74, 69],
    [128, 123, 116, 111, 104, 99, 92, 87, 80, 75, 68],
    [127, 124, 115, 112, 103, 100, 91, 88, 79, 76, 67],
    [126, 125, 114, 113, 102, 101, 90, 89, 78, 77, 66],
    # Bottom panel
    [5, 6, 17, 18, 29, 30, 41, 42, 53, 54, 65],
    [4, 7, 16, 19, 28, 31, 40, 43, 52, 55, 64],
    [3, 8, 15, 20, 27, 32, 39, 44, 51, 56, 63],
    [2, 9, 14, 21, 26, 33, 38, 45, 50, 57, 62],
    [1, 10, 13, 22, 25, 34, 37, 46, 49, 58, 61],
    [0, 11, 12, 23, 24, 35, 36, 47, 48, 59, 60]],

'evo': [[ 17,  18,  53,  54,  89,  90, 125, 126, 161, 162, 197],
       [ 16,  19,  52,  55,  88,  91, 124, 127, 160, 163, 196],
       [ 15,  20,  51,  56,  87,  92, 123, 128, 159, 164, 195],
       [ 14,  21,  50,  57,  86,  93, 122, 129, 158, 165, 194],
       [ 13,  22,  49,  58,  85,  94, 121, 130, 157, 166, 193],
       [ 12,  23,  48,  59,  84,  95, 120, 131, 156, 167, 192],
       [ 11,  24,  47,  60,  83,  96, 119, 132, 155, 168, 191],
       [ 10,  25,  46,  61,  82,  97, 118, 133, 154, 169, 190],
       [  9,  26,  45,  62,  81,  98, 117, 134, 153, 170, 189],
       [  8,  27,  44,  63,  80,  99, 116, 135, 152, 171, 188],
       [  7,  28,  43,  64,  79, 100, 115, 136, 151, 172, 187],
       [  6,  29,  42,  65,  78, 101, 114, 137, 150, 173, 186],
       [  5,  30,  41,  66,  77, 102, 113, 138, 149, 174, 185],
       [  4,  31,  40,  67,  76, 103, 112, 139, 148, 175, 184],
       [  3,  32,  39,  68,  75, 104, 111, 140, 147, 176, 183],
       [  2,  33,  38,  69,  74, 105, 110, 141, 146, 177, 182],
       [  1,  34,  37,  70,  73, 106, 109, 142, 145, 178, 181],
       [  0,  35,  36,  71,  72, 107, 108, 143, 144, 179, 180]]
       }

class MoonBoard:
    DEFAULT_PROBLEM_COLORS = {'START':COLORS.blue,'TOP':COLORS.red,'MOVES':COLORS.green}
    DEFAULT_COLOR = COLORS.blue #FIXME ?
    X_GRID_NAMES = string.ascii_uppercase[0:11] # FIXME: del
    LED_SPACING = 3 # Use every n-th LED only - used for 3 x 4x5 LED strp      # FIXME: normal=1
    ROWS = 18 
    COLS = 11
    NUM_PIXELS = ROWS*COLS * LED_SPACING
    DEFAULT_BRIGHTNESS = 100 # FIXME: to config file
    SETUP = 'MoonboardMasters2017' # FIXME: to config file / Arg

    
    # FIXME: json
    MAPPING= { }

    with open('/home/pi/moonboard/led/led_mapping.json') as json_file:
        data = json.load(json_file)
        MAPPING = data


    def __init__(self, driver_type, led_layout=None, brightness=DEFAULT_BRIGHTNESS):
        try:
            if driver_type == "PiWS281x":
                driver = PiWS281X(self.NUM_PIXELS)
            elif driver_type == "WS2801":
                driver = WS2801(self.NUM_PIXELS, dev='/dev/spidev0.1',spi_interface= SPI_INTERFACES.PERIPHERY,spi_speed=1)
            elif driver_type == "SimPixel":
                driver = SimPixel(self.NUM_PIXELS)
                driver.open_browser()
            else:
                raise ValueError("driver_type {driver_type} unknow.".format(driver_type) )
        except (ImportError, ValueError) as e:
            print("Not able to initialize the driver. Error{}".format(e))
            print("Use bibliopixel.drivers.dummy_driver")
            driver = DriverDummy(self.NUM_PIXELS)

        if led_layout is not None:
            self.layout = Strip (driver, brightness=brightness,threadedUpdate=True)
        else:
            self.layout = Strip (driver, brightness=brightness,threadedUpdate=True) 
        self.layout.cleanup_drivers()
        self.layout.start()
        self.animation = None

    def clear(self):
        self.stop_animation()
        self.layout.all_off()
        self.layout.push_to_driver()

    def set_hold(self, hold, color=DEFAULT_COLOR):
        self.layout.set(self.MAPPING[hold], color)

    def show_hold(self, hold, color=DEFAULT_COLOR):
        self.set_hold(hold, color)
        self.layout.push_to_driver()

    def show_problem(self, holds, hold_colors={}):
        self.clear()
        for k in ['START', 'MOVES', 'TOP']:
            for hold in holds[k]:
                self.set_hold(
                    hold, 
                    hold_colors.get(k, self.DEFAULT_PROBLEM_COLORS[k]),
                    )
        self.layout.push_to_driver()

    # run all colors in led´s to see if something is missing
    def led_test(self):
        print('led test')
        duration = 0.4
        COLORS = ['red', 'green', 'blue']

        for color in range(len(COLORS)):
            for i in range(1,self.ROWS+1):
                for j in range (0,self.COLS):
                    le = chr(j+65)
                    h = le+str(i)
                    #print (h)
                    self.layout.set(self.MAPPING[h], COLORS[color])
                self.layout.push_to_driver()
                time.sleep(duration)

        time.sleep (1.2)
        self.clear()



    def run_flare(self, my_col="F", use_cols=False):
        # Reference: http://www.anirama.com/1000leds/1d-fireworks/
        NUM_LEDS = 18 # FIXME
        #NUM_SPARKS = NUM_LEDS/2 #// max number (could be NUM_LEDS / 2);
        
        sparkPos = [0,0,0,0,0,0,0,0,0] # width of flare: 3 LED
        sparkVel = [0,0,0,0,0,0,0,0,0]
        sparkCol = [0,0,0,0,0,0,0,0,0]
        tmp_col = ord (my_col)
        spark_col = [tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col]
        
        flarePos = 0.
        gravity = -.004 * 10 # m/s/s
        flareVel = random.randint(50,90) / 100.  *1.55 # trial and error to get reasonable range
        brightness = 1.

        # initialize launch sparks
        print ("Init launch sparks")
        for i in range (0,3): # FIXME nSparks
            sparkPos[i] = 0.
            sparkVel[i] = flareVel * float(random.randint(80,120) / 100)  # * (flareVel / 5)
            # random around 20% of flare velocity
            sparkCol[i] = sparkVel[i] * 1000
            sparkCol[i] = clamp(sparkCol[i], 0, 255)
            print (str(i)+ " with "+str(sparkVel[i])+" and "+str(sparkCol[i]))

        # Phase 1: Flare
        print ("Launch flare")
        self.clear()
        while flareVel >= -.2:
            # sparks
            print ("Run spark with velocity "+str(flareVel))

            # Disable all led in column
            for i in range (1,NUM_LEDS+1):
                tmp_led = my_col + str (i)
                self.layout.set(self.MAPPING[tmp_led], (0,0,0))

            for i in range (0,3):
                sparkPos[i] = sparkPos[i] + sparkVel[i]
                sparkPos[i] = clamp(sparkPos[i], 0.0, NUM_LEDS*1.0)
                sparkVel[i] = sparkVel[i] + gravity
                sparkCol[i] = sparkCol[i] -.8*7 # FIXME
                sparkCol[i] = clamp(sparkCol[i], 0.0, 255.0)
                tmp_row = clamp(int (sparkPos[i]), 1, NUM_LEDS)
                c = (sparkCol[i],0,0) # FIXME: cleanup
                tmp_led = my_col + str (tmp_row)
                print ("Spark position "+str(tmp_led)+" with "+str(sparkPos[i])+" and "+str(sparkCol[i]))
                self.layout.set(self.MAPPING[tmp_led], c)


            # flare
            tmp_row = clamp(int (flarePos), 1, NUM_LEDS)
            tmp_led = my_col + str (tmp_row)
            flareCol = (255.,0,0) # FIXME 
            print ("Flare position "+str(tmp_led)+" with "+str(flarePos)+" and "+str(flareCol))
            self.layout.set(self.MAPPING[tmp_led], flareCol)
            self.layout.push_to_driver()
            flarePos = flarePos + flareVel
            flarePos = clamp(flarePos, 0, NUM_LEDS)
            flareVel = flareVel + gravity
            brightness =  brightness * 0.9

        # Phase 2: Explosion
        print ("Run explosion")
        nSparks = int (flarePos / 2)

        # Initialize Sparks
        for i in range (0,nSparks):
            sparkPos[i] = flarePos
            sparkVel[i] = float(random.randint(-100,100) / 100) # from -1 to 1 
            sparkCol[i] = abs(sparkVel[i]) * 500 # set colors before scaling velocity to keep them bright 
            sparkCol[i] = clamp(sparkCol[i], 0., 255.)
            sparkVel[i] = sparkVel[i] * flarePos / NUM_LEDS # proportional to height 

        sparkCol[0] = 255 # // this will be our known spark 
        dying_gravity = gravity
        c1 = 120*1.5
        c2 = 50*2.7

        while sparkCol[0] > c2/128: # as long as our known spark is lit, work with all the sparks
            print ("Run spark with reference spark lit  "+str(sparkCol[0]))

            # Disable all led in column
            for i in range (1,NUM_LEDS+1):
                tmp_led = my_col + str (i)
                self.layout.set(self.MAPPING[tmp_led], (0,0,0))

            for i in range (0,nSparks):
                sparkPos[i] = sparkPos[i] + sparkVel[i]
                sparkPos[i] = clamp(sparkPos[i], 0, NUM_LEDS)
                sparkVel[i] = sparkVel[i] + dying_gravity
                sparkCol[i] = sparkCol[i] * .9 # FIXME 
                sparkCol[i] = clamp(sparkCol[i], 0, 255) #  // red cross dissolve 
                
                tmp_col = my_col
                if use_cols:
                    spark_col[i] = spark_col[i] + sparkVel[i]
                    spark_col[i] = clamp(spark_col[i],65,65+11-1) # FIXME
                    tmp_col = chr(int(spark_col[i]))

                c = (0,0,0)
                tmp_row = clamp(int (sparkPos[i]), 1, NUM_LEDS)
                tmp_led = tmp_col + str (tmp_row)
                if(sparkCol[i] > c1): #// fade white to yellow
                    c = (255, 255, (255 * (sparkCol[i] - c1)) / (255 - c1))
                elif sparkCol[i] < c2: # // fade from red to black
                    c = ((255 * sparkCol[i]) / c2, 0, 0)
                else: # // fade from yellow to red
                    c = (255, (255 * (sparkCol[i] - c2)) / (c1 - c2), 0)     

                print ("Spark position "+str(tmp_led)+" with "+str(sparkPos[i])+" and "+str(tmp_col)+" and "+str(c))

                self.layout.set(self.MAPPING[tmp_led], c)

            dying_gravity = dying_gravity * .995 #// as sparks burn out they fall slower
            self.layout.push_to_driver()

    def run_flare_multi(self, my_col="F", use_cols=False):
        # Reference: http://www.anirama.com/1000leds/1d-fireworks/
        NUM_LEDS = 18 # FIXME
        #NUM_SPARKS = NUM_LEDS/2 #// max number (could be NUM_LEDS / 2);
        
        sparkPos = [0,0,0,0,0,0,0,0,0] # width of flare: 3 LED
        sparkVel = [0,0,0,0,0,0,0,0,0]
        sparkCol = [0,0,0,0,0,0,0,0,0]
        tmp_col = ord (my_col)
        spark_col = [tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col,tmp_col]
        
        flarePos = 0.
        gravity = -.004 * 10 # m/s/s
        flareVel = random.randint(50,90) / 100.  *1.55 # trial and error to get reasonable range
        brightness = 1.

        # initialize launch sparks
        print ("Init launch sparks")
        for i in range (0,3): # FIXME nSparks
            sparkPos[i] = 0.
            sparkVel[i] = flareVel * float(random.randint(80,120) / 100)  # * (flareVel / 5)
            # random around 20% of flare velocity
            sparkCol[i] = sparkVel[i] * 1000
            sparkCol[i] = clamp(sparkCol[i], 0, 255)
            print (str(i)+ " with "+str(sparkVel[i])+" and "+str(sparkCol[i]))

        # Phase 1: Flare
        print ("Launch flare")
        self.clear()
        while flareVel >= -.2:
            # sparks
            print ("Run spark with velocity "+str(flareVel))

            # Disable all led in column
            for i in range (1,NUM_LEDS+1):
                for my_col in ["A","B","C","D","E","F","G","H","I","J","K"]:
                    tmp_led = my_col + str (i)
                    self.layout.set(self.MAPPING[tmp_led], (0,0,0))

            for i in range (0,3):
                sparkPos[i] = sparkPos[i] + sparkVel[i]
                sparkPos[i] = clamp(sparkPos[i], 0.0, NUM_LEDS*1.0)
                sparkVel[i] = sparkVel[i] + gravity
                sparkCol[i] = sparkCol[i] -.8*7 # FIXME
                sparkCol[i] = clamp(sparkCol[i], 0.0, 255.0)
                tmp_row = clamp(int (sparkPos[i]), 1, NUM_LEDS)
                c = (sparkCol[i],0,0) # FIXME: cleanup
                for my_col in ["A","B","C","D","E","F","G","H","I","J","K"]:
                    tmp_led = my_col + str (tmp_row)
                    print ("Spark position "+str(tmp_led)+" with "+str(sparkPos[i])+" and "+str(sparkCol[i]))
                    self.layout.set(self.MAPPING[tmp_led], c)


            # flare
            tmp_row = clamp(int (flarePos), 1, NUM_LEDS)
            for my_col in ["A","B","C","D","E","F","G","H","I","J","K"]:
                tmp_led = my_col + str (tmp_row)
                flareCol = (255.,0,0) # FIXME 
                print ("Flare position "+str(tmp_led)+" with "+str(flarePos)+" and "+str(flareCol))
                self.layout.set(self.MAPPING[tmp_led], flareCol)

            self.layout.push_to_driver()
            flarePos = flarePos + flareVel
            flarePos = clamp(flarePos, 0, NUM_LEDS)
            flareVel = flareVel + gravity
            brightness =  brightness * 0.9

        # Phase 2: Explosion
        print ("Run explosion")
        nSparks = int (flarePos / 2)

        # Initialize Sparks
        for i in range (0,nSparks):
            sparkPos[i] = flarePos
            sparkVel[i] = float(random.randint(-100,100) / 100) # from -1 to 1 
            sparkCol[i] = abs(sparkVel[i]) * 500 # set colors before scaling velocity to keep them bright 
            sparkCol[i] = clamp(sparkCol[i], 0., 255.)
            sparkVel[i] = sparkVel[i] * flarePos / NUM_LEDS # proportional to height 

        sparkCol[0] = 255 # // this will be our known spark 
        dying_gravity = gravity
        c1 = 120*1.5
        c2 = 50*2.7

        while sparkCol[0] > c2/128: # as long as our known spark is lit, work with all the sparks
            print ("Run spark with reference spark lit  "+str(sparkCol[0]))

            # Disable all led in column
            for i in range (1,NUM_LEDS+1):
                for my_col in ["A","B","C","D","E","F","G","H","I","J","K"]:
                    tmp_led = my_col + str (i)
                    self.layout.set(self.MAPPING[tmp_led], (0,0,0))

            for i in range (0,nSparks):
                sparkPos[i] = sparkPos[i] + sparkVel[i]
                sparkPos[i] = clamp(sparkPos[i], 0, NUM_LEDS)
                sparkVel[i] = sparkVel[i] + dying_gravity
                sparkCol[i] = sparkCol[i] * .9 # FIXME 
                sparkCol[i] = clamp(sparkCol[i], 0, 255) #  // red cross dissolve 

                if(sparkCol[i] > c1): #// fade white to yellow
                    c = (255, 255, (255 * (sparkCol[i] - c1)) / (255 - c1))
                elif sparkCol[i] < c2: # // fade from red to black
                    c = ((255 * sparkCol[i]) / c2, 0, 0)
                else: # // fade from yellow to red
                    c = (255, (255 * (sparkCol[i] - c2)) / (c1 - c2), 0)    

                for my_col in ["A","B","C","D","E","F","G","H","I","J","K"]:
                    tmp_col = my_col

                    c = (0,0,0)
                    tmp_row = clamp(int (sparkPos[i]), 1, NUM_LEDS)
                    tmp_led = tmp_col + str (tmp_row)
                  

                    print ("Spark position "+str(tmp_led)+" with "+str(sparkPos[i])+" and "+str(tmp_col)+" and "+str(c))

                    self.layout.set(self.MAPPING[tmp_led], c)

            dying_gravity = dying_gravity * .995 #// as sparks burn out they fall slower
            self.layout.push_to_driver()

    def run_animation(self, duration = 0.01): 
        # The moonboard can serve a (x,y) = (11,18) --> 198 Pixel display 
        # Refs: 
        # - http://www.anirama.com/1000leds/1d-fireworks/
        duration2 = duration * 0

        for i in range(1,self.ROWS+1):
            for j in range (0,self.COLS):

                le = chr(j+65)
                h = le+str(i)
                print (h)
                for c in [COLORS.purple, COLORS.blue, COLORS.red]:
                    self.layout.set(self.MAPPING[h], c)
                    self.layout.push_to_driver()
                    time.sleep(duration)
    
        time.sleep(duration2)

        self.clear()

    def display_melon(self):
        # Ref: http://pixelartmaker.com/art/d8f3ce82dd215ed
        self.clear()
        red = (255,0,0)
        black = (0,0,0)
        lila = hex2rgb("#ff99dd") #(255,100,200) #ff99dd
        green1 = hex2rgb("#118233") #COLORS.lime)
        green2 = hex2rgb("#089c48") #COLORS.limegreen

        for h in ["C1","D1","E1","F1","G1"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["B2","H2"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["C2","D2","E2","F2","G2"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["A3","I3"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["H3"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["B3","C3","D3","E3","F3","G3"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["A4","C4","D4","E4","F4","G4"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["H4"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["I4"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["J4"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["A5","B5","C5","E5","G4"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["H5"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["I5"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["J5"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["B6","C6","D6","E6","F6","G6"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["H6"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["I6"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["J6"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["C7","D7","F7","G7"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["H7"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["I7"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["J7"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["D8","E8","F8"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["H8"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["I8"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["J8"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["E9","F9"]:
            self.layout.set(self.MAPPING[h], red)
        for h in ["G9"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["H9"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["I9"]:
            self.layout.set(self.MAPPING[h], green2)
        for h in ["F10"]:
            self.layout.set(self.MAPPING[h], lila)
        for h in ["G10"]:
            self.layout.set(self.MAPPING[h], green1)
        for h in ["H10"]:
            self.layout.set(self.MAPPING[h], green2)

        self.layout.push_to_driver()
        time.sleep(10)


        
    def run_animation_single_color(self, duration = 5,color=(255,0,0)): 
        for i in range(1,self.ROWS+1):
            for j in range (0,self.COLS):

                le = chr(j+65)
                h = le+str(i)
                print (h)
                self.layout.set(self.MAPPING[h], color)

        self.layout.push_to_driver()

        time.sleep(duration)

        self.clear()

    def run_animation_xmas(self, duration = 0.01): 

        duration2 = 1#duration * 10

        for c in [COLORS.purple, COLORS.blue, COLORS.red, COLORS.green]:

            for i in range(1,self.ROWS+1):
                for j in range (0,self.COLS):

                    le = chr(j+65)
                    h = le+str(i)
                    print (h)
                    self.layout.set(self.MAPPING[h], c)

                self.layout.push_to_driver()

                time.sleep(duration)

            time.sleep(duration2)





        self.clear()
        
    def display_holdset(self, holdset="Hold Set A", duration=10, **kwds): 
        print ("Display holdset: " + str(holdset))

        with open('../problems/HoldSetup.json') as json_file: # FIXME: path 
            data = json.load(json_file)
            for hold in data[self.SETUP]:
                hs = (data[self.SETUP][hold]['HoldSet']) 
                color = COLORS.black
    
                if (hs == holdset):# FIXME
                        color = COLORS.green                    
    
                self.layout.set(self.MAPPING[hold], color)

                #self.set_hold (hold, color)
                #print "Orientation"
        
        self.layout.push_to_driver()

        wait_holdset_duration = duration # FIXME
        time.sleep(wait_holdset_duration)

        self.clear()
                
                
                
    def stop_animation(self):
        if self.animation is not None:
            self.animation.stop()


class TestAnimation:
    COLOR=[COLORS.Green, COLORS.Blue]
    def __init__(self, layout, ):
        self.layout = layout

    def step(self, amt=1):
        pass

if __name__=="__main__":
    import argparse
    import time
    import subprocess

    parser = argparse.ArgumentParser(description='Test led system')

    parser.add_argument('--driver_type', type=str,
                        help='driver type, depends on leds and device controlling the led.',choices=['PiWS281x', 'WS2801', 'SimPixel'],
                        default = "PiWS281x")
    parser.add_argument('--duration',  type=int, default=10,
                        help='Delay of progress.')
    parser.add_argument('--holdset',  type=str, help="Display a holdset for current layout", 
                        choices=['Hold Set A', 'Hold Set B', 'Hold Set C', 'Original School Holds', "Wooden Holds"],
                        default = "Hold Set A")
    args = parser.parse_args()
        
    led_layout = None

    MOONBOARD = MoonBoard(args.driver_type,led_layout )
    
    # Display a holdset
    #MOONBOARD.display_holdset(args.holdset, args.duration)

    print("Run animation,")
    #MOONBOARD.run_animation() 
    #MOONBOARD.run_flare(my_col="A")
    while True:
        #
        MOONBOARD.run_animation_xmas()
        MOONBOARD.display_melon()
        MOONBOARD.run_flare(my_col="F")
        MOONBOARD.run_animation_single_color(color=(255,1,154))
        MOONBOARD.run_animation_single_color(color=(255,255,0))
        #MOONBOARD.run_animation_single_color(color=(0,0,255))

    print(f"wait {args.duration} seconds,")
    time.sleep(args.duration)
    print("clear and exit.")
    MOONBOARD.clear()