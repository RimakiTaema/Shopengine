#!/usr/bin/env python3
"""
ExcellentShop Converter - Main Entry Point

A comprehensive tool for converting shop configurations between various Minecraft 
economy plugins and ExcellentShop format. Supports bidirectional conversion with 
a modern terminal user interface.

Features:
    - Convert from ESGUI, DShop3, UltimateShop to ExcellentShop
    - Convert from ExcellentShop back to other plugin formats
    - Interactive TUI with real-time progress tracking
    - Support for complex pricing models (FLAT, FLOAT, DYNAMIC, PLAYER_AMOUNT)
    - Comprehensive error handling and logging

Usage:
    python3 shop-converter.py          # Run converter with TUI
    python3 shop-converter.py init     # Initialize folder structure

Author: RimakiTaema
Version: 2.0.0
"""

import sys
import logging
import curses
from curses import wrapper

from converter.main_menu import main_menu
from converter.utils import init_folders
from converter.constants import SUPPORTED_PLUGINS

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('shop_converter.log', encoding='utf-8'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the shop converter"""
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'init':
        try:
            init_folders()
            print("✓ Folder structure initialized!")
            print("\nCreated directories:")
            for plugin in SUPPORTED_PLUGINS:
                print(f"  - shops_to_convert/{plugin}/")
            print("\nPlace your shop files in the appropriate plugin folder.")
        except Exception as e:
            print(f"\n✗ Failed to initialize folders: {e}")
            logger.exception("Failed to initialize folders")
            sys.exit(1)
    else:
        try:
            wrapper(main_menu)
        except KeyboardInterrupt:
            print("\n\n⊘ Conversion cancelled by user.")
            logger.info("User cancelled conversion")
        except curses.error as e:
            print(f"\n\n✗ Terminal error: {e}")
            print("Try running in a different terminal or check terminal compatibility.")
            logger.exception("Terminal error occurred")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n✗ Fatal error: {e}")
            logger.exception("Fatal error occurred")
            sys.exit(1)


if __name__ == '__main__':
    main()
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'init':
        try:
            init_folders()
            print("✓ Folder structure initialized!")
            print("\nCreated directories:")
            for plugin in SUPPORTED_PLUGINS:
                print(f"  - shops_to_convert/{plugin}/")
            print("\nPlace your shop files in the appropriate plugin folder.")
        except Exception as e:
            print(f"\n✗ Failed to initialize folders: {e}")
            logger.exception("Failed to initialize folders")
            sys.exit(1)
    else:
        try:
            wrapper(main_menu)
        except KeyboardInterrupt:
            print("\n\n⊘ Conversion cancelled by user.")
            logger.info("User cancelled conversion")
        except curses.error as e:
            print(f"\n\n✗ Terminal error: {e}")
            print("Try running in a different terminal or check terminal compatibility.")
            logger.exception("Terminal error occurred")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n✗ Fatal error: {e}")
            logger.exception("Fatal error occurred")
            sys.exit(1)
