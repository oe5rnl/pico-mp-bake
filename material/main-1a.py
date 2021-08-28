
# OE5VRL Bake

import utime
from machine import UART, Pin, Timer
#import machine
import time
import os
import json

class Port:
    def __init__(self, id='', gpio='', mode='s', on_cmd='', off_cmd='', port_on=False, morse_on_cmd='', morse_off_cmd=''):
        
        self.id = id
        self.gpio = int(gpio)
        self.mode = mode # s = switch, b = bake
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd
        self.morse_on_cmd = morse_on_cmd
        self.morse_off_cmd = morse_off_cmd
        self.name="port_"+str(self.gpio)

        self.port_on = port_on
        self.morse_aktiv = True

        self.p = Pin(self.gpio, Pin.OUT)
        #self.p.off()
        self.p.on()
    
    def set_mode(self,mode):
        self.mode = mode

    def dtmf_on(self):
        self.p.on()
        self.port_on = True

    def dtmf_off(self):
        self.p.off()
        self.port_on = False

    def traeger_on(self):
        # if self.id==0: 
        #     print()
        #     print('ON: '+str(self.mode)+' '+str(self.port_on)+' '+str(self.morse_aktiv))
        if self.mode == 'B' and self.port_on and self.morse_aktiv:
            self.p.on()

    def traeger_off(self):
        # if self.id==0:
        #     print()
        #     print('OFF: '+str(self.mode)+' '+str(self.port_on)+' '+str(self.morse_aktiv))
        if self.mode == 'B' and self.port_on and self.morse_aktiv:
            self.p.off()

    def morse_on(self):
        self.port_on = True
        #print(str(self.mode),str(self.port_on),str(self.morse_aktiv))
        if self.mode == 'B' and self.port_on and self.morse_aktiv:
            self.p.on()

    def morse_off(self):
        if (self.mode == 'B') and self.port_on and self.morse_aktiv:          
            self.p.off()
    
    def morse_temp_on(self): # Morsen einschalten
        self.morse_aktiv = True
        self.p.on()

    def morse_temp_off(self): # Morsen teporär ausschalten
        self.morse_aktiv = False
        self.p.on()
 

class Pgm:
    def __init__(self):
        pass


class pause:
    def __init__(self,d):
        self.d = d
        self.c = self.d
    
    def dec(self):
        self.c -= 1
        if self.c <= 0:
            self.c = self.d
            return True
        return False



class Trigger:
    def __init__(self):
        self.d = False # todo ?
        self.state = 0
        self.ret = False

    def run(self):
        if self.state == 0:
            self.ret = True
            self.state = 1
        
        elif self.state == 1:
            self.ret = False
            if self.d:
                self.state = 2

        elif self.state == 2:
            pass

        return self.ret

    def res(self):
        self.d = True


    # def set(self):
    #     self.d = True

    # def res(self):
    #     self.state = 0


    # def set(self):
    #     if self.doit:
    #         return False
    #     self.doit = True
    #     return True

    # def get(self):
    #     return self.doit
   
    # def res(self):
    #     self.doit=False

        

class Morse:

    def __init__(self, ports, callback):
      
        self.txt=""
        self.callback = callback

        self.ports=ports
        #self.tick_len = 1
        self.tick_len = 10
   
        self.play = False

        self.t = Trigger() #+++

        # state machine variable
        self.state = 0
        self.ci = 0   # index im Text
        self.c = ''   # ein zeichen aus dem Text 
        self.ps = ''  # Punkte und Striche eines Zeichens
        self.psi = 0  # Index in Pukte und Striche eines Zeichens
     

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

        self.tim = Timer()
        self.start_timer()

        #self.speed = 60
        m = 4  # 2 ca 20 wpm = 60 cpm
        self.dauer_punkt = pause(25*m)
        self.dauer_strich = pause(75*m)
        self.pause1 = pause(25*m)
        self.pause3 = pause(75*m)
        self.pause7 = pause(175*m)


    def start_timer(self):
        self.tim.init(period=self.tick_len, mode=Timer.PERIODIC, callback=self.tick)

    def stop_timer(self):
        self.tim.deinit()

    def tick(self,x):  # 50 ms
        ##self.sync()
        if self.play:
            self.play_msg()
            
    def set_txt(self,txt):
        self.txt=txt
    
    def sync(self):
        t = Pin(27, Pin.OUT)
        t.on()
        time.sleep_us(100)
        t.off()
        
    def play_start(self):  
        self.sync()
        self.play = True
 
    def play_bake(self):   #+++
       
        if self.t.run():
            self.sync()
            self.play = True
            self.state = 0
            self.ci = 0   # index im Text
            self.c = ''   # ein zeichen aus dem Text 
            self.ps = ''  # Punkte und Striche eines Zeichens
            self.psi = 0  # Index in Pukte und Striche eines Zeichens      
            self.start_timer()
 

    def ports_on(self):
        for e in self.ports:
            e.morse_on()
    
    def ports_off(self):
        for e in self.ports:
            e.morse_off()        

    def play_msg(self):
        #print(self.state)

        if self.state == 0: # starte morsen
            self.c = self.txt[self.ci]   # c = ein zeichen aus dem Text , ci index im Text
            if self.c == ' ':
                self.state = 95   # Pause zwischen zwei Wörtern
            else:
                self.ps = self.MorseCodes[self.c]  # das Morsezeichen mit . und -
                self.state = 1

        elif self.state == 95:
            if self.pause7.dec():  # Zeichendauer ende 
                self.state = 98

        # ps --- . ..... .-. -. .-..
        elif self.state == 1: 
            if self.ps[self.psi] == '.':
                self.state = 100  

            elif self.ps[self.psi] == '-':
                self.state = 300              
            self.ports_on()   
           
        elif self.state == 100:  
            if self.dauer_punkt.dec():  # Zeichendauer ende
                self.ports_off() 
                self.state = 99

        elif self.state == 300:  
            if self.dauer_strich.dec():  # Zeichendauer ende
                self.ports_off() 
                self.state = 99

        elif self.state == 99:     # pause zwischen Punkt und Strich im morsezeichen      
            if self.pause1.dec():  
                self.state = 97
                
        elif self.state == 97: # Nächstes Element im Morsezeichen oder neues Morsezeichen holen
            self.psi += 1
            if self.psi >=  len(self.ps):
                self.state = 96  # Morsezeichen fertig - zeit zwischen Morsezeichen starten
            else:
                self.state = 1

        elif self.state == 96: # Zeit zwischen Morsezeichen
            if self.pause3.dec():  
                self.state = 98

        elif self.state == 98:  # neues zeichenaus self.txt zeichen holen 
            self.ci += 1
            if self.ci >= len(self.txt):
                self.state = 1000
            else:
                self.psi = 0
                self.state = 0
    
        elif self.state == 1000: # ende der Textausgabe
            self.play = False
            self.state = 0
            self.ci = 0
            self.psi = 0
            self.ports_off()
            self.callback() # msg output done -> send pre 

  
class Config:

    def __init__(self):
        
        self.config_file = 'config.json'

        self.c = {
                'saves': '0',
                'Version': '0.99',
                'CW Speed': '100',
                'Bakentext': 'OE5RNL',
                'On Time': '5',
                'Pre Time': '2',
                'Post Time':'2',
                'CW Off Timeout': '20',
                'ports':[    
                    {'id':'0','Name':'LED',   'Mode':'B','gpio':'25','On': '01','Off':'00','Port On':'1', 'CW Off':'03','CW On':'04'},
                    {'id':'1','Name':'10 GHZ','Mode':'B','gpio':'16','On': '11','Off':'10','Port On':'1', 'CW Off':'13','CW On':'14'},
                    {'id':'2','Name':'24 GHZ','Mode':'B','gpio':'17','On': '21','Off':'20','Port On':'1', 'CW Off':'23','CW On':'24'},
                    {'id':'3','Name':'74 GHZ','Mode':'B','gpio':'18','On': '31','Off':'30','Port On':'0', 'CW Off':'33','CW On':'34'},
                    {'id':'4','Name':'FREI',  'Mode':'S','gpio':'19','On': '41','Off':'40','Port On':'0', 'CW Off':'43','CW On':'44'},
                    {'id':'5','Name':'FREI',  'Mode':'S','gpio':'20','On': '51','Off':'50','Port On':'0', 'CW Off':'53','CW On':'54'},
                    {'id':'6','Name':'FREI',  'Mode':'S','gpio':'21','On': '61','Off':'60','Port On':'0', 'CW Off':'63','CW On':'64'},
                    {'id':'7','Name':'FREI',  'Mode':'S','gpio':'22','On': '71','Off':'70','Port On':'0', 'CW Off':'73','CW On':'74'},
                ]
                }
        
     
        self.load()

    def get_attr(self, a):
        return self.c[a]

    def set_attr(self,a,v):
        self.c[a] = v

    def get_port_attr(self,p,a):
        return self.c['ports'][p][a]

    def set_port_attr(self,p,a,v):
        self.c['ports'][p][a] = v

    def get_port(self,id):
        return self.c['ports'][id]

    def load(self):
        try:
            self.f = open(self.config_file,'r')
            self.txt = self.f.read()
            self.c = json.loads(self.txt)

        except OSError:  # open failed
            self.c = self.c

    def save(self):
        print('sa')
        self.set_attr('saves',str(int(self.get_attr('saves'))+1))
        print('sb')
        with open(self.config_file, 'w') as fp:
            print('sc')
            json.dump(self.c, fp)
        print('sd')
        #machine.reset()

    def get_intatt(self,a):
        return int(self.get_attr(a))*1000

def a():
    pass


def print_ports(ports):
    for p in ports:
        #print(p.id) 
        print(ports)   
        pass


def main():
    config = Config()

    ports=[]      
    for i in range(8):
        ports.append(Port(  id=             int(config.get_port_attr(i,'id')),
                            gpio=           config.get_port_attr(i,'gpio'), 
                            mode=           config.get_port_attr(i,'Mode'), 
                            on_cmd=         config.get_port_attr(i,'On'), 
                            off_cmd=        config.get_port_attr(i,'Off'),
                            port_on=        config.get_port_attr(i,'Port On'),
                            morse_off_cmd=  config.get_port_attr(i,'CW Off'), 
                            morse_on_cmd=   config.get_port_attr(i,'CW On')
                            )
                    )        
    #pgm = Pgm()
    morse = Morse(ports,callback=a)
  

    #tim = Timer()
    #tim.init(mode=Timer.PERIODIC, period=5, callback=self.tick)


    print(ports)

    morse.set_txt('OE5RNL')
    morse.start_timer()

    m=0
    while True:
        #print('m='+str(m))
        m += 1
        morse.sync()
        morse.play_start1()
        time.sleep_ms(5)

        # for e in ports:
        #     e.morse_on()
        # #time.sleep_ms(1)
        # for e in ports:
        #     e.morse_off()

if __name__ == "__main__":
    main()


 