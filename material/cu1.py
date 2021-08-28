import curses

class Ui:
    def __init__(self):
        self.el = []
        self.akt_tab = 0

    def add(self,e):
        self.el.append(e)

    # def loop(self):
    #     while True:
    #         cr = self.win.getch()
    #         c = chr(cr)
    #         self.win.addstr(30, 2, "Input: |" + str(c) + "| " + str(cr)+ " ")
    #         if c == "s": 
    #             break

class Field:
    def __init__(self, win, x, y, label):
        self.win = win
        self.x=x
        self.y=y        
        self.label = label

        
    def show(self):
        print(self.label)
        self.win.addstr(self.y, self.x, self.label)


class Input(Field):
    def __init__(self, win, x, y, p, label, a):
        # win curses window
        # x pos
        # y pos
        # p input pos
        # lwbale text to display 
        # a dummy

        super().__init__(win, x, y, label)
        
        self.label = label
        self.a = a
        self.p = p
        self.tab_nr = 0

  
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
    screen = curses.initscr()

    #ui = Ui()
    f1 = Field(screen, 5, 5, "Port1")
    i1 = Input(screen, 5, 6, 10, "Port1", "a")
    i2 = Input(screen, 5, 7, 10, "Port2", "a")

    # ui.add(f1)
    # ui.add(i1)
    # ui.add(i2)

    i1.add_tab_nr(1)
    i1.add_tab_nr(2)
    
    
    f1.show()
    i1.show()
    i2.show()

    i1.read_value()

    #ui.loop()


if __name__ == '__main__':
        main()
