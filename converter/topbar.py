'''Topbar for the TUI'''

import curses
from datetime import datetime

class Topbar:
    def __init__(self, stdscr, width):
        self.stdscr = stdscr
        self.width = width
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.COLOR_HEADER = curses.color_pair(6)

    def draw(self):
        '''Draw the top bar with time and title'''
        self.stdscr.attron(self.COLOR_HEADER | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * self.width)
        
        # Title
        title = "Shop Converter"
        title_x = (self.width - len(title)) // 2
        self.stdscr.addstr(0, title_x, title)
        
        # Time
        time_str = datetime.now().strftime("%H:%M:%S")
        required_width = len(time_str) + 2
        if self.width >= required_width:
            x = self.width - len(time_str) - 2
            self.stdscr.addstr(0, x, time_str)
        
        self.stdscr.attroff(self.COLOR_HEADER | curses.A_BOLD)
