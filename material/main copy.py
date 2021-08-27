# OE5VRL Bake


#https://docs.micropython.org/en/latest/library/machine.UART.html


#from machine import Pin, Timer
#import machine
#import time
#import sys
#import uselect

# from machine import Pin

# print("1")
# p0 = Pin(25, Pin.OUT)    # create output pin on GPIO0
# p0.on()                 # set pin to "on" (high) level
# p0.off()                # set pin to "off" (low) level
# p0.value(1)             # set pin to on/high
# print("2")

import utime
from machine import UART
print("start")
u=UART(0)

u.write("\nhello\n")
utime.sleep_ms(100)
#while u.any():
while True:
    if u.any():
        print(".")
        print(u.read(1))
    utime.sleep_ms(100)
    print("*")    

print()
print("- bye -")




#comm = machine.UART(1,9600)
#comm.init(9600, bits=8, parity=None, stop=1, timeout=2000, tx=1, rx=2) 
#comm.write("hugo")

#s = input("?")
#print(s)

#led = Pin(25, Pin.OUT)
#tim = Timer()
# def tick(timer):
#     global led
#     led.toggle()

# tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

# i=0
 #while True:
#     print(i)
#     i=i+1
#     time.sleep(.5)
 
#class serial():
#    def __init__(self):
#        #comm = machine.UART(1,9600)
#        #comm.init(9600, bits=8, parity=None, stop=1, timeout=2000) 
#        #tim.init(freq=2.5, mode=Timer.PERIODIC, callback=self.tick)#
#
#        pass
#
#    def tick(self,x):
#        print("hi")


#s = serial()
#s.tick(1)

#tim.init(freq=2.5, mode=Timer.PERIODIC, callback=s.tick)


# # Function to read a character from USB serial or return None.
# def kbhit():
#     spoll=uselect.poll()        # Set up an input polling object.
#     spoll.register(sys.stdin,uselect.POLLIN)    # Register polling object.

#     kbch = sys.stdin.read(1) if spoll.poll(0) else None

#     spoll.unregister(sys.stdin)
#     return(kbch)

# # MAIN ---------------------------------
# print('Input characters: ', end='')
# while True:
#     new_ch = kbhit()
#     if new_ch == None:
#         continue
#     elif new_ch == 'q':
#         break
#     else:
#         print(new_ch, end='', sep='')

# sys.stdin.close()
# print(sys.version)
# sys.exit(0)