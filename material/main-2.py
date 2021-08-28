
# OE5VRL Bake

import utime
from machine import UART, Pin, Timer
#import machine
import time
import os
import json



def main():
    tim = Timer()
    tim.init(mode=Timer.PERIODIC, period=10, callback=tick)

def tick(x):

    pass


if __name__ == "__main__":
    main()
