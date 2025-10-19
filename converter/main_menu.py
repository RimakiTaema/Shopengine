"""
Main menu for the Shop Converter TUI.
"""
import sys
import logging
from curses import wrapper

from .engine import ShopConverterEngine
from .ui import ShopConverterTUI
from converter.utils import init_folders
from converter.constants import SUPPORTED_PLUGINS

logger = logging.getLogger(__name__)

def main_menu(stdscr):
    """
    Displays the main menu and handles user input.
    """
    tui = ShopConverterTUI(stdscr)
    engine = ShopConverterEngine(tui=tui)

    while True:
        menu_items = [
            "Convert Shops",
            "Initialize Folders",
            "Exit"
        ]
        
        option = tui.show_menu(
            "Shop Converter",
            menu_items,
            "Select an option to begin."
        )

        if option == 0:
            # Convert Shops
            try:
                engine.convert_shops()
            except Exception as e:
                logger.exception("Error during shop conversion")
                tui.add_log(f"An unexpected error occurred: {e}", "ERROR")
                tui.draw_dashboard()


        elif option == 1:
            # Initialize Folders
            try:
                init_folders()
                tui.add_log("Folder structure initialized successfully!", "SUCCESS")
                for plugin in SUPPORTED_PLUGINS:
                    tui.add_log(f"  - shops_to_convert/{plugin}/", "INFO")
                tui.draw_dashboard()
            except Exception as e:
                logger.exception("Error initializing folders")
                tui.add_log(f"Error initializing folders: {e}", "ERROR")
                tui.draw_dashboard()


        elif option == 2 or option == -1:
            # Exit
            break
