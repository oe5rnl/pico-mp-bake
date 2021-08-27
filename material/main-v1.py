# OE5VRL Bake

import utime
from machine import UART, Pin, Timer
#import machine
import time
#from statemachine import StateMachine, State
# https://docs.micropython.org/en/latest/wipy/tutorial/timer.html

class dtmf:

    def __init__(self):
        self.u=UART(0)
        tim = Timer()
        tim.init(freq=2.5, mode=Timer.PERIODIC, callback=self.tick)
        self.i=0
        self.command=""

       #comm = machine.UART(1,9600)
       #comm.init(9600, bits=8, parity=None, stop=1, timeout=2000) 
    
    def tick(self,x):
        #print(self.i)
        self.i=self.i+1
        if self.u.any():
          c=self.u.read(1).decode()
          print(c)          

          if c == "*":
               print("reset eingabe *")
               self.command=""
          elif c == "#":
               print("command fertig")
               print(self.command)
          elif c != "*" and c != "#":  
               self.command=self.command+c
               

class morse:

    def __init__(self):
        #tim = Timer()
        #tim.init(period=500, mode=Timer.PERIODIC, callback=self.tick)
        self.txt=""
        self.paying=False
        self.i=0
        self.ports=[]


        self.MorseCodes = {
        '$' : ".........",
        '%' : ".........",     
        '&' : ".........",     
        '\'' : ".----.",         
        '(' : "-.--.",          
        ')' : "-.--.-",        
        '*' : ".........",     
        '+' : ".........",    
        ':' : "--..--",        
        '-' : "-...._",        
        '.' : ".-.-.-",        
        '/' : "-..-.",         
        '0' : "-----",         
        '1' : ".----",         
        '2' : "..---",         
        '3' : "...--",         
        '4' : "....-",         
        '5' : ".....",         
        '6' : "-....",         
        '7' : "--...",         
        '8' : "---..",         
        '9' : "----.",        
        ':' : "---...",        
        ' :' : ".........",     
        '<' : ".........",     
        '=' : ".........",     
        '>' : ".........",     
        '?' : "..--..",        
        '@' : ".........",     
        'A' : ".-",            
        'B' : "-...",          
        'C' : "-.-.",          
        'D' : "-..",           
        'E' : ".",             
        'F' : "..-.",          
        'G' : "--.",           
        'H' : "....",          
        'I' : "..",            
        'J' : ".---",          
        'K' : "-.-",           
        'L' : ".-..",          
        'M' : "--",            
        'N' : "-.",            
        'O' : "---",           
        'P' : ".--.",          
        'Q' : "--.-",          
        'R' : ".-.",           
        'S' : "...",           
        'T' : "-",             
        'U' : "..-",           
        'V' : "...-",          
        'W' : ".--",           
        'X' : "-..-",          
        'Y' : "-.--",          
        'Z' : "--.."          
        }

    def add_port(self,port):
        self.ports.append(port)
        
    def print_ports(self):
        for p in self.ports:
            print(p.name)    

    def tick(self,x):  # 0.1 sec
        #print("morse:"+str(self.i))
        self.i=self.i+1
        print(self.i)
        
        #if self.playing:
        #    pass

    def set_txt(self,txt):
        self.txt=txt
    
    def _play_char(self,c):

        self.print_ports() 
        ps = self.MorseCodes[c]
        for e in ps:
            print(e)
            for p in self.ports:
                if e == '.':
                    print('p')
                    p.on()
                    time.sleep_ms(50)
                    p.off()
                if e == '-':
                    print('s')
                    p.on()
                    time.sleep_ms(150)
                    p.off()
            time.sleep_ms(200)

    def _play_txt(self):    
        self.paying=True
        print(self.txt)
        for e in self.txt:
            self._play_char(e)
            time.sleep_ms(300)

    def stop(self):
        self.paying=False



class port:
  def __init__(self, pin):
    self.name="port_"+str(pin)
    self.pin=pin
    self.p = Pin(self.pin, Pin.OUT)    # create output pin on GPIO0

  def on(self):
     self.p.on()

  def off(self):     
     self.p.off()          

class Bake:
    def __init__(self):
        # Träger ein  | Pre Zeit | Kennung | Post Zeit   | Träger ein
        
        # ÄNDERN !
        self.p = Pin(25, Pin.OUT)    # 
      
        self.bake_tim = Timer()    
        self.traeger()
     
    
    def traeger(self):
        print("start traeger")
        self.p.on()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=5000, callback=self.pre)


    def pre(self,x):
        print("traeger_ende -> start pre")
        self.p.off()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.play_text)
    
    def play_text(self,x):
        print("call ausgabe")
        for i in range(1,20):
            print("*")
            self.p.toggle()
            time.sleep_ms(100)
        self.p.off()
        print("play_text -> start post")
        self.p.off()
        self.bake_tim.init(mode=Timer.ONE_SHOT, period=2000, callback=self.post)
        
    def post(self,x):
        print("post")
        print("post -> traeger")
        self.traeger()
        
#      
#     def start(self):
#         #         self.key=self.tein



def main():    
    # # ------------ MAIN --------------
    print("bake")
    p1=port(25)
    # p2=port(6)
    # p3=port(7)
    # #p4=port(8)
    # #p5=port(9)
    # #p6=port(10)
    # #p7=port(11)

    m=morse()
    m.add_port(p1)
    #m.set_txt(">>> OE5VRL")
    m.set_txt("OE5RNL")
    #m.play_char('A')
    #time.sleep(2)
    #m._play_txt()


    # m.add_port(p2)
    # m.add_port(p3)
    # m.print_ports()

    # c=dtmf()

    bake = Bake()
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

    m=0
    while True:
        print("Bake main:"+str(m))
        time.sleep_ms(500)
        m=m+1

        



if __name__ == "__main__":
    main()
















