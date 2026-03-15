# -*- coding: utf-8 -*-
import argparse
from moonboard import MoonBoard
from functools import partial
import json
import RPi.GPIO as GPIO
import os
#import signal
import sys
import logging
import time
import paho.mqtt.client as paho # FIXME pip install 
import math # floor

# external power LED and power button
LED_GPIO = 26
BUTTON_GPIO = 3


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='Display(%(threadName)-10s) %(message)s',
                    )

class Database():
    def __init__(self, driver_type="", led_layout=""):
        self._MOONBOARD = MoonBoard(driver_type, led_layout)

        # Init timers
        self._time_current = time.time()
        self._time_last = self._time_current 
        self._update_interval = 1.0 #0.5 # Update interval for display in seconds


    def _on_message(self, client, userdata, message):
        logging.debug("Received message " + str(message.payload.decode("utf-8")))
        #mm = message.payload.decode("utf-8")
        msg = json.loads(message.payload.decode("utf-8"))

        GREEN = (0,255,0)
        BLUE = (0,0,255)
        RED = (255,0,0)
        VIOLET = (180,0,255)
        CYAN = (0,255,255)
        PINK = (255,96,136)

        self._MOONBOARD.clear()
        for hold_type, color in [("START", GREEN), ("MOVES", BLUE), ("LEFT", VIOLET),
                                  ("FOOT", CYAN), ("MATCH", PINK), ("TOP", RED)]:
            for h in msg.get(hold_type, []):
                if h in self._MOONBOARD.MAPPING:
                    self._MOONBOARD.layout.set(self._MOONBOARD.MAPPING[h], color)
                else:
                    logging.warning("Hold %s not in mapping, skipping", h)
        self._MOONBOARD.layout.push_to_driver()



    def _record_data(self, hostname="localhost",port=1883):
        logging.debug("Start recording data from mqtt to database")
        self._client= paho.Client("client-001")  # FIXME
        self._client.on_message=self._on_message
        self._client.connect(hostname,port,60)#connect

        # FIXME: subscribe to all?
        
        self._client.subscribe("moonboard/ble/problem")


        self._client.loop_forever()

# Main stuff

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--driver_type',
                        help='driver type, depends on leds and device controlling the led.',
                        choices=['PiWS281x', 'WS2801', 'SimPixel'],
                        default='PiWS281x')

    parser.add_argument('--brightness',  default=100, type=int)

    parser.add_argument('--led_mapping',
                        type=str,  
                        default='led_mapping.json', 
                        )

    parser.add_argument('--debug',  action = "store_true")

    args = parser.parse_args()
    argsd=vars(args)
    logger = logging.getLogger('run')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    #problems
    led_layout = args.led_mapping
    driver_type = args.driver_type

    d = Database(driver_type=driver_type, led_layout=led_layout)
    d._record_data(hostname="localhost")   
