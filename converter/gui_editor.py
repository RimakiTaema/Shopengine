"""
GUI Editor for ExcellentShop - Chest-style GUI editing

This module provides a visual GUI editor similar to Minecraft chest GUI editors
like GUIPlus, supporting different chest sizes and ExcellentShop integration.
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ChestSize(Enum):
    """Supported chest sizes for GUI editing"""
    CHEST_9x1 = "generic_9x1"  # Single row
    CHEST_9x2 = "generic_9x2"  # Double chest
    CHEST_9x3 = "generic_9x3"  # Triple chest
    CHEST_9x4 = "generic_9x4"  # Quad chest
    CHEST_9x5 = "generic_9x5"  # Penta chest
    CHEST_9x6 = "generic_9x6"  # Hexa chest (max size)


@dataclass
class GUISlot:
    """Represents a slot in the GUI editor"""
    slot: int
    material: str = ""
    display_name: str = ""
    lore: List[str] = None
    enchantments: Dict[str, int] = None
    is_empty: bool = True
    
    def __post_init__(self):
        if self.lore is None:
            self.lore = []
        if self.enchantments is None:
            self.enchantments = {}


class GUIEditor:
    """Chest-style GUI editor for ExcellentShop"""
    
    def __init__(self, tui=None):
        self.tui = tui
        self.chest_size = ChestSize.CHEST_9x6  # Default to max size
        self.slots: Dict[int, GUISlot] = {}
        self.shop_name = ""
        self.currency = "coins"
        
    def select_chest_size(self) -> ChestSize:
        """Let user select chest size"""
        if self.tui:
            size_options = [
                "9x1 - Single Row (9 slots)",
                "9x2 - Double Chest (18 slots)", 
                "9x3 - Triple Chest (27 slots)",
                "9x4 - Quad Chest (36 slots)",
                "9x5 - Penta Chest (45 slots)",
                "9x6 - Hexa Chest (54 slots)"
            ]
            
            size_idx = self.tui.show_menu(
                "Select Chest Size",
                size_options,
                "Choose the size of your shop GUI"
            )
            
            if size_idx == -1:
                return None
                
            size_map = [
                ChestSize.CHEST_9x1,
                ChestSize.CHEST_9x2, 
                ChestSize.CHEST_9x3,
                ChestSize.CHEST_9x4,
                ChestSize.CHEST_9x5,
                ChestSize.CHEST_9x6
            ]
            
            return size_map[size_idx]
        else:
            # Console fallback
            print("\nChest Sizes:")
            print("1. 9x1 - Single Row (9 slots)")
            print("2. 9x2 - Double Chest (18 slots)")
            print("3. 9x3 - Triple Chest (27 slots)")
            print("4. 9x4 - Quad Chest (36 slots)")
            print("5. 9x5 - Penta Chest (45 slots)")
            print("6. 9x6 - Hexa Chest (54 slots)")
            
            choice = input("Select size (1-6): ").strip()
            try:
                size_map = [
                    ChestSize.CHEST_9x1,
                    ChestSize.CHEST_9x2,
                    ChestSize.CHEST_9x3, 
                    ChestSize.CHEST_9x4,
                    ChestSize.CHEST_9x5,
                    ChestSize.CHEST_9x6
                ]
                return size_map[int(choice) - 1]
            except (ValueError, IndexError):
                return ChestSize.CHEST_9x6  # Default
    
    def get_slot_count(self) -> int:
        """Get number of slots based on chest size"""
        size_map = {
            ChestSize.CHEST_9x1: 9,
            ChestSize.CHEST_9x2: 18,
            ChestSize.CHEST_9x3: 27,
            ChestSize.CHEST_9x4: 36,
            ChestSize.CHEST_9x5: 45,
            ChestSize.CHEST_9x6: 54
        }
        return size_map.get(self.chest_size, 54)
    
    def initialize_slots(self):
        """Initialize empty slots"""
        slot_count = self.get_slot_count()
        self.slots = {}
        for i in range(slot_count):
            self.slots[i] = GUISlot(slot=i, is_empty=True)
    
    def display_gui(self):
        """Display the current GUI state"""
        if not self.tui:
            self._display_gui_console()
            return
            
        # Clear screen and show GUI
        self.tui.clear()
        
        # Show header
        self.tui.add_log(f"GUI Editor - {self.shop_name} ({self.chest_size.value})", "INFO")
        self.tui.add_log("Use arrow keys to navigate, Enter to edit, 'q' to quit", "INFO")
        
        # Display grid
        rows = self.get_slot_count() // 9
        for row in range(rows):
            row_start = row * 9
            row_end = min(row_start + 9, self.get_slot_count())
            
            # Show row header
            self.tui.add_log(f"Row {row + 1}:", "INFO")
            
            # Show slots in this row
            slot_line = ""
            for slot in range(row_start, row_end):
                if self.slots[slot].is_empty:
                    slot_line += "[ ] "
                else:
                    slot_line += f"[{self.slots[slot].material.split(':')[-1][:3]}] "
            
            self.tui.add_log(slot_line, "INFO")
        
        self.tui.draw_dashboard()
    
    def _display_gui_console(self):
        """Console version of GUI display"""
        print(f"\nGUI Editor - {self.shop_name} ({self.chest_size.value})")
        print("=" * 50)
        
        rows = self.get_slot_count() // 9
        for row in range(rows):
            print(f"\nRow {row + 1}:")
            row_start = row * 9
            row_end = min(row_start + 9, self.get_slot_count())
            
            # Show slot numbers and contents
            for slot in range(row_start, row_end):
                if self.slots[slot].is_empty:
                    print(f"  {slot:2d}: [Empty]")
                else:
                    material = self.slots[slot].material.split(':')[-1]
                    print(f"  {slot:2d}: [{material}] {self.slots[slot].display_name}")
    
    def edit_slot(self, slot: int) -> bool:
        """Edit a specific slot"""
        if slot not in self.slots:
            return False
            
        slot_obj = self.slots[slot]
        
        if self.tui:
            self.tui.add_log(f"Editing slot {slot}", "INFO")
            
            # Get material
            material = self.tui.get_input(f"Material (minecraft:item_name) for slot {slot}:", 
                                        slot_obj.material or "minecraft:stone")
            if not material:
                return False
                
            # Get display name
            display_name = self.tui.get_input(f"Display name for slot {slot}:", 
                                            slot_obj.display_name or "")
            
            # Get lore (simplified)
            lore_input = self.tui.get_input(f"Lore (comma-separated) for slot {slot}:", 
                                          ",".join(slot_obj.lore) if slot_obj.lore else "")
            lore = [line.strip() for line in lore_input.split(",") if line.strip()] if lore_input else []
            
            # Get enchantments (simplified)
            enchants_input = self.tui.get_input(f"Enchantments (name:level,name:level) for slot {slot}:", 
                                              ",".join([f"{k}:{v}" for k, v in slot_obj.enchantments.items()]) if slot_obj.enchantments else "")
            enchantments = {}
            if enchants_input:
                for enchant in enchants_input.split(","):
                    if ":" in enchant:
                        name, level = enchant.strip().split(":", 1)
                        try:
                            enchantments[name.strip()] = int(level.strip())
                        except ValueError:
                            pass
            
            # Update slot
            slot_obj.material = material
            slot_obj.display_name = display_name
            slot_obj.lore = lore
            slot_obj.enchantments = enchantments
            slot_obj.is_empty = False
            
            self.tui.add_log(f"Slot {slot} updated: {material}", "SUCCESS")
            return True
        else:
            # Console fallback
            print(f"\nEditing slot {slot}:")
            material = input(f"Material (minecraft:item_name) [{slot_obj.material or 'minecraft:stone'}]: ").strip()
            if not material:
                material = slot_obj.material or "minecraft:stone"
                
            display_name = input(f"Display name [{slot_obj.display_name or ''}]: ").strip()
            lore_input = input(f"Lore (comma-separated) [{','.join(slot_obj.lore) if slot_obj.lore else ''}]: ").strip()
            lore = [line.strip() for line in lore_input.split(",") if line.strip()] if lore_input else []
            
            enchants_input = input(f"Enchantments (name:level,name:level) [{','.join([f'{k}:{v}' for k, v in slot_obj.enchantments.items()]) if slot_obj.enchantments else ''}]: ").strip()
            enchantments = {}
            if enchants_input:
                for enchant in enchants_input.split(","):
                    if ":" in enchant:
                        name, level = enchant.strip().split(":", 1)
                        try:
                            enchantments[name.strip()] = int(level.strip())
                        except ValueError:
                            pass
            
            # Update slot
            slot_obj.material = material
            slot_obj.display_name = display_name
            slot_obj.lore = lore
            slot_obj.enchantments = enchantments
            slot_obj.is_empty = False
            
            print(f"Slot {slot} updated: {material}")
            return True
    
    def clear_slot(self, slot: int):
        """Clear a specific slot"""
        if slot in self.slots:
            self.slots[slot] = GUISlot(slot=slot, is_empty=True)
    
    def export_to_excellentshop(self, output_path: str) -> bool:
        """Export the GUI to ExcellentShop format"""
        try:
            # Create ExcellentShop structure
            excellentshop_data = {
                'Settings': {
                    'Aliases': [],
                    'Name': f'<soft_yellow><b>{self.shop_name}</b></soft_yellow>',
                    'Description': [],
                    'Icon': {
                        'Material': 'minecraft:chest',
                        'Lore': []
                    },
                    'Permission_Required': False,
                    'Buying': True,
                    'Selling': True,
                    'Pages': 1,
                    'MainMenu': {'Slot': 10},
                    'Layout': {
                        'Paginated': False,
                        'ByPage': {'0': self.chest_size.value}
                    }
                },
                'Items': {}
            }
            
            # Add items from slots
            for slot, slot_obj in self.slots.items():
                if not slot_obj.is_empty:
                    item_key = slot_obj.material.lower().replace(':', '_')
                    
                    excellentshop_data['Items'][item_key] = {
                        'Type': 'ITEM',
                        'Item': {
                            'Provider': 'vanilla',
                            'Data': {
                                'Value': f'{{count:1,id:"{slot_obj.material}"}}',
                                'DataVersion': 4189,
                                'Enchantments': [{'id': k, 'lvl': v} for k, v in slot_obj.enchantments.items()]
                            },
                            'CompareNBT': False
                        },
                        'Rotating': False,
                        'Allowed_Ranks': [],
                        'Required_Permissions': [],
                        'Forbidden_Permissions': [],
                        'Currency': self.currency,
                        'Price': {
                            'Type': 'FLAT',
                            'BUY': 100.0,
                            'SELL': 50.0
                        },
                        'Stock': {
                            'GLOBAL': {
                                'BuyAmount': -1,
                                'SellAmount': -1,
                                'RestockTime': 0
                            },
                            'PLAYER': {
                                'BuyAmount': -1,
                                'SellAmount': -1,
                                'RestockTime': 0
                            }
                        },
                        'Shop_View': {
                            'Slot': slot,
                            'Page': 1
                        }
                    }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(excellentshop_data, f, default_flow_style=False, 
                         sort_keys=False, allow_unicode=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to export GUI: {e}")
            return False
    
    def run_editor(self) -> bool:
        """Run the main GUI editor loop"""
        # Get shop name
        if self.tui:
            self.shop_name = self.tui.get_input("Enter shop name:", "MyShop")
        else:
            self.shop_name = input("Enter shop name: ").strip() or "MyShop"
        
        # Select chest size
        self.chest_size = self.select_chest_size()
        if not self.chest_size:
            return False
            
        # Initialize slots
        self.initialize_slots()
        
        # Main editor loop
        while True:
            self.display_gui()
            
            if self.tui:
                # TUI mode
                self.tui.add_log("Commands: slot_number to edit, 'clear slot_number' to clear, 'save' to save, 'quit' to exit", "INFO")
                command = self.tui.get_input("Enter command:", "")
                
                if command.lower() in ['quit', 'q', 'exit']:
                    break
                elif command.lower() == 'save':
                    output_path = self.tui.get_input("Output file path:", f"{self.shop_name}.yml")
                    if self.export_to_excellentshop(output_path):
                        self.tui.add_log(f"GUI saved to {output_path}", "SUCCESS")
                    else:
                        self.tui.add_log("Failed to save GUI", "ERROR")
                    self.tui.draw_dashboard()
                elif command.startswith('clear '):
                    try:
                        slot = int(command.split()[1])
                        self.clear_slot(slot)
                        self.tui.add_log(f"Slot {slot} cleared", "SUCCESS")
                    except (ValueError, IndexError):
                        self.tui.add_log("Invalid slot number", "ERROR")
                elif command.isdigit():
                    try:
                        slot = int(command)
                        if 0 <= slot < self.get_slot_count():
                            self.edit_slot(slot)
                        else:
                            self.tui.add_log("Invalid slot number", "ERROR")
                    except ValueError:
                        self.tui.add_log("Invalid command", "ERROR")
                else:
                    self.tui.add_log("Invalid command", "ERROR")
            else:
                # Console mode
                print("\nCommands: slot_number to edit, 'clear slot_number' to clear, 'save' to save, 'quit' to exit")
                command = input("Enter command: ").strip()
                
                if command.lower() in ['quit', 'q', 'exit']:
                    break
                elif command.lower() == 'save':
                    output_path = input("Output file path: ").strip() or f"{self.shop_name}.yml"
                    if self.export_to_excellentshop(output_path):
                        print(f"GUI saved to {output_path}")
                    else:
                        print("Failed to save GUI")
                elif command.startswith('clear '):
                    try:
                        slot = int(command.split()[1])
                        self.clear_slot(slot)
                        print(f"Slot {slot} cleared")
                    except (ValueError, IndexError):
                        print("Invalid slot number")
                elif command.isdigit():
                    try:
                        slot = int(command)
                        if 0 <= slot < self.get_slot_count():
                            self.edit_slot(slot)
                        else:
                            print("Invalid slot number")
                    except ValueError:
                        print("Invalid command")
                else:
                    print("Invalid command")
        
        return True