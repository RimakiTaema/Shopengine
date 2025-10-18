"""Terminal User Interface for shop converter using curses"""

import curses
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class ShopConverterTUI:
    """Advanced Terminal User Interface with full-screen dashboard"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Initialize curses settings
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        stdscr.nodelay(False)
        stdscr.keypad(True)
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)      # Success
        curses.init_pair(2, curses.COLOR_RED, -1)        # Error
        curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Warning
        curses.init_pair(4, curses.COLOR_CYAN, -1)       # Info
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # Highlight
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Success bg
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Info bg
        
        self.COLOR_SUCCESS = curses.color_pair(1)
        self.COLOR_ERROR = curses.color_pair(2)
        self.COLOR_WARNING = curses.color_pair(3)
        self.COLOR_INFO = curses.color_pair(4)
        self.COLOR_HIGHLIGHT = curses.color_pair(5)
        self.COLOR_HEADER = curses.color_pair(6)
        self.COLOR_SUCCESS_BG = curses.color_pair(7)
        self.COLOR_INFO_BG = curses.color_pair(8)
        
        # State management
        self.log_messages = []
        self.current_operation = "Initializing..."
        self.stats = {'success': 0, 'skipped': 0, 'errors': 0, 'total': 0}
        self.progress = {'current': 0, 'total': 0, 'message': ''}
        self.start_time = time.time()
        
        # Create scrollable log pad
        self.log_pad = curses.newpad(1000, self.width - 4)
        self.log_scroll_pos = 0
        self.max_log_display = self.height - 20
    
    def draw_border(self, win, y: int, x: int, height: int, width: int, 
                   title: str = "", color=None):
        """Draw a fancy border with title"""
        if color:
            win.attron(color)
        
        # Corners
        win.addch(y, x, '╔')
        win.addch(y, x + width - 1, '╗')
        win.addch(y + height - 1, x, '╚')
        win.addch(y + height - 1, x + width - 1, '╝')
        
        # Horizontal lines
        for i in range(1, width - 1):
            win.addch(y, x + i, '═')
            win.addch(y + height - 1, x + i, '═')
        
        # Vertical lines
        for i in range(1, height - 1):
            win.addch(y + i, x, '║')
            win.addch(y + i, x + width - 1, '║')
        
        # Title
        if title:
            title_str = f"╡ {title} ╞"
            title_x = x + (width - len(title_str)) // 2
            if title_x > x:
                win.addstr(y, title_x, title_str, 
                          self.COLOR_HIGHLIGHT | curses.A_BOLD)
        
        if color:
            win.attroff(color)
    
    def draw_header(self):
        """Draw the main header banner"""
        header_text = "EXCELLENT SHOP CONVERTER"
        version = "v2.0"
        
        # Full width header bar
        self.stdscr.attron(self.COLOR_HEADER | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * self.width)
        
        # Center the title
        title_x = (self.width - len(header_text)) // 2
        self.stdscr.addstr(0, title_x, header_text)
        
        # Version in corner
        self.stdscr.addstr(0, self.width - len(version) - 2, version)
        self.stdscr.attroff(self.COLOR_HEADER | curses.A_BOLD)
        
        # Subtitle
        subtitle = "Plugin Shop Format Converter"
        sub_x = (self.width - len(subtitle)) // 2
        self.stdscr.addstr(1, sub_x, subtitle, self.COLOR_INFO)
        
        # Separator
        self.stdscr.addstr(2, 0, "═" * self.width, self.COLOR_INFO)
    
    def draw_status_panel(self, y: int):
        """Draw current status and operation panel"""
        panel_width = self.width // 2 - 2
        
        self.draw_border(self.stdscr, y, 1, 6, panel_width, "Current Status", 
                        self.COLOR_INFO)
        
        # Elapsed time
        elapsed = int(time.time() - self.start_time)
        time_str = f"{elapsed // 60:02d}:{elapsed % 60:02d}"
        
        self.stdscr.addstr(y + 1, 3, f"⏱  Time Elapsed: ", self.COLOR_INFO)
        self.stdscr.addstr(time_str, self.COLOR_HIGHLIGHT | curses.A_BOLD)
        
        # Current operation
        self.stdscr.addstr(y + 2, 3, f"⚙  Operation: ", self.COLOR_INFO)
        op_text = self.current_operation[:panel_width - 20]
        self.stdscr.addstr(op_text, self.COLOR_HIGHLIGHT)
        
        # Progress bar
        if self.progress['total'] > 0:
            self.stdscr.addstr(y + 3, 3, f"📊 Progress: ", self.COLOR_INFO)
            
            bar_width = panel_width - 18
            percentage = int((self.progress['current'] / self.progress['total']) * 100)
            filled = int((self.progress['current'] / self.progress['total']) * bar_width)
            
            self.stdscr.addstr(y + 4, 3, f"   [{percentage:3d}%] ", 
                             self.COLOR_INFO | curses.A_BOLD)
            
            # Progress bar
            bar_start = 13
            self.stdscr.addstr(y + 4, bar_start, "█" * filled, self.COLOR_SUCCESS)
            self.stdscr.addstr("░" * (bar_width - filled), self.COLOR_INFO)
            
            # Count
            count_str = f" {self.progress['current']}/{self.progress['total']}"
            self.stdscr.addstr(y + 4, bar_start + bar_width + 1, count_str, 
                             self.COLOR_INFO)
    
    def draw_stats_panel(self, y: int):
        """Draw statistics panel"""
        panel_width = self.width // 2 - 2
        panel_x = self.width // 2 + 1
        
        self.draw_border(self.stdscr, y, panel_x, 6, panel_width, "Statistics", 
                        self.COLOR_SUCCESS)
        
        # Success
        self.stdscr.addstr(y + 1, panel_x + 3, "✓ Success: ", self.COLOR_SUCCESS)
        self.stdscr.addstr(f"{self.stats['success']:4d}", 
                          self.COLOR_SUCCESS | curses.A_BOLD)
        
        # Skipped
        self.stdscr.addstr(y + 2, panel_x + 3, "⊘ Skipped: ", self.COLOR_WARNING)
        self.stdscr.addstr(f"{self.stats['skipped']:4d}", 
                          self.COLOR_WARNING | curses.A_BOLD)
        
        # Errors
        self.stdscr.addstr(y + 3, panel_x + 3, "✗ Errors:  ", self.COLOR_ERROR)
        self.stdscr.addstr(f"{self.stats['errors']:4d}", 
                          self.COLOR_ERROR | curses.A_BOLD)
        
        # Total
        total = (self.stats['success'] + self.stats['skipped'] + 
                self.stats['errors'])
        self.stdscr.addstr(y + 4, panel_x + 3, "━ Total:   ", self.COLOR_INFO)
        self.stdscr.addstr(f"{total:4d}", self.COLOR_INFO | curses.A_BOLD)
    
    def draw_log_panel(self, y: int):
        """Draw scrollable log panel"""
        panel_height = self.height - y - 1
        
        self.draw_border(self.stdscr, y, 1, panel_height, self.width - 2, 
                        "Conversion Log", self.COLOR_INFO)
        
        # Instructions
        help_text = "↑↓ Scroll | Q Quit"
        self.stdscr.addstr(y, self.width - len(help_text) - 5, help_text, 
                          self.COLOR_WARNING)
        
        # Display logs from pad
        log_display_height = panel_height - 2
        log_display_width = self.width - 4
        
        # Update log pad with all messages
        self.log_pad.clear()
        for i, (timestamp, level, message) in enumerate(self.log_messages):
            color = self.COLOR_INFO
            icon = "•"
            
            if level == "SUCCESS":
                color = self.COLOR_SUCCESS
                icon = "✓"
            elif level == "ERROR":
                color = self.COLOR_ERROR
                icon = "✗"
            elif level == "WARNING":
                color = self.COLOR_WARNING
                icon = "⚠"
            
            log_line = f" {icon} [{timestamp}] {message}"
            
            # Word wrap long messages
            if len(log_line) > log_display_width:
                log_line = log_line[:log_display_width - 3] + "..."
            
            try:
                self.log_pad.addstr(i, 0, log_line, color)
            except curses.error:
                pass
        
        # Auto-scroll to bottom
        max_scroll = max(0, len(self.log_messages) - log_display_height)
        self.log_scroll_pos = max_scroll
        
        # Refresh the visible portion of the pad
        try:
            self.log_pad.refresh(
                self.log_scroll_pos, 0,
                y + 1, 2,
                y + log_display_height, self.width - 3
            )
        except curses.error:
            pass
    
    def draw_dashboard(self):
        """Draw the complete dashboard"""
        self.stdscr.clear()
        
        # Header
        self.draw_header()
        
        # Status and Stats panels (side by side)
        self.draw_status_panel(4)
        self.draw_stats_panel(4)
        
        # Log panel (bottom, full width)
        self.draw_log_panel(11)
        
        self.stdscr.refresh()
    
    def add_log(self, message: str, level: str = "INFO"):
        """Add a log message and update display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_messages.append((timestamp, level, message))
        
        # Keep only last 500 messages
        if len(self.log_messages) > 500:
            self.log_messages.pop(0)
        
        # Update stats
        if level == "SUCCESS":
            self.stats['success'] += 1
        elif level == "ERROR":
            self.stats['errors'] += 1
        elif level == "WARNING":
            self.stats['skipped'] += 1
        
        self.stats['total'] = (self.stats['success'] + 
                               self.stats['skipped'] + 
                               self.stats['errors'])
    
    def update_operation(self, operation: str):
        """Update current operation"""
        self.current_operation = operation
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress information"""
        self.progress = {
            'current': current,
            'total': total,
            'message': message
        }
    
    def show_menu(self, title: str, options: List[str], description: str = "") -> int:
        """Show an interactive menu with arrow key navigation"""
        selected = 0
        
        while True:
            self.stdscr.clear()
            self.draw_header()
            
            # Description
            if description:
                desc_y = 4
                for line in description.split('\n'):
                    desc_x = (self.width - len(line)) // 2
                    self.stdscr.addstr(desc_y, desc_x, line, self.COLOR_INFO)
                    desc_y += 1
                menu_y = desc_y + 2
            else:
                menu_y = 5
            
            # Menu box
            box_width = max(len(opt) for opt in options) + 8
            box_height = len(options) + 2
            box_x = (self.width - box_width) // 2
            
            self.draw_border(self.stdscr, menu_y, box_x, box_height, box_width, 
                           title, self.COLOR_HIGHLIGHT)
            
            # Options
            for i, option in enumerate(options):
                opt_y = menu_y + i + 1
                
                if i == selected:
                    # Highlighted option
                    self.stdscr.addstr(opt_y, box_x + 2, "►", 
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD)
                    self.stdscr.addstr(opt_y, box_x + 4, option, 
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD | curses.A_REVERSE)
                else:
                    self.stdscr.addstr(opt_y, box_x + 2, " ")
                    self.stdscr.addstr(opt_y, box_x + 4, option)
            
            # Instructions
            instructions = "Use ↑↓ arrows to navigate, Enter to select"
            inst_x = (self.width - len(instructions)) // 2
            self.stdscr.addstr(self.height - 2, inst_x, instructions, 
                             self.COLOR_WARNING)
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(options) - 1:
                selected += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                return selected
            elif key == ord('q') or key == ord('Q'):
                return -1
    
    def get_input(self, prompt: str, default: str = "", 
                 input_type: str = "text") -> str:
        """Get user input with a nice interface"""
        self.stdscr.clear()
        self.draw_header()
        
        # Input box
        box_width = 60
        box_height = 5
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        self.draw_border(self.stdscr, box_y, box_x, box_height, box_width, 
                        "Input Required", self.COLOR_INFO)
        
        # Prompt
        self.stdscr.addstr(box_y + 1, box_x + 2, prompt, 
                          self.COLOR_INFO | curses.A_BOLD)
        
        # Default value hint
        if default:
            hint = f"(default: {default})"
            self.stdscr.addstr(box_y + 2, box_x + 2, hint, self.COLOR_WARNING)
        
        # Input field
        input_y = box_y + 3
        input_x = box_x + 2
        
        curses.echo()
        curses.curs_set(1)
        
        self.stdscr.addstr(input_y, input_x, "> ", self.COLOR_HIGHLIGHT)
        self.stdscr.addstr(input_y, input_x + 2, " " * (box_width - 6))
        
        try:
            input_str = self.stdscr.getstr(input_y, input_x + 2, 
                                          box_width - 6).decode('utf-8').strip()
        except:
            input_str = ""
        
        curses.noecho()
        curses.curs_set(0)
        
        return input_str if input_str else default
    
    def show_completion(self):
        """Show completion screen"""
        self.stdscr.clear()
        self.draw_header()
        
        # Success banner
        banner_y = 5
        banner_lines = [
            "╔═══════════════════════════════════════╗",
            "║                                       ║",
            "║     CONVERSION COMPLETED! ✓           ║",
            "║                                       ║",
            "╚═══════════════════════════════════════╝"
        ]
        
        for i, line in enumerate(banner_lines):
            line_x = (self.width - len(line)) // 2
            color = self.COLOR_SUCCESS | curses.A_BOLD
            self.stdscr.addstr(banner_y + i, line_x, line, color)
        
        # Stats summary
        stats_y = banner_y + len(banner_lines) + 2
        
        total = (self.stats['success'] + self.stats['skipped'] + 
                self.stats['errors'])
        elapsed = int(time.time() - self.start_time)
        
        summary = [
            f"Total Shops Processed: {total}",
            f"Successful: {self.stats['success']}",
            f"Skipped Items: {self.stats['skipped']}",
            f"Errors: {self.stats['errors']}",
            f"Time Elapsed: {elapsed // 60:02d}:{elapsed % 60:02d}",
        ]
        
        for i, line in enumerate(summary):
            line_x = (self.width - len(line)) // 2
            
            if "Successful" in line:
                color = self.COLOR_SUCCESS
            elif "Errors" in line:
                color = self.COLOR_ERROR
            elif "Skipped" in line:
                color = self.COLOR_WARNING
            else:
                color = self.COLOR_INFO
            
            self.stdscr.addstr(stats_y + i, line_x, line, color | curses.A_BOLD)
        
        # Exit instruction
        exit_msg = "Press any key to exit..."
        exit_x = (self.width - len(exit_msg)) // 2
        self.stdscr.addstr(self.height - 3, exit_x, exit_msg, 
                          self.COLOR_HIGHLIGHT | curses.A_BLINK)
        
        self.stdscr.refresh()
        self.stdscr.getch()

    def show_yes_no(self, title: str, message: str) -> bool:
        """Show a yes/no dialog"""
        options = ["Yes", "No"]
        result = self.show_menu(title, options, message)
        return result == 0
    
    def show_shop_items_preview(self, shops_data: Dict[str, Dict]) -> None:
        """Display all shops and their items in a scrollable view"""
        self.stdscr.clear()
        self.draw_header()
        
        # Create content
        content_lines = []
        content_lines.append(("═" * (self.width - 4), self.COLOR_INFO))
        content_lines.append(("  SHOPS TO BE CONVERTED", self.COLOR_HIGHLIGHT | curses.A_BOLD))
        content_lines.append(("═" * (self.width - 4), self.COLOR_INFO))
        content_lines.append(("", 0))
        
        for shop_name, shop_info in shops_data.items():
            item_count = shop_info.get('item_count', 0)
            
            # Shop header
            shop_header = f"📦 {shop_name}"
            content_lines.append((shop_header, self.COLOR_SUCCESS | curses.A_BOLD))
            content_lines.append((f"   Items: {item_count}", self.COLOR_INFO))
            
            # Show first few items as preview
            items = shop_info.get('items', [])[:5]
            for item in items:
                material = item.get('material', 'unknown')
                buy = float(item.get('buy_price', 0))
                sell = float(item.get('sell_price', 0))
                item_line = f"   • {material} (Buy: ${buy:.2f}, Sell: ${sell:.2f})"
                content_lines.append((item_line, self.COLOR_INFO))
            
            if len(shop_info.get('items', [])) > 5:
                more = f"   ... and {len(shop_info.get('items', [])) - 5} more items"
                content_lines.append((more, self.COLOR_WARNING))
            
            content_lines.append(("", 0))
        
        # Display in scrollable window
        scroll_pos = 0
        max_display = self.height - 10
        
        while True:
            self.stdscr.clear()
            self.draw_header()
            
            # Display visible portion
            y = 4
            for i in range(scroll_pos, min(scroll_pos + max_display, len(content_lines))):
                if y >= self.height - 4:
                    break
                line, color = content_lines[i]
                try:
                    self.stdscr.addstr(y, 2, line[:self.width-4], color)
                except curses.error:
                    pass
                y += 1
            
            # Instructions
            instructions = "↑↓ Scroll | Enter to continue"
            self.stdscr.addstr(self.height - 2, 2, instructions, 
                             self.COLOR_WARNING | curses.A_BOLD)
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and scroll_pos > 0:
                scroll_pos -= 1
            elif key == curses.KEY_DOWN and scroll_pos < len(content_lines) - max_display:
                scroll_pos += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                break
            elif key == ord('q') or key == ord('Q'):
                break
    
    def edit_shop_items(self, shops_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Interactive editor for shops and items"""
        shop_names = list(shops_data.keys())
        selected_shop = 0
        
        while True:
            self.stdscr.clear()
            self.draw_header()
            
            # Shop list panel
            list_width = self.width // 3
            self.draw_border(self.stdscr, 4, 1, self.height - 6, list_width, 
                           "Shops", self.COLOR_INFO)
            
            # Display shops
            y = 5
            for i, shop_name in enumerate(shop_names):
                if y >= self.height - 3:
                    break
                
                item_count = shops_data[shop_name].get('item_count', 0)
                shop_line = f"{shop_name} ({item_count})"
                
                if i == selected_shop:
                    self.stdscr.addstr(y, 3, "►", self.COLOR_HIGHLIGHT | curses.A_BOLD)
                    self.stdscr.addstr(y, 5, shop_line[:list_width-7], 
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD | curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y, 5, shop_line[:list_width-7], self.COLOR_INFO)
                y += 1
            
            # Item details panel
            detail_x = list_width + 2
            detail_width = self.width - list_width - 3
            self.draw_border(self.stdscr, 4, detail_x, self.height - 6, detail_width,
                           "Items", self.COLOR_SUCCESS)
            
            # Display items for selected shop
            current_shop = shop_names[selected_shop]
            items = shops_data[current_shop].get('items', [])
            
            y = 5
            for i, item in enumerate(items[:self.height - 10]):
                material = item.get('material', 'unknown')
                buy = float(item.get('buy_price', 0))
                sell = float(item.get('sell_price', 0))
                
                item_line = f"• {material}"
                price_line = f"  Buy: ${buy:.2f} | Sell: ${sell:.2f}"
                
                try:
                    self.stdscr.addstr(y, detail_x + 2, item_line[:detail_width-4], 
                                     self.COLOR_SUCCESS)
                    self.stdscr.addstr(y + 1, detail_x + 2, price_line[:detail_width-4],
                                     self.COLOR_INFO)
                except curses.error:
                    pass
                y += 2
            
            if len(items) > self.height - 10:
                more_text = f"... and {len(items) - (self.height - 10)} more items"
                try:
                    self.stdscr.addstr(y, detail_x + 2, more_text, self.COLOR_WARNING)
                except curses.error:
                    pass
            
            # Instructions
            instructions = "↑↓ Navigate | Enter Edit Shop | C Continue | Q Quit"
            self.stdscr.addstr(self.height - 2, 2, instructions, 
                             self.COLOR_WARNING | curses.A_BOLD)
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected_shop > 0:
                selected_shop -= 1
            elif key == curses.KEY_DOWN and selected_shop < len(shop_names) - 1:
                selected_shop += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                # Edit items in selected shop
                shops_data[current_shop] = self._edit_shop_items_detail(
                    current_shop, shops_data[current_shop]
                )
            elif key == ord('c') or key == ord('C'):
                break
            elif key == ord('q') or key == ord('Q'):
                raise KeyboardInterrupt("User cancelled")
        
        return shops_data
    
    def _edit_shop_items_detail(self, shop_name: str, shop_data: Dict) -> Dict:
        """Edit items within a specific shop"""
        items = shop_data.get('items', [])
        selected_item = 0
        
        while True:
            self.stdscr.clear()
            self.draw_header()
            
            # Shop title
            title = f"Editing: {shop_name}"
            title_x = (self.width - len(title)) // 2
            self.stdscr.addstr(4, title_x, title, 
                             self.COLOR_HIGHLIGHT | curses.A_BOLD)
            
            # Item list
            list_y = 6
            list_height = self.height - 10
            
            self.draw_border(self.stdscr, list_y, 2, list_height, self.width - 4,
                           f"Items ({len(items)})", self.COLOR_INFO)
            
            # Display items
            y = list_y + 1
            display_start = max(0, selected_item - (list_height - 4) // 2)
            
            for i in range(display_start, min(display_start + list_height - 2, len(items))):
                if y >= list_y + list_height - 1:
                    break
                
                item = items[i]
                material = item.get('material', 'unknown')
                buy = float(item.get('buy_price', 0))
                sell = float(item.get('sell_price', 0))
                
                item_text = f"{material} - Buy: ${buy:.2f}, Sell: ${sell:.2f}"
                
                if i == selected_item:
                    self.stdscr.addstr(y, 4, "►", self.COLOR_HIGHLIGHT | curses.A_BOLD)
                    self.stdscr.addstr(y, 6, item_text[:self.width-10],
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD | curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y, 6, item_text[:self.width-10], self.COLOR_INFO)
                y += 1
            
            # Instructions
            instructions = "↑↓ Navigate | Enter Edit Item | D Delete | B Back"
            self.stdscr.addstr(self.height - 2, 2, instructions,
                             self.COLOR_WARNING | curses.A_BOLD)
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected_item > 0:
                selected_item -= 1
            elif key == curses.KEY_DOWN and selected_item < len(items) - 1:
                selected_item += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                # Edit selected item
                items[selected_item] = self._edit_single_item(items[selected_item])
            elif key == ord('d') or key == ord('D'):
                # Delete item
                if self.show_yes_no("Confirm Delete", 
                                   f"Delete {items[selected_item].get('material', 'item')}?"):
                    items.pop(selected_item)
                    if selected_item >= len(items) and selected_item > 0:
                        selected_item -= 1
            elif key == ord('b') or key == ord('B'):
                break
            elif key == ord('q') or key == ord('Q'):
                break
        
        shop_data['items'] = items
        shop_data['item_count'] = len(items)
        return shop_data
    
    def _edit_single_item(self, item: Dict) -> Dict:
        """Edit a single item's properties"""
        fields = ['material', 'buy_price', 'sell_price']
        selected_field = 0
        
        while True:
            self.stdscr.clear()
            self.draw_header()
            
            # Title
            title = f"Edit Item: {item.get('material', 'unknown')}"
            title_x = (self.width - len(title)) // 2
            self.stdscr.addstr(4, title_x, title,
                             self.COLOR_HIGHLIGHT | curses.A_BOLD)
            
            # Fields
            box_width = 60
            box_height = len(fields) + 4
            box_x = (self.width - box_width) // 2
            box_y = 7
            
            self.draw_border(self.stdscr, box_y, box_x, box_height, box_width,
                           "Properties", self.COLOR_INFO)
            
            y = box_y + 1
            for i, field in enumerate(fields):
                value = item.get(field, '')
                field_text = f"{field.replace('_', ' ').title()}: {value}"
                
                if i == selected_field:
                    self.stdscr.addstr(y, box_x + 2, "►", 
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD)
                    self.stdscr.addstr(y, box_x + 4, field_text[:box_width-6],
                                     self.COLOR_HIGHLIGHT | curses.A_BOLD | curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y, box_x + 4, field_text[:box_width-6],
                                     self.COLOR_INFO)
                y += 1
            
            # Instructions
            instructions = "↑↓ Navigate | Enter Edit | S Save | ESC Cancel"
            self.stdscr.addstr(self.height - 2, 2, instructions,
                             self.COLOR_WARNING | curses.A_BOLD)
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected_field > 0:
                selected_field -= 1
            elif key == curses.KEY_DOWN and selected_field < len(fields) - 1:
                selected_field += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                # Edit field
                field = fields[selected_field]
                current_value = str(item.get(field, ''))
                prompt = f"Enter new {field.replace('_', ' ')}:"
                new_value = self.get_input(prompt, current_value)
                
                if new_value:
                    if field in ['buy_price', 'sell_price']:
                        try:
                            item[field] = float(new_value)
                        except ValueError:
                            pass
                    else:
                        item[field] = new_value
            elif key == ord('s') or key == ord('S'):
                break
            elif key == 27:  # ESC
                break
        
        return item
