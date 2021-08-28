import curses

screen = curses.initscr()

screen.move(1,1) 

screen.refresh()
curses.napms(2000)
