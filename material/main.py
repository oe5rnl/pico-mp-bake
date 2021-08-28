
#
# Bakencontroller
# by OE5RNL, OE5VRL
# 2021-08-26
#

import utime
from machine import UART, Pin, Timer
import time
import os
import json
from machine import WDT


# https://onlinetonegenerator.com/dtmf.html
# from statemachine import StateMachine, State
# https://docs.micropython.org/en/latest/wipy/tutorial/timer.html
# https://docs.micropython.org/en/latest/library/machine.html
# https://morsecode.world/international/timing.html
# https://kofler.info/wp-content/uploads/pico-gpios.png
# https://www.accessengineeringlibrary.com/content/book/9781260117585/back-matter/appendix1

code_version = '0.7a 2021-08-24'

class Line:

    def __init__(self,com,wd):
        self.txt=''
        self.com = com
        self.len = 0
        self.wd = wd

    def read_char(self):
        while True:
            self.wd.feed()
            if self.com.any():
                c=self.com.read(1)
                if c != None:
                    return c        

    def g(self,c,a,w):
        # isnumeric würde auch für 1/2 etc gelten
        num    = ['0','1','2','3','4','5','6','7','8','9']
        alphaU = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q',
                 'R','S','T','U','V','W','X','Y','Z',' ']
        alphaL = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
                 'r','s','t','u','v','w','x','y','z']
        
        ret = False
        ch = chr(ord(c))
        if a == 'a':
            if ch in alphaL or ch in num:
                ret = True
        if a.upper() == 'A':
            if ch in alphaU or ch in num:
                ret = True
        if a == 'Aa':
            if ch in alphaL or ch in alphaU or ch in num:
                ret = True

        elif a == 'n':
            if ch  in num:
                ret = True
        elif a == 'w':
            #print(a)
            #print(w)
            if ch in w:
                ret = True
                print(ret)
        else:
            ret = False
        return ret

    def read(self,e, default):
        txt = default
        l = len(txt)       
        maxlen = e[1]
        alnum = e[2]
        wb = e[3]
        
        self.com.write(txt)

        while True:
            self.wd.feed()
            c = self.read_char()       
            if ord(c) == 0x7f:  # bs           
                if l > 0:
                    l -= 1
                    txt = txt[:-1]
                    self.com.write(c) #bs
            else: 
                if (l <= maxlen-1):
                    if self.g(c,alnum,wb):
                        l += 1
                        txt = txt + c.upper()
                        self.com.write(c)
                    else:
                        #print('xx')
                        #print(c)
                        #print('---')
                        pass
            if c == b'\r':
                if l>0:
                    # trim beide Seiten, keine doppelten leerzeichen
                    return " ".join(txt.decode().strip().split())

            #print("txt: |"+txt.decode()+'| len='+str(l))       
        return txt


class Console:
    
    def __init__(self, config, callback1, callback2):
        
        self.i=0
        self.stop_timer = callback1
        self.start_timer = callback2
        self.command = ""
        self.cmode = False
        self.config = config
        self.save = False

        self.sw = Switch_port()

        self.c = b''
        self.prompt = b'\r\n0-7(edit Port), a(edit Allgemein), r(eset) c(print config) s(ave) >'
        self.ueberschrift = "{0:^10}{1:^10}{2:<10}{3:^10}{4:^10}{5:^10}{6:^10}{6:^10}"
        self.werte       = "{0:^10}{1:^10}{2:<10}{3:^10}{4:^10}{5:^10}{6:^10}{6:^10}"

        self.u = UART(id=0, baudrate=9600, bits=8, parity=None, stop=1, timeout=0, rxbuf=1024, txbuf=2048)
        self.flush()
        self.u.write(b'\n\r\n\r\n\r\n\rBeacon-Controller by OE5RNL & OE5NVL für OE5VRL\n\r')
        self.u.write(b'\n\rpress Enter for config >')
        self.line = Line(self.u,self.config.wd)   #.encode('utf-8')

    def flush(self): 
        while self.u.any():
            self.config.wd.feed()
            self.u.read()
      
    def read_char(self):
        while True:
            self.config.wd.feed()
            if self.u.any():
                c=self.u.read(1)
                if c != None:
                    return c

    def cmd(self):  
       
        if self.u.any():
            c=self.u.read(1) 
            if c != None:    
                if c == b'\r':
                    self.print_config()
                    self.u.write(b' ')
                elif  c == b'c':
                    self.print_config()               
                elif chr(ord(c)) in '01234567':
                    self.edit_port(c)
                elif c == b'a':
                    self.edit_allgemein()
                elif c == b'r':
                    machine.reset( )
                elif c == b's':
                    self.stop_timer()
                    self.config.save()
            
                self.u.write(self.prompt)
        
    def crlf(self):
        self.u.write(b'\r\n')

    def edit_port(self,c):
        #self.u.write(b'\r\nPort number: ')
        #c=self.read_char()
        i = int.from_bytes(c,'big')-48
        #self.u.write(c)
        self.crlf()
        self.crlf()
        f = "Edit Port {0} {1:<15} ({2:<7}) Neu: "
  
        if c in [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7']:
            key = [['Name',15,'Aa',''],['Port On',1,'n',''],['Mode',1,'w','BSbs'],['On',10,'n',''],['Off',10,'n',''],['CW Off',10,'n',''],['CW On',10,'n','']]
            for e in key:                     
                if self.config.get_port_attr(i,'Mode') == 'S' and (e[0] == 'CW Off' or e[0] == 'CW On'):
                    pass                          
                else:
                    if e[0] == 'Port On':
                         self.sw.set_last(self.config.get_port_attr(i,'Port On'))

                    self.u.write(f.format(i, e[0], self.config.get_port_attr(i,e[0]).encode('utf-8'),''))
                    line = self.line.read(e, default=self.config.get_port_attr(i,e[0]).encode('utf-8'))
                    self.config.set_port_attr(i,e[0],line)
                    # write attribute into port object
                    #self.saveatt_obj(i,e[0],)
                    self.crlf()
                    
                    if e[0] == 'Port On':
                        v = self.config.get_port_attr(i,'Port On')
                        if self.sw.get_last() != v :
                            self.sw.set_sw(i,v)

                
                

            self.stop_timer()  
            self.config.save()
            self.start_timer()

    def edit_allgemein(self):
        self.crlf()
        key = [['CW Speed',3,'n',''],['Bakentext',50,'Aa',''],['On Time',3,'n',''],['Pre Time',2,'n',''],['Post Time',2,'n',''],['CW Off Timeout',4,'n','']]
        f = "Edit {0:<17} Aktuell: {1:<7} Neu: "
        for e in key:       
            self.u.write(f.format(e[0],self.config.get_attr(e[0]).encode('utf-8')))
            line = self.line.read(e, default=self.config.get_attr(e[0]).encode('utf-8'))
            self.config.set_attr(e[0],line)
            self.crlf()
        #self.save = True
        self.stop_timer() 
        self.config.save()
        self.start_timer()
    
    def print_config(self):

        f = "{0:<12} : {1:<7} {2:<10}  {3:<10}"

        self.u.write(b'\n\r\n\rBeacon-Controller by OE5RNL & OE5NVL für OE5VRL\n\r\n\r')
        self.u.write(b'Code-Version   : '+code_version+'\r\n')
        self.u.write(b'Config-Version : '+self.config.get_attr('Version')+'\r\n')        
        self.u.write(b'Saves          : '+self.config.get_attr('saves')+'\r\n')
        self.u.write(b'Core Temerature: '+self.get_core_temperature()+'\n\r')
        self.u.write('\r\n') 
        self.u.write(b'CW Speed       : '+self.config.get_attr('CW Speed')+'\r\n') 
        self.u.write(b'Bakentext      : '+self.config.get_attr('Bakentext')+'\r\n')
        self.u.write(b'On Time        : '+self.config.get_attr('On Time')+'\r\n')    
        self.u.write(b'Pre Time       : '+self.config.get_attr('Pre Time')+'\r\n')
        self.u.write(b'Post Time      : '+self.config.get_attr('Post Time')+'\r\n')
        self.u.write(b'CW Timeout     : '+self.config.get_attr('CW Off Timeout')+'\r\n')
        self.u.write(b'\r\n')

        self.u.write(self.ueberschrift.format('Port','Status','Name','Mode','On','Off','CW aus','CW ein')+'\r\n')    
        for i in range(8):
            self.show_port_data(i)
                                                        
    def show_port_data(self,i):
        if self.config.get_port_attr(i,'Mode') in 'B':
            self.u.write(self.werte.format( self.config.get_port_attr(i,'id'),
                                            self.t(self.config.get_port_attr(i,'Port On')),
                                            self.config.get_port_attr(i,'Name'),
                                            self.config.get_port_attr(i,'Mode'),
                                            self.config.get_port_attr(i,'On'),
                                            self.config.get_port_attr(i,'Off'),
                                            self.config.get_port_attr(i,'CW Off'),
                                            self.config.get_port_attr(i,'CW On')
                                          )+'\r\n'
                        )

        if self.config.get_port_attr(i,'Mode') in 'Ss':
            self.u.write(self.werte.format( self.config.get_port_attr(i,'id'), 
                                            self.t(self.config.get_port_attr(i,'Port On')),
                                            self.config.get_port_attr(i,'Name'),
                                            self.config.get_port_attr(i,'Mode'),
                                            self.config.get_port_attr(i,'On'),
                                            self.config.get_port_attr(i,'Off'),
                                            b'',b''
                                          )+'\r\n'
                        )
     
    def t(self,b):
        if b=='1':
            return('Ein')
        else:
            return('Aus')

    def get_core_temperature(self):
        sensor_temp = machine.ADC(4)
        conversion_factor = 3.3 / (65535)
        #reading = sensor_temp.read_u16() * conversion_factor 
        temp = 27 - (sensor_temp.read_u16() * conversion_factor - 0.706)/0.001721
        return "{0:.2f}".format(temp)


class Switch_port:
    def __init__(self):
        self.doit = False # todo ?
        self.i = -1 # port numer
        self.v = 0 # value
        self.last = '0' # 

    def set_last(self,w):
        self.last = w
        #print('set_last:'+str(w))

    def get_last(self):
        #print('get_last:'+str(self.last))
        return self.last

    def set_sw(self,i,v):
        self.i = i
        self.sw = v
        self.doit = True
        #print('set_sw: '+'i='+str(self.i)+'sw='+str(self.sw) +'doit='+str(self.doit))

    def get_sw(self):
        #print('get_sw:'+str(self.doit)+str(self.v))
        return self.doit, self.i, self.v
   
    def res_sw(self):
        self.doit=False
        #print('res_sw')
        

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

        self.st.irq(trigger=Pin.IRQ_RISING, handler=self.dtmf)
  
    def dtmf(self,pin):
        print("IRQ")
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
 

class Pause:
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
        for i in range(0,len(self.timers)): # range problem ????
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
        bpm = 300
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

        print('state='+str(self.state))

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





class Bake:
    def __init__(self, config, txt=''):
        #print('bake-init')
        self.status="none"
        self.config = config
        self.save = False

        self.ports=[]      
        for i in range(8):
            self.ports.append(Port( id=             int(config.get_port_attr(i,'id')),
                                    gpio=           config.get_port_attr(i,'gpio'), 
                                    mode=           config.get_port_attr(i,'Mode'), 
                                    on_cmd=         config.get_port_attr(i,'On'), 
                                    off_cmd=        config.get_port_attr(i,'Off'),
                                    port_on=        config.get_port_attr(i,'Port On'),
                                    morse_off_cmd=  config.get_port_attr(i,'CW Off'), 
                                    morse_on_cmd=   config.get_port_attr(i,'CW On')
                                   )
                             )        
        self.print_ports()
 
        # set saved state of the port
        for p in self.ports:
            if config.get_port_attr(p.id,'Port On') == '1':
                p.dtmf_on() 
            else:
                p.dtmf_off() 
            #print(config.get_port_attr(p.id,'Port On'))
            #print(p.port_on)

        self.timeout = Timeout(self.ports)
        self.m = Morse(self.ports,self.playende)

        # Träger ein  | Pre Zeit | Kennung | Post Zeit   | Träger ein
        self.bake_tim = Timer()   
        self.start_timer()
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

            p.on_cmd  = self.config.get_port_attr(p.id,'On') 
            p.off_cmd  = self.config.get_port_attr(p.id,'Off')
            p.morse_on_cmd  = self.config.get_port_attr(p.id,'CW On')
            p.morse_off_cmd   = self.config.get_port_attr(p.id,'CW Off')

            print(p.on_cmd)     
            print(p.off_cmd)  
            print(p.morse_on_cmd)  
            print(p.morse_off_cmd)    

            # Port ein/aus
            if p.on_cmd == cmd:
                print('*1')

                p.dtmf_on() 
                self.config.set_port_attr(p.id,'Port On','1') 
                self.save = True

            elif p.off_cmd == cmd:           
                print('*1')
                p.dtmf_off()     
                self.config.set_port_attr(p.id,'Port On','0') 
                self.save = True

            # Morsen unterdrücken/freigeben
            elif p.morse_on_cmd == cmd:
                print('on')
                p.morse_temp_on() # Morsen einschalten 
                #self.timeout.set(1, 20, p.morse_temp_on)
          
            elif p.morse_off_cmd == cmd:
                p.morse_temp_off() # Morsen temp. ausschalten
            

    def print_ports(self):
        for p in self.ports:
            #print(p.id)    
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
        self.status="traeger"
        self.set_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.config.get_intatt('On Time'), callback=self.pre)

    def pre(self,x):
        self.status="pre"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.config.get_intatt('Pre Time'), callback=self.play_text)
    
    def play_text(self,x):
        self.status="call"
        self.m.set_txt(self.config.get_attr('Bakentext'))
        self.m.sync()
        while  self.m.play_msg():
            pass
        #self.m.play_msg()

    def post(self):
        self.status="post"
        self.reset_traeger()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=self.config.get_intatt('Post Time'), callback=self.traeger)


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


def main():    
    print('bake')

    config = Config()
    config.wd.start(False)

    #bake = Bake(config,"PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS PARIS")
    bake = Bake(config)
    dtmf = Dtmf(callback=bake.ctl)
    console  = Console(config, callback1=bake.stop_timer, callback2=bake.start_timer) 

    m=0
    while True:
        config.wd.feed()
        #print('m='+str(m))
        m += 1
        #time.sleep_ms(10)
        console.cmd()
        #print(bake.status)

        if bake.save:
            print('save')
            bake.stop_timer()  
            config.save()
            #print('ma1')
            bake.start_timer()
            #print('mb')
            bake.save = False

if __name__ == "__main__":
    main()



