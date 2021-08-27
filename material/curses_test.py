from curses import wrapper
import curses
from curses.textpad import Textbox, rectangle

# https://www.devdungeon.com/content/curses-programming-python

   
class Port:

    def __init__(self,y):

        screen = curses.initscr()
        
        port_window = curses.newwin(15, 20, 0, 0)
        port_window.addstr(y, 10, "Port1") 

        port_window.refresh()
        port_window.refresh()
        curses.napms(2000)

def main(stdscr):
    p1 = Port(5)

    # screen = curses.initscr()

    # # Update the buffer, adding text at different locations
    # screen.addstr(0, 10, "Beaken-Controller Config Tool")
    # screen.addstr(3, 10, "Port1")  
    # screen.addstr(4, 10, "Port2")
    
    # # Changes go in to the screen buffer and only get
    # # displayed after calling `refresh()` to update
    # screen.refresh()


    # screen.addstr(20,5,"Press any key...")
    # screen.refresh()

    # while True:
    #     c = screen.getch()
    #     if chr(c) == "q":
    #         #curses.endwin()
    #         break
    #     screen.addstr(6, 6, chr(c))

    # # Convert the key to ASCII and print ordinal value
    # print("You pressed %s which is keycode %d." % (chr(c), c))

wrapper(main)



    # # Clear screen
    # screen = initscr()
    # #stdscr.clear()

    # screen.addstr(0, 0, "This string gets printed at position (0, 0)")
    # screen.addstr(3, 1, "Try Russian text: Привет")  # Python 3 required for unicode
    # screen.addstr(4, 4, "X")
    # screen.addch(5, 5, "Y")

    # # # This raises ZeroDivisionError when i == 10.
    # # for i in range(11, 30):
    # #     v = i-10
    # #     stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))

    # # stdscr.refresh()
    # # stdscr.getkey()



    # stdscr.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send)")

    # editwin = curses.newwin(5,30, 2,1)
    # rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
    # stdscr.refresh()

    # box = Textbox(editwin)

    # # Let the user edit until Ctrl-G is struck.
    # box.edit()

    # # Get resulting contents
    # message = box.gather()
