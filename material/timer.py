from machine import Pin, Timer
import time

def tick(x):
        t = Pin(17, Pin.OUT)
        t.on()
        time.sleep_ms(1)
        t.off()
        #time.sleep_ms(3000)

tim = Timer()
tim.init(period=50, mode=Timer.PERIODIC, callback=tick)

t = Pin(27, Pin.OUT)
t.on()
time.sleep_us(100)
t.off()

while True:
    time.sleep(500)
