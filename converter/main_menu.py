"""
Main menu for the Shop Converter TUI.
"""
import sys
import logging
from curses import wrapper

from converter.engine import ShopConverterEngine
from converter.ui import ShopConverterTUI
from converter.utils import init_folders
from converter.constants import SUPPORTED_PLUGINS

logger = logging.getLogger(__name__)

def main_menu(stdscr) -> None:
    """
    Displays the main menu and handles user input.
    """
    tui = ShopConverterTUI(stdscr)
    engine = ShopConverterEngine(tui=tui)

    while True:
        menu_items = [
            "Convert Shops (To ExcellentShop)",
            "Convert from ExcellentShop",
            "Initialize Folders",
            "Exit"
        ]
        
        option = tui.show_menu(
            "Shop Converter",
            menu_items,
            "Select an option to begin."
        )

        if option == 0:
            # Convert Shops (To ExcellentShop)
            try:
                engine.convert_shops()
            except Exception as e:
                logger.exception("Error during shop conversion")
                tui.add_log(f"An unexpected error occurred: {e}", "ERROR")
                tui.draw_dashboard()

        elif option == 1:
            # Convert from ExcellentShop
            try:
                # Ask user for target format
                format_options = ["ESGUI (Beta)", "DShop3 (Soon)", "UltimateShop (Soon)"]
                format_idx = tui.show_menu(
                    "Select Target Format",
                    format_options,
                    "Choose which plugin format to convert to"
                )
                
                if format_idx != -1:
                    if format_idx == 0:  # ESGUI (Beta)
                        target_format = "esgui"
                        engine.convert_from_excellentshop(target_format)
                    else:  # DShop3 or UltimateShop (Soon)
                        tui.add_log("This feature is not yet implemented", "WARNING")
                        tui.add_log("Please check back in a future update", "INFO")
                        tui.draw_dashboard()
                        tui.get_input("Press Enter to continue...", "")
            except Exception as e:
                logger.exception("Error during reverse conversion")
                tui.add_log(f"An unexpected error occurred: {e}", "ERROR")
                tui.draw_dashboard()

        elif option == 2:
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

        elif option == 3 or option == -1:
            # Exit
            break
