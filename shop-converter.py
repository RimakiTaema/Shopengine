#!/usr/bin/env python3
"""
ExcellentShop Converter - Main Entry Point
Converts shop configurations from various Minecraft economy plugins to ExcellentShop format.

Usage:
    python shop-converter.py          # Run converter with TUI
    python shop-converter.py init     # Initialize folder structure
"""

import sys
import logging
from curses import wrapper

from converter import ShopConverterEngine, ShopConverterTUI
from converter.utils import init_folders
from converter.constants import SUPPORTED_PLUGINS

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('shop_converter.log')
    ]
)
logger = logging.getLogger(__name__)


def main(stdscr):
    """Main function with full TUI"""
    tui = ShopConverterTUI(stdscr)
    
    tui.add_log("Shop Converter initialized", "INFO")
    tui.add_log("Scanning for shops to convert...", "INFO")
    tui.update_operation("Initializing conversion engine")
    tui.draw_dashboard()
    
    import time
    time.sleep(1)
    
    engine = ShopConverterEngine(tui=tui)
    engine.convert_shops()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'init':
        init_folders()
        print("✓ Folder structure initialized!")
        print("\nCreated directories:")
        for plugin in SUPPORTED_PLUGINS:
            print(f"  - shops_to_convert/{plugin}/")
        print("\nPlace your shop files in the appropriate plugin folder.")
    else:
        try:
            wrapper(main)
        except KeyboardInterrupt:
            print("\n\n⊘ Conversion cancelled by user.")
        except Exception as e:
            print(f"\n\n✗ Fatal error: {e}")
            logger.exception("Fatal error occurred")
