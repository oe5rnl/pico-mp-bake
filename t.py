from machine import UART, Pin, Timer
import utime


class T:

    def __init__(self):
        self.t1=0
        self.t2=0
        self.t3=0
        self.tim = Timer()
        
    def start(self):
        self.tim.init(period=5000, mode=Timer.ONE_SHOT, callback=self.dummy)

    def dummy(self, x):
        self.t3 = utime.ticks_us()
        #print(self.t3)
        print((self.t3-self.t1)/1000000)
        print('dummy')

def main():
    print('tt')

    t = T()
    t.t1 = utime.ticks_us()
    t.start()
    t.t2 = utime.ticks_us()

    #print(t.t1)
    #print(t.t2)
    print((t.t2-t.t1)/1000000)
    #print(t.t3)
    print('-----')


if __name__ == "__main__":
    main()





 # #uendTime= utime.ticks_us()
        # #ud = utime.ticks_diff(uendTime, self.ustartTime)
        # #print(ud)