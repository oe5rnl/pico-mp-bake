# OE5VRL Bake

import utime
from machine import UART, Pin, Timer
#import machine
import time
import os
import json


# https://onlinetonegenerator.com/dtmf.html
# from statemachine import StateMachine, State
# https://docs.micropython.org/en/latest/wipy/tutorial/timer.html
# https://docs.micropython.org/en/latest/library/machine.html

class Pgm:
    
    def __init__(self):
        
        self.i=0
        self.command = ""
        self.cmode = False
           
        self.u = UART(id=0,baudrate=9600, bits=8, parity=None, stop=1, timeout=2000, rxbuf=256, txbuf=256)
        #self.u.irq( UART.RX_ANY , Priorität = 1 , Handler = uart_rx , Wake = machine.IDLE )
    
        tim = Timer()
        tim.init(period=50, mode=Timer.PERIODIC, callback=self.tick)
         

    def tick(self,x):
        #print("*")
        #print(self.i)
        #self.i=self.i+1
        if self.u.any():
            c=self.u.read(1).decode()
            #self.u.write(c) # echo
            print(c, end='')
            # config upload
            
            if c == chr(2): #STX
                self.command=""
                self.cmode = True
                print()
                print("STX")
                
            if self.cmode:
                self.command = self.command + c
            
            if c == chr(3): #ETX
                print()
                print("ETX")
                self.cmode = False              
                f = open('config.txt', 'w')
                f.write(self.command)
                f.close()      
            
            if not self.cmode:
                # sonstige commands
                if c == "*":
                    print("reset eingabe *")
                    self.command=""
                elif c == "#":
                    print("command fertig")
                    print(self.command)
                    if self.command == "VVV":
                        self.u.write("v0.1")
                        print("v0.1")
                        machine.soft_reset( )                  
                elif c != "*" and c != "#":  
                    self.command=self.command+c
            
    
class Dtmf:

    def __init__(self,callback):

        self.command = ""
        self.dtmf_code = 0
        self.dtmf_char = ''
        self.eingabe_mode = False
        self.callback = callback
        self.i = 0
        
        self.bc = {1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'0',11:'*',12:'#',13:'A',14:'B',15:'C',0:'D'}

        self.d1 = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.d2 = Pin(3, Pin.IN, Pin.PULL_DOWN)
        self.d3 = Pin(4, Pin.IN, Pin.PULL_DOWN)
        self.d4 = Pin(5, Pin.IN, Pin.PULL_DOWN)
        
        #self.st = Pin(6, Pin.IN, Pin.PULL_DOWN)
        #self.st.irq(trigger=Pin.IRQ_RISING, handler=self.de)
        
        self.st = Pin(7, Pin.IN, Pin.PULL_DOWN)
        self.st.irq(trigger=Pin.IRQ_RISING, handler=self.de)
        
  
    def de(self,pin):
        print("IRQ")
        self.i +=1
        print(self.i)
        
        #print(str(self.d4.value())+str(self.d3.value())+str(self.d2.value())+str(self.d1.value()))
        self.dtmf_code = 0
        self.dtmf_code = self.dtmf_code + self.d1.value() * 1
        self.dtmf_code = self.dtmf_code + self.d2.value() * 2 
        self.dtmf_code = self.dtmf_code + self.d3.value() * 4 
        self.dtmf_code = self.dtmf_code + self.d4.value() * 8 
        #print(self.dtmf_code)
        self.dtmf_char = self.bc[self.dtmf_code]
        print("dtmf_char "+self.dtmf_char)
                    
        if self.dtmf_char == '*':
              print("reset eingabe *")
              self.command = ""
              self.eingabe_mode = True
        elif self.eingabe_mode and self.dtmf_char == '#':
              print("command fertig")
              self.eingabe_mode = False
              print("in dtmf " + self.command)
              self.callback(self.command)        
        elif self.eingabe_mode and self.dtmf_char != '*' and self.dtmf_char != '#':  
              self.command = self.command+str(self.dtmf_char)
              print("eingabe " + self.dtmf_char)


class Morse:

    def __init__(self, ports):
        tim = Timer()
        #tim.init(period=500, mode=Timer.PERIODIC, callback=self.tick)
        self.txt=""
        self.i=0
        self.ports=ports
        self.point_len = 100
        self.strich_len = 300
        self.pause_len = 700

        self.MorseCodes = {
        '0' : "-----",'1' : ".----",'2' : "..---",'3' : "...--",'4' : "....-",'5' : ".....",'6' : "-....",'7' : "--...",'8' : "---..",'9' : "----.",            
        'A' : ".-",'B' : "-...",'C' : "-.-.",'E' : ".",'F' : "..-.",'G' : "--.",'H' : "....",'I' : "..",'J' : ".---",'K' : "-.-",'L' : ".-..",          
        'M' : "--",'N' : "-.",'O' : "---",'P' : ".--.",'Q' : "--.-",'R' : ".-.",'S' : "...",'T' : "-",'U' : "..-",'V' : "...-",'W' : ".--",'X' : "-..-",'Y' : "-.--",'Z' : "--..",
        '$' : "...-..-",'&' : ".-...",'(' : "-.--.",')' : "-.--.-",'+' : ".-.-.",'-' : "-....-",'.' : ".-.-.-",',' : "--..--",'/' : "-..-.",
        ':' : "---...",';' : "-.-.-.",'=' : "-...-",'?' : "..--..",'@' : ".--.-.","'" : ".----.",'"' : ".-..-.",'Ä' : ".-.-",'Ö' : "---.",'Ü' : "..--",'ß' : "···−−··",'_' : "··−−·−",
        ' ' : "space"
        
         #f   '%' : ".........",
         #f   '\'' : ".----.",
         #f '*' : "-..-",
         #f  '<' : ".........",
         #f  '>' : ".........",     
        
        }


    def tick(self,x):  # 0.1 sec   
        self.i=self.i+1
        print("morse:"+str(self.i))
        
    def set_txt(self,txt):
        self.txt=txt
    
    def play_char1(self, c):
        #print("play_char1")
        ps = self.MorseCodes[c]
        if ps == "space":
            print("SPACE", end='')
            #time.sleep_ms(self.pause_len)
        else:
            for e in ps:
                #print("e="+e)
                print(e, end='')
                for p in self.ports:
                    if e == '.':
                        p.on()
                        #time.sleep_ms(self.point_len)
                        p.off()
                    if e == '-':
                        p.on()
                        #time.sleep_ms(self.strich_len)
                        p.off()        
        print(' ', end='')

    
  
    def play_txt(self):    
        print(self.txt)
        for e in self.txt:
            self.play_char1(e)
            time.sleep_ms(self.pause_len)
        print()




    def play_char2(self,c):
        ps = self.MorseCodes[c]
        for e in ps:
            print(e, end='')
            for p in self.ports:
                if e == '.':
                    p.on()
                    time.sleep_ms(50)
                    p.off()
                if e == '-':
                    p.on()
                    time.sleep_ms(150)
                    p.off()        
            time.sleep_ms(200)
        print(' ', end='')


class Port:
    def __init__(self, nr=0, pin=0, mode='s', on_cmd='', off_cmd='', temp_on_cmd='', temp_off_cmd=''):
        
        self.nr = nr
        self.pin = pin
        self.mode = mode # s = switch, b = bake
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd
        self.temp_on_cmd = temp_on_cmd
        self.temp_off_cmd = temp_off_cmd
        self.name="port_"+str(pin)
        
        self.p = Pin(self.pin, Pin.OUT)
    
    def save(self):
        pass
    
    def load(self):
        pass
    
    def set_mode(self,mode):
        self.mode = mode

    def on(self):
        self.p.on()

    def off(self):     
        self.p.off()          


class Bake:
    def __init__(self, txt):
        self.status="none"
        self.ports=[]      
        self.ports.append(Port(nr=1, pin=25, mode='b', on_cmd='11', off_cmd="10", temp_on_cmd='13', temp_off_cmd='14'))
        self.ports.append(Port(nr=2, pin=6,  mode='s', on_cmd='21',  off_cmd='20'))
          
        self.m = Morse(self.ports)
        self.m.set_txt(txt)
        
        self.play = False
        
        # Träger ein  | Pre Zeit | Kennung | Post Zeit   | Träger ein
        self.bake_tim = Timer()    
        self.traeger()

    def ctl(self,cmd):
        print("in bake: " + cmd)
        for e in self.ports:  
                if e.on_cmd == cmd:
                    e.on()
                elif e.off_cmd == cmd:
                    e.off()
                if e.mode == 'b':
                    if e.temp_on_cmd == cmd:
                        pass
                    elif e.temp_off_cmd == cmd:
                        pass      
    
    def print_ports(self):
        for p in self.ports:
            print(p.name)    

    def set_traeger(self):
        for p in self.m.ports:
            if p.mode == 'b':
                p.on()
                
    def reset_traeger(self):
        for p in self.m.ports:
            p.off()
    
    # statemachine methods    
    def traeger(self,x=''):
        self.status="traeger"
        self.set_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=10000, callback=self.pre)

    def pre(self,x):
        self.status="pre"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.play_text)
    
    def play_text(self,x):
        self.play = True
        #self.bake_tim.deinit()
        #self.status="call"
        #self.m.play_txt()
        #self.post()

#     def play_text(self,x):
#         #self.bake_tim.deinit()
#         self.status="call"
#         self.m.play_txt()
#         self.post()

    def post(self):
        self.status="post"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.traeger)


class config:

    def __init__(self, pin, mode='s'):
        pass


def main():    
    print("bake")
    bake = Bake("OE5RNL OE5NVL OE5JAL")
    dtmf = Dtmf(callback=bake.ctl)
    pgm = Pgm()

    m=0
    while True:
        if bake.play:
            
        #print("Bake main:"+str(m)+" "+bake.status)
        time.sleep_ms(500)
        m=m+1

if __name__ == "__main__":
    #print(os.listdir())
    #time.sleep(1)
    #f = open('config.txt', 'w')
    #f.write('Hello again!')
    #f.close()
    #time.sleep(2)
    #f = open('config.txt')
    #print(f.readline(), 'r')
    #time.sleep(1)
    main()





       #comm = machine.UART(1,9600)
       #comm.init(9600, bits=8, parity=None, stop=1, timeout=2000) 
    
    
    #p1=port(25)
    # p2=port(6)
    # p3=port(7)
    # #p4=port(8)
    # #p5=port(9)
    # #p6=port(10)
    # #p7=port(11)

    #m=morse()
    #m.add_port(p1)
    #m.set_txt(">>> OE5VRL")
    #m.set_txt("OE5RNL")
    #m.play_char('A')
    #time.sleep(2)
    #m._play_txt()


    # m.add_port(p2)
    # m.add_port(p3)
    # m.print_ports()

    # c=dtmf()


    # # bake.start()
    # i=0
    # def aa(x):
    #     global i
    #     print(i)
    #     i=i+1

    #bake = Timer()
    #bake.init(mode=Timer.PERIODIC, period=100, callback=aa)


    #bake = Timer()
    # #bake.init(freq=1, mode=Timer.PERIODIC, callback=m.play())


    #pin25 = Pin(25, Pin.OUT) 










