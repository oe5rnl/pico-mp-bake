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
# https://morsecode.world/international/timing.html

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
        if self.u.any():
            c=self.u.read(1).decode()
            print(c, end='')
            
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
        
        self.bc = {1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'0',11:'*',12:'#',13:'A',14:'B',15:'C',0:'D'}

        self.d1 = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.d2 = Pin(3, Pin.IN, Pin.PULL_DOWN)
        self.d3 = Pin(4, Pin.IN, Pin.PULL_DOWN)
        self.d4 = Pin(5, Pin.IN, Pin.PULL_DOWN)
        self.st = Pin(7, Pin.IN, Pin.PULL_DOWN)

        self.st.irq(trigger=Pin.IRQ_RISING, handler=self.de)
  
    def de(self,pin):
        print("IRQ")
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
        self.active = True
      
        self.p = Pin(self.pin, Pin.OUT)
    
    def save(self):
        pass
    
    def load(self):
        pass
    
    def set_mode(self,mode):
        self.mode = mode

    def on(self):
        if self.active:
            self.p.on()

    def off(self):     
        if self.active:
            self.p.off()          


class Morse:

    def __init__(self, ports, callback):
      
        self.txt=""
        self.callback = callback

        self.ports=ports
        self.point_len = 9
    
        self.play = False


        # state machine variable
        self.m_state = 0
        self.ci = 0
        self.c = ''
        self.ps = ''
        self.mi = 0
        self.mclen =0
        self.p7 = 4

        self.MorseCodes = {
        '0' : "-----",'1' : ".----",'2' : "..---",'3' : "...--",'4' : "....-",'5' : ".....",'6' : "-....",'7' : "--...",
        '8' : "---..",'9' : "----.",'A' : ".-",'B' : "-...",'C' : "-.-.",'E' : ".",'F' : "..-.",'G' : "--.",'H' : "....",
        'I' : "..",'J' : ".---",'K' : "-.-",'L' : ".-..",          
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

        tim = Timer()
        tim.init(period=self.point_len, mode=Timer.PERIODIC, callback=self.tick)

    def tick(self,x):  # 50 ms
        if self.play:
            self.playx()
            
    def set_txt(self,txt):
        self.txt=txt
    
    def pause7(self):
        self.p7 -= 1
        if self.p7 == 0:
            self.p7 = 4
            return True
        return False

    def sync(self):
        t = Pin(27, Pin.OUT)
        t.on()
        time.sleep_us(100)
        t.off()
        
    def play_start(self):  
        self.sync()
        self.play = True
 
    def ports_on(self):
        for e in self.ports:
            e.on()
    
    def ports_off(self):
        for e in self.ports:
            e.off()        

    def playx(self):
       
        if self.m_state == 0: # starte morsen
            self.c = self.txt[self.ci]   # ein zeichen aus dem Text 
            self.ps = self.MorseCodes[self.c]  # das Morsezeichen mit . und -
            self.m_state = 1

        # ps --- . ..... .-. -. .-..
        elif self.m_state == 1: 
            if self.ps[self.mi] == '.':
                self.m_state = 100  
            elif self.ps[self.mi] == '-':
                self.m_state = 300 
                self.mclen = 3
            self.ports_on()   
           
        elif self.m_state == 100:  
            self.ports_off()
            if self.pause7():  # pause innerhalb morsezeichen
                self.m_state = 99

        elif self.m_state == 300:  
            self.mclen -= 1
            if self.mclen <= 0:
                self.ports_off()
                if self.pause7(): # pause innerhalb morsezeichen
                    self.m_state = 99

        elif self.m_state == 99:   # pause zwischen morsezeichen
            if self.pause7():
                self.m_state = 97
                
        elif self.m_state == 97: # nächsten . oder - aus morsezeichen holen
            self.mi += 1
            if self.mi >=  len(self.ps):
                self.m_state = 98  # Morsezeichen fertig
            else:
                self.m_state = 1

        elif self.m_state == 98:  # neues zeichenaus self.txt zeichen holen 
            self.ci += 1
            if self.ci >= len(self.txt):
                self.m_state = 1000
            else:
                self.mi = 0
                self.m_state = 0
    
        elif self.m_state == 1000: # ende der Textausgabe
            self.play = False
            self.m_state = 0
            self.ci = 0
            self.mi = 0
            self.ports_off()
            self.callback()
            

class Bake:
    def __init__(self, txt):
        self.status="none"
        self.ports=[]      
        self.ports.append(Port(nr=0, pin=25, mode='b', on_cmd='01', off_cmd="00", temp_on_cmd='03', temp_off_cmd='04'))

        self.ports.append(Port(nr=1, pin=16,  mode='b', on_cmd='11', off_cmd='10', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=2, pin=17,  mode='b', on_cmd='21', off_cmd='20', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=3, pin=18,  mode='b', on_cmd='31', off_cmd='30', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=4, pin=19,  mode='b', on_cmd='41', off_cmd='40', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=5, pin=20,  mode='b', on_cmd='51', off_cmd='50', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=6, pin=21,  mode='b', on_cmd='61', off_cmd='60', temp_on_cmd='23', temp_off_cmd='24'))
        self.ports.append(Port(nr=7, pin=22,  mode='b', on_cmd='71', off_cmd='70', temp_on_cmd='23', temp_off_cmd='24'))

        #for e in self.ports:   
        #    print(e.on_cmd, " ", e.off_cmd, " ", e.temp_on_cmd, " ",e.temp_off_cmd)

        self.m = Morse(self.ports,self.playende)
        self.m.set_txt(txt)

        # Träger ein  | Pre Zeit | Kennung | Post Zeit   | Träger ein
        self.bake_tim = Timer()    
        #self.bake_tim.init(mode=Timer.PERIODIC, period=2000, callback=self.test)
        
        self.traeger()

 
    def playende(self):
        print("Playende")
        self.post()

    def ctl(self,cmd):
        print("in bake: " + cmd)
        for e in self.ports:  
            if e.on_cmd == cmd:
                e.on() 
                e.active = True
            elif e.off_cmd == cmd:           
                e.off()     
                e.active = False        
            # if e.mode == 'b':
            #     if e.temp_on_cmd == cmd:
            #         pass
            #     elif e.temp_off_cmd == cmd:
            #         pass      
    
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
    
    def test(self,x):
        self.m.play_start() 

    # statemachine methods    
    def traeger(self,x=''):
        self.status="traeger"
        self.set_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=5000, callback=self.pre)

    def pre(self,x):
        self.status="pre"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.play_text)
    
    def play_text(self,x):
        self.status="call"
        self.m.play_start() 

    def post(self):
        self.status="post"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.traeger)


class config:

    def __init__(self, pin, mode='s'):
        pass



def main():    
    print("bake")
    bake = Bake("OE5RNL")
    dtmf = Dtmf(callback=bake.ctl)
    pgm = Pgm()

    
    # def tick(x):
    #     t = Pin(17, Pin.OUT)

    #     t.on()
    #     time.sleep_ms(3000)
    #     t.off()
    #     time.sleep_ms(3000)

    # tim = Timer()
    # tim.init(period=1, mode=Timer.PERIODIC, callback=tick)

    # t = Pin(17, Pin.OUT)
    #t.off()
    while True:
        time.sleep_ms(500)
        # print('*')
        # t.on()
        # time.sleep_ms(3000)
        # t.off()
        # time.sleep_ms(3000)


if __name__ == "__main__":
    main()


