from curses import wrapper
import curses
from curses.textpad import Textbox, rectangle

# https://www.devdungeon.com/content/curses-programming-python


class Port:

    def __init__(self, screen ,y, config):
        self.config = config
        #screen.addstr(y, 5, str(self.config['mode'])) 
        screen.refresh()

    def show(self):
        pass


    def read_port_values(self,nr):
        print(nr)
        # lines, columns, start line, start column
        pw = curses.newwin(8, 30, 15, 5)
        pw.border('|', '|', '-', '-', '+', '+', '+', '+')
        curses.curs_set(1)
        #pw.setxy(2,2)
        # Long strings will wrap to the next line automatically
        # to stay within the window
        pw.addstr(1, 2, "Port Parameter")
        pw.addstr(2, 2, "Port" + str(nr) + " Mode        : " + self.config['mode'] )
        pw.addstr(3, 2, "Port" + str(nr) + " ON_CMD      : " + self.config['on-cmd']  )
        pw.addstr(4, 2, "Port" + str(nr) + " OFF_CMD     : " + self.config['off-cmd']  )
        pw.addstr(5, 2, "Port" + str(nr) + " TEMP_ON_CMD : " + self.config['temp-on-cmd']  )
        pw.addstr(6, 2, "Port" + str(nr) + " TEMP_OFF_CMD: " + self.config['temp-off-cmd']  )
        
        pw.refresh()

        while True:
            c = chr(pw.getch())
            #pw.addstr(30, 2, "Input: " + str(c))
            if c == "s":
                break

        curses.curs_set(0)
        



def main(stdscr):

    config = {
        "version":"0.3",
        "cw_speed": "100",

        "ports":[    
                {"id":1,"mode":"b","pin":"25","on-cmd": "11","off-cmd":"10", "temp-on-cmd":"13","temp-off-cmd":"14"},
                {"id":2,"mode":"s","pin":"21","on-cmd": "21","off-cmd":"20", "temp-on-cmd":"23","temp-off-cmd":"24"},
                {"id":3,"mode":"s","pin":"22","on-cmd": "31","off-cmd":"30", "temp-on-cmd":"33","temp-off-cmd":"34"},
                {"id":4,"mode":"s","pin":"24","on-cmd": "41","off-cmd":"40", "temp-on-cmd":"43","temp-off-cmd":"44"},
                {"id":5,"mode":"s","pin":"25","on-cmd": "51","off-cmd":"50", "temp-on-cmd":"53","temp-off-cmd":"54"},
                {"id":6,"mode":"s","pin":"26","on-cmd": "61","off-cmd":"60", "temp-on-cmd":"63","temp-off-cmd":"64"},
                {"id":7,"mode":"s","pin":"27","on-cmd": "71","off-cmd":"70", "temp-on-cmd":"73","temp-off-cmd":"74"},
        ]
    }

    screen = curses.initscr()
    curses.curs_set(0)

    p1 = Port(screen, 5, config['ports'][0])
    p2 = Port(screen, 6, config['ports'][1])
    p3 = Port(screen, 7, config['ports'][2])
    p4 = Port(screen, 8, config['ports'][3])
    p5 = Port(screen, 9, config['ports'][4])
    p6 = Port(screen, 10,config['ports'][5])
    p7 = Port(screen, 11,config['ports'][6])

    while True:
        c = chr(screen.getch())
        screen.addstr(25, 2, "Input: " + str(c))
        if c == "p":
            curses.beep()

        if c == "q":
            break
        elif c in ['1','2','3','4','5','6','7']:
                eval("p"+c+".read_port_values(c)")


wrapper(main)

