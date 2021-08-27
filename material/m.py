import utime
from machine import UART, Pin, Timer
import time
import os
import json
from machine import WDT


class Wdt:

    def __init__(self,t):
        self.state = False
        self.t = t

    # we can't stop the wd after start !
    def start(self,v):
        if v:
            self.wd = WDT(timeout=self.t)
            self.state = True
             
    def feed(self):
        if self.state:
            self.wd.feed()

class Config:

    def __init__(self):

        self.wd = Wdt(8000)
        
        self.config_file = 'config.json'

        self.c = {
                'saves': '0',
                'Version': '0.99',
                'CW Speed': '100',
                'Bakentext': 'OE5RNL',
                'On Time': '2',
                'Pre Time': '2',
                'Post Time':'2',
                'CW Off Timeout': '20',
                'ports':[    
                    {'id':'0','Name':'LED',   'Mode':'B','gpio':'25','On': '01','Off':'00','Port On':'1', 'CW Off':'03','CW On':'04'},
                    {'id':'1','Name':'10 GHZ','Mode':'B','gpio':'16','On': '11','Off':'10','Port On':'1', 'CW Off':'13','CW On':'14'},
                    {'id':'2','Name':'24 GHZ','Mode':'S','gpio':'17','On': '21','Off':'20','Port On':'1', 'CW Off':'23','CW On':'24'},
                    {'id':'3','Name':'74 GHZ','Mode':'S','gpio':'18','On': '31','Off':'30','Port On':'0', 'CW Off':'33','CW On':'34'},
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
            print('config from fs loaded')
        except: 
            print('load failed -  use default')
            self.c = self.c

    def save(self):
        self.set_attr('saves',str(int(self.get_attr('saves'))+1))
        with open(self.config_file, 'w') as fp:
            print('sc')
            json.dump(self.c, fp)

        print(self.c)

    def get_intatt(self,a):
        return int(self.get_attr(a))*1000

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
        self.p.off()
    
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
 


class Morse:

    def __init__(self, ports, callback):
      
        self.txt=""
        self.callback = callback

        self.ports=ports
        self.tick_len = 1
   
        self.play = False

        # state machine variable
        self.state = -1
        self.len_txt = 0
        self.chi = 0      # index im Text
        self.ch = ''      # ein zeichen aus dem Text 
        self.cwch = ''    # Punkte und Striche eines Zeichens
        self.cwchi = 0    # Index in Pukte und Striche eines Zeichens
        self.len_cwch = 0 # 
        #self.len_txt=0 
        self.last_state = 0

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
        #self.start_timer()

        # dit length in milliseconds : 240ms =  20bpm =  5 wpm
        # dit length in milliseconds : 100ms =  60bpm = 12 wpm
        # dit length in milliseconds : 60ms  = 100bpm = 20 wpm
        # dit length in milliseconds :  20ms = 300bpm = 60 wpm
        bpm = 60
        wpm = bpm/5
        ms = 60/(50*(bpm/5))*1000

        print("".format(bpm,wpm,))

        #self.dauer_punkt = Pause(ms)
        #self.dauer_strich = Pause(ms*3)
        
        #self.pause1 = Pause(ms*1)
        #self.pause3 = Pause(ms*3)
        #self.pause7 = Pause(ms*7) # 7


        self.t_punkt  = int(ms)
        self.t_strich = int(ms * 3)
        self.t_pause1 = int(ms * 1)
        self.t_pause3 = int(ms * 3)
        self.t_pause7 = int(ms * 7)

        print("bpm={0} wpm={1} punkt={2} strich={3}".format(bpm, wpm, ms, ms*3),end='')


        self.i = 0
        self.next_state = -9

    def start_timer(self):
        #self.tim.init(period=self.tick_len, mode=Timer.PERIODIC, callback=self.tick)
        pass

    def stop_timer(self):
        #self.tim.deinit()
        pass

    def _tick(self,x):  # 50 ms
        #if self.play:
        #    self.play_msg()
        pass

    def set_txt(self,txt):
        self.txt = txt  # Text ist durch console schon gestrippt und keine doppelten ' '
        self.len_txt = len(self.txt)
    
    def sync(self):
        t = Pin(27, Pin.OUT)
        t.on()
        time.sleep_us(100)
        t.off()
        
    def play_start(self):  
        #self.sync()
        #self.play = True
        pass
 
    def ports_on(self):
        for e in self.ports:
            e.morse_on()
    
    def ports_off(self):
        for e in self.ports:
            e.morse_off()        

    def dummy(self,x):
        self.state = self.next_state
        #print('*')
        pass

    def play_msg(self):
    
        # self.i += 1
        # if self.i <= 1000:
        #     #self.i = 0
        #     return False
        #     pass

        #print('state='+str(self.state))

        if self.state == -1:
            #print('state-1='+str(self.state))
            #print(self.txt)
            self.ch=''
            self.chi = 0
            self.cwch =''
            self.cwchi = 0
            self.state = 0

        if self.state == 0: 
            #print('state0='+str(self.state))
            # starte morsen eines Zeichen
            if len(self.txt)>0:
                self.ch = self.txt[self.chi]   # ch = ein zeichen aus dem Text , chi index im Text
                self.cwch = self.MorseCodes[self.ch]  # Morsecode für ein Zeichen holen
                self.len_cwch = len(self.cwch)    
                #print('to 1')      
                self.state = 1 
            else:
                #print('to 1000')   
                self.state = 1000  # Kein Zeichen im Text

        # ps --- . ..... .-. -. .-..
        elif self.state == 1: 
            #print('state1='+str(self.state))
            if self.cwch[self.cwchi] == '.':
                self.tim.init(period=self.t_punkt, mode=Timer.ONE_SHOT, callback=self.dummy)
                self.next_state = 97
                self.state = 999  
                #print('to 100')

            elif self.cwch[self.cwchi] == '-':
                #print('-')
                self.tim.init(period=self.t_strich, mode=Timer.ONE_SHOT, callback=self.dummy)
                #print('öööööööööö')
                self.next_state = 97
                self.state = 999              
            
            self.ports_on()   

        elif self.state == 97:
            #print('state97='+str(self.state))
            # Noch ein Element im Morsezeichen
            # oder nächstes Mossezeichen
            # oder Textende      
            #             

            self.ports_off() 
            #print('in 97')  

            self.cwchi += 1
            if self.cwchi < len(self.cwch): 
                # Ja noch ein Element im Morsezeichen vorhanden, Elementpause einleiten
                self.state = 99
            else: 
                # Kein Element im Moresezeichen mehr da == Morsezeichen fertig 
                self.chi += 1
                if self.chi < len(self.txt):
                    # ja es gibt noch Zeichen im Text
                    if self.txt[self.chi] == ' ':
                        # Wortende
                        self.chi += 1
                        self.state = 95 
                    else:
                        # nachstes cw Zeichen ausgeben, pause 3 einleiten              
                        self.state = 96
                    self.cwchi = 0
                else:
                    # keine Zeichen im Text mehr -> txt Ende
                    self.state = 1000     

      
        elif self.state == 99:   # pause zwischen Elementen im morsezeichen
            #if self.pause1.dec():  
            #    self.state = 1
            self.tim.init(period=self.t_pause1, mode=Timer.ONE_SHOT, callback=self.dummy)
            self.state = 999
            self.next_state = 1            

        elif self.state == 95:     
            # Leezeichen zwischen zwei wörter
            #if self.pause7.dec():  
            #    self.state = 0
            self.tim.init(period=self.t_pause7, mode=Timer.ONE_SHOT, callback=self.dummy)
            self.state = 999
            self.next_state = 0           

                               
        elif self.state == 96:   # Zeit zwischen Morsezeichen
            # if self.pause3.dec():  
            #     self.state = 0
            self.tim.init(period=self.t_pause3, mode=Timer.ONE_SHOT, callback=self.dummy)
            self.state = 999
            self.next_state = 0          
 

        elif self.state == 1000: # ende der Textausgabe
            self.play = False
            self.ch=''
            self.chi = 0
            self.cwch=''
            self.cwchi = 0
            self.state = 0
            self.ports_off()
            #self.callback() # msg output done -> send pre 
            return False

        # waite state
        elif self.state == 999:
            #print('999')
            pass

        #time.sleep_ms(2)
        return True

        #if self.last_state != self.state:
        #    print(self.state)
        #self.last_state = self.state 



def d():
    print('d')
    pass  

def main():

    config = Config()
    ports=[]      
    for i in range(8):
        ports.append(Port( id=             int(config.get_port_attr(i,'id')),
                                gpio=           config.get_port_attr(i,'gpio'), 
                                mode=           config.get_port_attr(i,'Mode'), 
                                on_cmd=         config.get_port_attr(i,'On'), 
                                off_cmd=        config.get_port_attr(i,'Off'),
                                port_on=        config.get_port_attr(i,'Port On'),
                                morse_off_cmd=  config.get_port_attr(i,'CW Off'), 
                                morse_on_cmd=   config.get_port_attr(i,'CW On')
                                )
                            )    


    m = Morse(ports, d)

    m.set_txt('OE5RNL OE5NVL')
    m.sync()
    while m.play_msg():
        pass

if __name__ == "__main__":
    main()


