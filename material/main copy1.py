
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
# https://kofler.info/wp-content/uploads/pico-gpios.png
# https://www.accessengineeringlibrary.com/content/book/9781260117585/back-matter/appendix1

code_version = '0.6'

class Line:

    def __init__(self,com):
        self.txt=''
        self.com = com
        self.len = 0

    def read_char(self):
        while True:
            if self.com.any():
                c=self.com.read(1)
                if c != None:
                    return c        

    def g(self,c,a):
        # isnumeric würde auch für 1/2 etc gelten
        num   = ['0','1','2','3','4','5','6','7','8','9']
        alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q',
                 'R','S','T','U','V','W','X','Y','Z',' '
        ]  
        ret = False
        ch = chr(ord(c))
        if a == 'a':
            if ch in alpha or ch in num:
                ret = True
        elif a == 'n':
            if ch  in num:
                ret = True
        else:
            ret = False
        return ret

    def read(self,e, default, cwb=''):
        txt = default
        l = len(txt)       
        maxlen = e[1]
        alnum = e[2]
        wb = e[3]

        self.com.write(txt)

        while True:
            c = self.read_char()       
            if ord(c) == 0x7f:  # bs           
                if l > 0:
                    l -= 1
                    txt = txt[:-1]
                    self.com.write(c) #bs
            else: 
                if (l <= maxlen-1):
                    if self.g(c,alnum):
                        l += 1
                        txt = txt + c
                        self.com.write(c)
                    else:
                        print('xx')
                        print(c)
                        print('---')
            if c == b'\r':
                if l>0:
                    # trim beide Seiten, keine doppelten leerzeichen
                    return " ".join(txt.decode().strip().split())

            #print("txt: |"+txt.decode()+'| len='+str(l))       
        return txt


class Pgm:
    
    def __init__(self, config, callback):
        
        self.i=0
        self.stop_timer = callback
        self.command = ""
        self.cmode = False
        self.config = config
        self.c = b''
        self.prompt = b'\r\np(edit port), a(edit Allgemein), r(eset) c(print config) s(ave) >'
        self.ueberschrift = "{0:^10}{1:^10}{2:<10}{3:^10}{4:^10}{5:^10}{6:^10}{6:^10}"
        self.werte       = "{0:^10}{1:^10}{2:<10}{3:^10}{4:^10}{5:^10}{6:^10}{6:^10}"

        self.u = UART(id=0, baudrate=9600, bits=8, parity=None, stop=1, timeout=10, rxbuf=256, txbuf=256)
        self.flush()
        #self.u.irq( UART.RX_ANY , Priorität = 1 , Handler = uart_rx , Wake = machine.IDLE )
        self.u.write(b'\n\r\n\r\n\r\n\rBeacon-Controller by OE5RNL & OE5NVL für OE5VRL\n\r\n\r')
        
        self.u.write(b'Code Version   : '+code_version+'\r\n')
        self.u.write(b'Config Version : '+config.get_attr('Version')+'\r\n')
        self.u.write(b'Saves          : '+config.get_attr('saves')+'\r\n')
        self.u.write(b'Core Temerature: '+self.get_core_temperature()+'\n\r')
        self.u.write(b'\n\rpress Enter for config >')
        self.line = Line(self.u)   #.encode('utf-8')

    def flush(self): 
        while self.u.any():
            self.u.read()
      
    def read_char(self):
        while True:
            if self.u.any():
                c=self.u.read(1)
                if c != None:
                    return c

    def uart_cmd(self):   
        self.c=self.u.read(1)
        if self.c == None:
            return
        if self.c == b'\r':
            self.do_it()
    
    def do_it(self):  
        self.print_config()
        self.u.write(b' ')
        self.u.write(self.prompt)

        while True:     
            c=self.u.read(1) 
            if c != None:      
                if c == b'c':
                    self.print_config()               
                elif c == b'p':
                    self.edit_port()
                elif c == b'a':
                    self.edit_allgemein()
                elif c == b'r':
                    machine.reset( )
                elif c == b's':
                    self.stop_timer()
                    self.config.save()
            
                self.u.write(self.prompt)
 

        #self.u.write(b'\n\rende\n\r')
        
    def crlf(self):
        self.u.write(b'\r\n')

    def edit_port(self):
        self.u.write(b'\r\nPort number: ')
        c=self.read_char()
        i = int.from_bytes(c,'big')-48
        self.u.write(c)
        self.crlf()

        if c in [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7']:
            key = [['Name',15,'a',''],['Mode',1,'a','bs'],['On',10,'n',''],['Off',10,'n',''],['CW Off',10,'n',''],['CW On',10,'n','']]
            f = "Edit Port{0} {1:<7}Aktuell: {2:<7} Neu: "
            for e in key:                       
                if self.getconfig.c['ports'][i]['Mode'] == 's' and (e == 'CW Off' or e == 'CW On'):
                    pass
                else:
                    self.u.write(f.format(i, e[0], self.config.c['ports'][i][e[0]].encode('utf-8'),''))
                    line = self.line.read(e, default=self.config.c['ports'][i][e[0]].encode('utf-8'))
                    self.config.c['ports'][i][e[0]]=line
                    self.crlf()
               
    def edit_allgemein(self):
        self.crlf()
        key = [['CW Speed',3,'n',''],['Bakentext',50,'a',''],['On Time',3,'n',''],['Pre Time',2,'n',''],['Post Time',2,'n',''],['CW Off Timeout',4,'n','']]
        f = "Edit {0:<17} Aktuell: {1:<7} Neu: "
        for e in key:       
            self.u.write(f.format(e[0],self.config.c[e[0]].encode('utf-8')))
            line = self.line.read(e, default=self.config.c[e[0]].encode('utf-8'))
            self.config.c[e[0]]=line
            self.crlf()
    
    def print_config(self):
        self.u.write(b'Aktuelle Konfig\n\r\r\n')
        self.u.write(b'Version   : '+self.config.get_attr('Version')+'\r\n')
        self.u.write(b'CW Speed  : '+self.config.get_attr('CW Speed')+'\r\n') 
        self.u.write(b'Bakentext : '+self.config.get_attr('Bakentext')+'\r\n')
        self.u.write(b'On Time   : '+self.config.get_attr('On Time')+'\r\n')    
        self.u.write(b'Pre Time  : '+self.config.get_attr('Pre Time')+'\r\n')
        self.u.write(b'Post Time : '+self.config.get_attr('Post Time')+'\r\n')
        self.u.write(b'CW Timeout: '+self.config.get_attr('CW Off Timeout')+'\r\n')
        self.u.write(b'\r\n')
        
        self.u.write(self.ueberschrift.format('Port','Status','Name','Mode','On','Off','CW aus','CW ein')+'\r\n')    
        for i in range(0,7):
            self.show_port_data(i)
                                                        
    def show_port_data(self,i):
        if self.config.get_port_attr(i,'Mode') == 'b':
            self.u.write(self.werte.format( self.config.get_port_attr(i,'id'), 
                                            self.config.get_port_attr(i,'port_on'),    
                                            self.config.get_port_attr(i,'Name'),
                                            self.config.get_port_attr(i,'Mode'),   
                                            self.config.get_port_attr(i,'On'),     
                                            self.config.get_port_attr(i,'Off'),
                                            self.config.get_port_attr(i,'CW Off'), 
                                            self.config.get_port_attr(i,'CW On')
                                          )+'\r\n'
                        )

        if self.config.get_port_attr(i,'Mode') == 's':
            self.u.write(self.werte.format( self.config.get_port_attr(i,'id'), 
                                            self.config.get_port_attr(i,'port_on'),       
                                            self.config.get_port_attr(i,'Name'),
                                            self.config.get_port_attr(i,'Mode'),   
                                            self.config.get_port_attr(i,'On'),     
                                            self.config.get_port_attr(i,'Off'),
                                            b'',b''
                                          )+'\r\n'
                        )
     
    def t(self,b):
        if b:
            return('Ein')
        else:
            return('Aus')

    def get_core_temperature(self):
        sensor_temp = machine.ADC(4)
        conversion_factor = 3.3 / (65535)
        #reading = sensor_temp.read_u16() * conversion_factor 
        temp = 27 - (sensor_temp.read_u16() * conversion_factor - 0.706)/0.001721
        return "{0:.2f}".format(temp)


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
        #print("IRQ")
        self.dtmf_code = 0
        self.dtmf_code = self.dtmf_code + self.d1.value() * 1
        self.dtmf_code = self.dtmf_code + self.d2.value() * 2 
        self.dtmf_code = self.dtmf_code + self.d3.value() * 4 
        self.dtmf_code = self.dtmf_code + self.d4.value() * 8 

        self.dtmf_char = self.bc[self.dtmf_code]
              
        if self.dtmf_char == '*':
              #print("reset eingabe *")
              self.command = ""
              self.eingabe_mode = True
        elif self.eingabe_mode and self.dtmf_char == '#':
              #print("command fertig")
              self.eingabe_mode = False
              #print("in dtmf " + self.command)
              self.callback(self.command)        
        elif self.eingabe_mode and self.dtmf_char != '*' and self.dtmf_char != '#':  
              self.command = self.command+str(self.dtmf_char)
              #print("eingabe " + self.dtmf_char)


class Port:
    def __init__(self, nr='', gpio='', mode='s', on_cmd='', off_cmd='', port_on=False, morse_on_cmd='', morse_off_cmd=''):
        
        self.nr = nr
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
        if self.mode == 'b' and self.port_on and self.morse_aktiv:
            self.p.on()

    def traeger_off(self):
        if self.mode == 'b' and self.port_on and self.morse_aktiv:
            self.p.off()

    def morse_on(self):
        if self.mode == 'b' and self.port_on and self.morse_aktiv:
            self.p.on()

    def morse_off(self):
        if (self.mode == 'b') and self.port_on and self.morse_aktiv:          
            self.p.off()
    
    def morse_temp_on(self): # Morsen einschalten
        self.morse_aktiv = True
        self.p.on()

    def morse_temp_off(self): # Morsen teporär ausschalten
        self.morse_aktiv = False
        self.p.on()
 

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

class Timeout():

    def __init__(self, ports):
        
        self.timers = [ {'t':-99,'f':object},{'t':-99,'f':object},{'t':-99,'f':object},{'t':-99,'f':object},
                        {'t':-99,'f':object},{'t':-99,'f':object},{'t':-99,'f':object},{'t':-99,'f':object}                 
                      ]
     
        self.tim = Timer()
        self.start_timer()

    def stop_timer(self):
        self.tim.deinit()

    def start_timer(self):
        self.tim.init(mode=Timer.PERIODIC, period=1000, callback=self.tick)

    def tick(self,x):
        for i in range(0,len(self.timers)):
            if self.timers[i]['t'] != -99:
                if  self.timers[i]['t'] > 0:
                    self.timers[i]['t'] = self.timers[i]['t'] - 1
                else:
                    self.timers[i]['t'] = -99
                    self.timers[i]['f']()

    def set(self, nr, t, f):
        self.timers[nr]['f'] = f
        self.timers[nr]['t'] = t
 

class Morse:

    def __init__(self, ports, callback):
      
        self.txt=""
        self.callback = callback

        self.ports=ports
        self.tick_len = 1
   
        self.play = False

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

  
class Bake:
    def __init__(self, bc, txt=''):
        self.status="none"
        self.bc = bc
        self.save = False

        self.ports=[]      
        self.ports.append(Port(nr=0, gpio=bc.c['ports'][0]['gpio'], mode=bc.c['ports'][0]['Mode'], on_cmd=bc.c['ports'][0]['On'], off_cmd=bc.c['ports'][0]['Off'],port_on=bc.c['ports'][0]['port_on'], morse_off_cmd=bc.c['ports'][0]['CW Off'], morse_on_cmd=bc.c['ports'][0]['CW On']))        
        self.ports.append(Port(nr=1, gpio=bc.c['ports'][1]['gpio'], mode=bc.c['ports'][1]['Mode'], on_cmd=bc.c['ports'][1]['On'], off_cmd=bc.c['ports'][1]['Off'],port_on=bc.c['ports'][1]['port_on'], morse_off_cmd=bc.c['ports'][1]['CW Off'], morse_on_cmd=bc.c['ports'][1]['CW On']))        
        self.ports.append(Port(nr=2, gpio=bc.c['ports'][2]['gpio'], mode=bc.c['ports'][2]['Mode'], on_cmd=bc.c['ports'][2]['On'], off_cmd=bc.c['ports'][2]['Off'],port_on=bc.c['ports'][2]['port_on'], morse_off_cmd=bc.c['ports'][2]['CW Off'], morse_on_cmd=bc.c['ports'][2]['CW On']))
        self.ports.append(Port(nr=3, gpio=bc.c['ports'][3]['gpio'], mode=bc.c['ports'][3]['Mode'], on_cmd=bc.c['ports'][3]['On'], off_cmd=bc.c['ports'][3]['Off'],port_on=bc.c['ports'][3]['port_on'], morse_off_cmd=bc.c['ports'][3]['CW Off'], morse_on_cmd=bc.c['ports'][3]['CW On']))
        self.ports.append(Port(nr=4, gpio=bc.c['ports'][4]['gpio'], mode=bc.c['ports'][4]['Mode'], on_cmd=bc.c['ports'][4]['On'], off_cmd=bc.c['ports'][4]['Off'],port_on=bc.c['ports'][4]['port_on'], morse_off_cmd=bc.c['ports'][4]['CW Off'], morse_on_cmd=bc.c['ports'][4]['CW On']))
        self.ports.append(Port(nr=5, gpio=bc.c['ports'][5]['gpio'], mode=bc.c['ports'][5]['Mode'], on_cmd=bc.c['ports'][5]['On'], off_cmd=bc.c['ports'][5]['Off'],port_on=bc.c['ports'][5]['port_on'], morse_off_cmd=bc.c['ports'][5]['CW Off'], morse_on_cmd=bc.c['ports'][5]['CW On']))
        self.ports.append(Port(nr=6, gpio=bc.c['ports'][6]['gpio'], mode=bc.c['ports'][6]['Mode'], on_cmd=bc.c['ports'][6]['On'], off_cmd=bc.c['ports'][6]['Off'],port_on=bc.c['ports'][6]['port_on'], morse_off_cmd=bc.c['ports'][6]['CW Off'], morse_on_cmd=bc.c['ports'][6]['CW On']))
        self.ports.append(Port(nr=7, gpio=bc.c['ports'][7]['gpio'], mode=bc.c['ports'][7]['Mode'], on_cmd=bc.c['ports'][7]['On'], off_cmd=bc.c['ports'][7]['Off'],port_on=bc.c['ports'][7]['port_on'], morse_off_cmd=bc.c['ports'][7]['CW Off'], morse_on_cmd=bc.c['ports'][7]['CW On']))

        self.timeout = Timeout(self.ports)
        self.m = Morse(self.ports,self.playende)

        # Träger ein  | Pre Zeit | Kennung | Post Zeit   | Träger ein
        self.bake_tim = Timer()   
  
        self.traeger()    

    def stop_timer(self):
        self.m.stop_timer()
        self.bake_tim.deinit()    
        self.timeout.stop_timer()
      
    def start_timer(self):
        self.timeout.start_timer()  
        self.m.start_timer()
        self.traeger()    
  
    def playende(self):
        #print("Playende")
        self.post()

    def ctl(self,cmd):
        print('bake.ctl-1')
        for p in self.ports:  
            if p.on_cmd == cmd:
                p.dtmf_on() 
                #self.bc.ports['']  ####################
            elif p.off_cmd == cmd:           
                p.dtmf_off()     

            elif p.morse_on_cmd == cmd:
                p.morse_temp_on() # Morsen einschalten       
            elif p.morse_off_cmd == cmd:
                p.morse_temp_off() # Morsen temp. ausschalten
                self.timeout.set(p.nr,self.bc.get_intatt("CW Off Timeout"),p.morse_temp_on)
        print('bake.ctl-2')          
        self.save = True
        print('bake.ctl-3')

    def print_ports(self):
        for p in self.ports:
            #print(p.name)    
            pass

    def set_traeger(self):
        for p in self.ports:
            p.traeger_on()
                
    def reset_traeger(self):
        for p in self.ports:
            p.traeger_off()
    
    def test(self,x):
        self.m.play_start() 

    # statemachine methods    
    def traeger(self,x=''):
        #self.status="traeger"
        self.set_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.bc.get_intatt('On Time'), callback=self.pre)

    def pre(self,x):
        #self.status="pre"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.bc.get_intatt('Pre Time'), callback=self.play_text)
    
    def play_text(self,x):
        #self.status="call"
        self.m.txt = self.bc.c['Bakentext']
        self.m.play_start() 

    def post(self):
        #self.status="post"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.bc.get_intatt('Post Time'), callback=self.traeger)


class Config:

    def __init__(self):
        
        self.config_file = 'config.json'

        self.state = [{'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0},
                  {'on':False,'cw':False,'cwcounter':0}    
        ]

        self.c = {
                'saves': '0',
                'Version': '0.5',
                'CW Speed': '100',
                'Bakentext': 'OE5RNL',
                'On Time': '5',
                'Pre Time': '2',
                'Post Time':'2',
                'CW Off Timeout': '20',
                'ports':[    
                    {'id':'0','Name':'LED',   'Mode':'b','gpio':'25','On': '01','Off':'00','port_on':True, 'CW Off':'03','CW On':'04'},
                    {'id':'1','Name':'10 GHz','Mode':'b','gpio':'16','On': '11','Off':'10','port_on':False, 'CW Off':'13','CW On':'14'},
                    {'id':'2','Name':'24 GHz','Mode':'b','gpio':'17','On': '21','Off':'20','port_on':False, 'CW Off':'23','CW On':'24'},
                    {'id':'3','Name':'74 GHz','Mode':'b','gpio':'18','On': '31','Off':'30','port_on':False, 'CW Off':'33','CW On':'34'},
                    {'id':'4','Name':'Frei',  'Mode':'s','gpio':'19','On': '41','Off':'40','port_on':False, 'CW Off':'43','CW On':'44'},
                    {'id':'5','Name':'Frei',  'Mode':'s','gpio':'20','On': '51','Off':'50','port_on':False, 'CW Off':'53','CW On':'54'},
                    {'id':'6','Name':'Frei',  'Mode':'s','gpio':'21','On': '61','Off':'60','port_on':False, 'CW Off':'63','CW On':'64'},
                    {'id':'7','Name':'Frei',  'Mode':'s','gpio':'22','On': '71','Off':'70','port_on':False, 'CW Off':'73','CW On':'74'},
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
        self.c['ports'][a] = v

    def load(self):
        try:
            self.f = open(self.config_file,'r')
            self.txt = self.f.read()
            self.c = json.loads(self.txt)

        except OSError:  # open failed
            self.c = self.c
 
    # def save1(self):
    #     with open("state.txt", 'w') as fp:
    #         self.c['Version'] = 'TEST-TEST-TEST'
    #         json.dump(self.c, fp)

    def save(self):
        print('a')
        self.c['saves'] = str(int(self.c['saves'])+1)
        print('b')
        with open(self.config_file, 'w') as fp:
            print('c')
            json.dump(self.c, fp)
        print('d')
        machine.reset()

    def get_intatt(self,a):
        return int(self.c[a])*1000

def null():
    pass

def main():    
    config = Config()
    #bake = Bake(config,"PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS")
    bake = Bake(config)
    dtmf = Dtmf(callback=bake.ctl)
    pgm  = Pgm(config, callback=bake.stop_timer) 
    #pgm  = Pgm(config, callback=null) 

    # config = Config()
    # bake = Bake(config)
    # dtmf = Dtmf(null)
    # pgm  = Pgm(config, callback=null) 
    # #pgm  = Pgm(config, callback=null) 



    m=0
    while True:
        #print('m='+str(m))
        m += 1
        time.sleep_ms(50)
        pgm.uart_cmd()

        if bake.save:
            print('a')
            bake.stop_timer()
            config.save()
            print('a1')
            bake.start_timer()
            print('b')
            bake.save = False



if __name__ == "__main__":
    main()



