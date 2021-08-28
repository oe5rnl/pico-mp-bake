import curses
from operator import attrgetter

class Ui:
    def __init__(self):
        self.screen = curses.initscr()
        self.el = []
        self.active_obj = 0


    def add(self,e):
        self.el.append(e)
        self.el.sort(key = attrgetter('tab_nr')) # , reverse = True)
        e.add_screen(self.screen)
        e.show()

    def print_el(self):
        for e in self.el:
            print(e.label + " tab="+str(e.tab_nr))

    def next_obj(self):
        gefunden = False
        for e in self.el:
            if e.tab_nr > 0:
                #print("akt="+str(self.active_obj.tab_nr) + " e="+str(e.tab_nr))
                if e.tab_nr > self.active_obj.tab_nr:
                    self.active(e)
                    gefunden = True
                    #print("gefunden")
                    break
        if not gefunden:
            for e in self.el:
                if e.tab_nr>0:
                    self.active(e)
                    break
            #print(self.e[])

    def active(self, e):
        #self.screen.move(e.y,e.x+e.p)
        self.active_obj = e
 

    def loop(self):
        while True:
            cr = self.screen.getch()
            c = chr(cr)
            self.screen.addstr(30, 2, "Input: |" + str(c) + "| " + str(cr)+ " ")
            self.active_obj.add_char(c)

            if ord(c) == 9:
                self.next_obj()

            if c == "q": 
                break



        

class Field():
    def __init__(self, x, y, label):
        self.win = 0
        self.x=x
        self.y=y        
        self.label = label
        self.tab_nr = 0
      
    def add_screen(self, screen):
        self.win = screen

    def show(self):
        self.win.addstr(self.y, self.x, self.label)

    def add_char(self,c):
        pass

class Input(Field):
    def __init__(self, x, y, p, max_txt_len, tab_nr, label, default):
        # win curses window
        # x pos
        # y pos
        # p input pos
        # max_txt_len max len of input text
        # lable text to display 
        # a dummy

        super().__init__( x, y, label)
        
        self.label = label
        self.text = ""
        self.max_txt_len = max_txt_len
        self.p = p
        self.ins_pos = 0
        self.tab_nr = tab_nr
        self.default = default
        #self.win.addstr(self.y,self.x+self.p+self.ins_pos,self.label)
   
    def show(self):
        self.win.addstr(self.y, self.x, self.label)
        self.win.addstr(self.y, self.x+self.p, self.default)
        


    def add_char(self,c):
        self.ins_pos = self.ins_pos + 1
        if  self.ins_pos <= self.max_txt_len:
            self.win.move(self.y,self.x+self.p+self.ins_pos)
            self.win.addstr(self.y,self.x+self.p+self.ins_pos,c)
            self.text = self.text + c


    def read_value(self):
         self.win.move(self.y,self.x+self.p)
         while True:
            cr = self.win.getch()
            c = chr(cr)
            self.win.addstr(30, 2, "Input: |" + str(c) + "| " + str(cr)+ " ")
            if c == "s": 
                break

    def add_tab_nr(self, nr):
        self.tab_nr = nr




def main():
    print('Fieldtest')
    #screen = curses.initscr()

    c = {
        "version":"0.3",
        "cw_speed": "100",
        "msg": "OE5VRL",
        "on_time": 50,
        "pre_time": 5,
        "post_time": 5,

        "ports":[    
                {"id":1,"mode":"b","pin":"25","on_cmd": "11","off_cmd":"10", "temp_on_cmd":"13","temp_off_cmd":"14"},
                {"id":2,"mode":"b","pin":"21","on_cmd": "21","off_cmd":"20", "temp_on_cmd":"23","temp_off_cmd":"24"},
                {"id":3,"mode":"b","pin":"22","on_cmd": "31","off_cmd":"30", "temp_on_cmd":"33","temp_off_cmd":"34"},
                {"id":4,"mode":"b","pin":"24","on_cmd": "41","off_cmd":"40", "temp_on_cmd":"43","temp_off_cmd":"44"},
                {"id":5,"mode":"s","pin":"25","on_cmd": "51","off_cmd":"50", "temp_on_cmd":"53","temp_off_cmd":"54"},
                {"id":6,"mode":"s","pin":"26","on_cmd": "61","off_cmd":"60", "temp_on_cmd":"63","temp_off_cmd":"64"},
                {"id":7,"mode":"s","pin":"27","on_cmd": "71","off_cmd":"70", "temp_on_cmd":"73","temp_off_cmd":"74"},
        ]
    }

    # #for e in c['ports']:
    # #    print(e['id'])
    # ##c['ports'].sort(key = attrgetter('id')) # , reverse = True)

    ui = Ui()

    # y = 6
    # for e in c['ports']:
    #     ui.add(Field(5, y+1, "Port"+str(e['id'])))
    #     ui.add(Input(12,y+1,  8, 10, 1, e['on-cmd']))
    #     y=y+1

    #print(c['ports'][0]['mode'])

    f1 = Field(2, 6,  "Port1: "+c['ports'][0]['mode'])
    f2 = Field(2, 7,  "Port2: "+c['ports'][1]['mode'])
    f3 = Field(2, 8,  "Port3: "+c['ports'][2]['mode'])
    f4 = Field(2, 9,  "Port4: "+c['ports'][3]['mode'])
    f5 = Field(2, 10, "Port5: "+c['ports'][4]['mode'])
    f6 = Field(2, 11, "Port6: "+c['ports'][5]['mode'])
    f7 = Field(2, 12, "Port7: "+c['ports'][6]['mode'])
    
    p1_on = Input(12, 6,  8, 10, 11, "on_cmd", c['ports'][0]['on_cmd'])
    p2_on = Input(12, 7,  8, 10, 21, "on_cmd", c['ports'][1]['on_cmd'])
    p3_on = Input(12, 8,  8, 10, 31, "on_cmd", c['ports'][2]['on_cmd'])
    p4_on = Input(12, 9,  8, 10, 41, "on_cmd", c['ports'][3]['on_cmd'])
    p5_on = Input(12, 10, 8, 10, 51, "on_cmd", c['ports'][4]['on_cmd'])
    p6_on = Input(12, 11, 8, 10, 61, "on_cmd", c['ports'][5]['on_cmd'])
    p7_on = Input(12, 12, 8, 10, 71, "on_cmd", c['ports'][6]['on_cmd'])

    p1_off = Input(35, 6,  8, 10, 12, "on_off", c['ports'][0]['off_cmd'])
    p2_off = Input(35, 7,  8, 10, 22, "on_off", c['ports'][1]['off_cmd'])
    p3_off = Input(35, 8,  8, 10, 32, "on_off", c['ports'][2]['off_cmd'])
    p4_off = Input(35, 9,  8, 10, 42, "on_off", c['ports'][3]['off_cmd'])
    p5_off = Input(35, 10, 8, 10, 52, "on_off", c['ports'][4]['off_cmd'])
    p6_off = Input(35, 11, 8, 10, 62, "on_off", c['ports'][5]['off_cmd'])
    p7_off = Input(35, 12, 8, 10, 72, "on_off", c['ports'][6]['off_cmd'])

    y = 6
    i=1
    for e in c['ports']:
        if e['mode'] == 'b':
            p1_temp_on = Input(50,     y, 15, 10, i*10+3, "temp_on_cmd", c['ports'][i-1]['temp_on_cmd'])
            p2_temp_on = Input(50+20,  y, 15, 10, i*10+4, "temp_off_cmd", c['ports'][i-1]['temp_off_cmd'])
            ui.add(p1_temp_on)
            ui.add(p2_temp_on)
        i=i+1
        y=y+1




    ui.add(f1)
    ui.add(f2)
    ui.add(f3)
    ui.add(f4)
    ui.add(f5)
    ui.add(f6)
    ui.add(f7)

    ui.add(p1_on)
    ui.add(p2_on)
    ui.add(p3_on)
    ui.add(p4_on)
    ui.add(p5_on)
    ui.add(p6_on)
    ui.add(p7_on)

    
    ui.add(p1_off)
    ui.add(p2_off)
    ui.add(p3_off)
    ui.add(p4_off)
    ui.add(p5_off)
    ui.add(p6_off)
    ui.add(p7_off)
    
    ui.print_el()
    
    #f1.show()
    #i1.show()
    #i2.show()

    ui.active(p1_on)
    ui.loop()


if __name__ == '__main__':
        main()
