"""Configuration for the TUI's appearance."""
import curses

class ColorScheme:
    """Holds the color pairs for the TUI."""
    def __init__(self):
        try:
            curses.start_color()
            curses.use_default_colors()
        except curses.error as e:
            raise RuntimeError("ColorScheme must be initialized after curses.initscr()") from e

        # Define custom colors (if terminal supports it)
        if curses.can_change_color():
            curses.init_color(100, 200, 200, 200) # Light grey
            curses.init_color(101, 0, 200, 700)   # Custom blue
            curses.init_color(102, 0, 700, 200)   # Custom green

        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)      # Success
        curses.init_pair(2, curses.COLOR_RED, -1)        # Error
        curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Warning
        curses.init_pair(4, curses.COLOR_CYAN, -1)       # Info
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # Highlight
        
        if curses.can_change_color():
            curses.init_pair(6, curses.COLOR_WHITE, 101)   # Header with custom blue
            curses.init_pair(7, curses.COLOR_BLACK, 102)  # Success bg with custom green
            curses.init_pair(9, 100, -1)                      # Light grey text
        else:
            curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header fallback
            curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Success bg fallback
            curses.init_pair(9, curses.COLOR_WHITE, -1)                   # Light grey fallback
        
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Info bg
        self.SUCCESS = curses.color_pair(1)
        self.ERROR = curses.color_pair(2)
        self.WARNING = curses.color_pair(3)
        self.INFO = curses.color_pair(4)
        self.HIGHLIGHT = curses.color_pair(5)
        self.HEADER = curses.color_pair(6)
        self.SUCCESS_BG = curses.color_pair(7)
        self.INFO_BG = curses.color_pair(8)
        self.GREY_TEXT = curses.color_pair(9)
