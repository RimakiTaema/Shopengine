"""Main conversion engine for shop converter"""

import os
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from .models import PriceConfig, PriceFormat, ItemConfig
from .parsers import SOURCE_PLUGIN_CONVERTERS
from .constants import SHOP_METADATA
from .utils import create_excellent_shop_item

logger = logging.getLogger(__name__)


def get_price_config_interactive(shop_name: str, tui=None) -> Tuple[PriceConfig, str]:
    """Interactive price configuration with enhanced TUI"""
    
    if tui:
        tui.add_log(f"Pricing configuration needed for '{shop_name}'", "WARNING")
        tui.update_operation(f"Configuring prices for {shop_name}")
        tui.draw_dashboard()
        
        # Ask scope
        scope_idx = tui.show_menu(
            "Apply Pricing To",
            ["This shop only", "All remaining shops"],
            f"Shop '{shop_name}' requires pricing configuration"
        )
        
        if scope_idx == -1:
            raise KeyboardInterrupt("User cancelled")
        
        scope = 'this' if scope_idx == 0 else 'all'
        
        # Ask format
        format_idx = tui.show_menu(
            "Select Pricing Format",
            ["FLAT - Fixed buy/sell prices", 
             "FLOAT - Fluctuating prices with min/max",
             "DYNAMIC - Supply/demand based pricing"],
            "Choose how prices should be calculated"
        )
        
        if format_idx == -1:
            raise KeyboardInterrupt("User cancelled")
        
        price_format = [PriceFormat.FLAT, PriceFormat.FLOAT, PriceFormat.DYNAMIC][format_idx]
        
        extra = {}
        buy_price = sell_price = 0.0
        
        if price_format == PriceFormat.FLOAT:
            buy_price = float(tui.get_input("Minimum price:", "0") or 0)
            sell_price = float(tui.get_input("Maximum price:", "999999") or 999999)
            step = float(tui.get_input("Price step size:", "1") or 1)
            timer = int(tui.get_input("Update timer (seconds):", "30") or 30)
            extra = {'MIN': buy_price, 'MAX': sell_price, 'STEP': step, 'TIMER': timer}
        
        elif price_format == PriceFormat.DYNAMIC:
            buy_price = float(tui.get_input("Initial price:", "100") or 100)
            sell_price = buy_price
            step = float(tui.get_input("Price change step:", "10") or 10)
            min_p = float(tui.get_input("Minimum price:", "0") or 0)
            max_p = float(tui.get_input("Maximum price:", "999999") or 999999)
            extra = {'INITIAL': buy_price, 'STEP': step, 'MIN': min_p, 'MAX': max_p}
        
        else:  # FLAT
            buy_price = float(tui.get_input("Buy price:", "100") or 100)
            sell_price = float(tui.get_input("Sell price:", "50") or 50)
        
        tui.add_log(f"Price config set: {price_format.value} (scope: {scope})", "SUCCESS")
        
        return PriceConfig(price_format, buy_price, sell_price, extra), scope
    
    else:
        # Fallback to console
        logger.warning(f"Pricing not found for shop '{shop_name}'")
        
        scope = input("Apply to this shop or all? [this/all]: ").strip().lower() or 'this'
        
        print("Formats: FLAT, FLOAT, DYNAMIC")
        price_format_str = input("Format: ").strip().upper() or 'FLAT'
        
        try:
            price_format = PriceFormat[price_format_str]
        except KeyError:
            logger.warning(f"Invalid format, using FLAT")
            price_format = PriceFormat.FLAT
        
        extra = {}
        buy_price = sell_price = 0.0
        
        if price_format == PriceFormat.FLOAT:
            buy_price = float(input("Min price: ") or 0)
            sell_price = float(input("Max price: ") or 999999)
            step = float(input("Step: ") or 1)
            timer = int(input("Timer: ") or 30)
            extra = {'MIN': buy_price, 'MAX': sell_price, 'STEP': step, 'TIMER': timer}
        
        elif price_format == PriceFormat.DYNAMIC:
            buy_price = float(input("Initial: ") or 100)
            sell_price = buy_price
            step = float(input("Step: ") or 10)
            min_p = float(input("Min: ") or 0)
            max_p = float(input("Max: ") or 999999)
            extra = {'INITIAL': buy_price, 'STEP': step, 'MIN': min_p, 'MAX': max_p}
        
        else:
            buy_price = float(input("Buy: ") or 100)
            sell_price = float(input("Sell: ") or 50)
        
        return PriceConfig(price_format, buy_price, sell_price, extra), scope


class ShopConverterEngine:
    """Main conversion engine with enhanced TUI integration"""
    
    def __init__(self, source_folder: str = 'shops_to_convert', 
                 output_folder: str = 'excellentshop', 
                 currency: str = 'coins',
                 tui=None):
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.currency = currency
        self.tui = tui
        self.price_cache: Dict[str, PriceConfig] = {}
    
    def collect_shop_data(self) -> Dict[str, Dict]:
        """Collect all shop data for preview and editing"""
        shops_data = {}
        
        if not os.path.exists(self.source_folder):
            return shops_data
        
        for plugin_type in os.listdir(self.source_folder):
            plugin_path = os.path.join(self.source_folder, plugin_type)
            
            if not os.path.isdir(plugin_path) or plugin_type not in SOURCE_PLUGIN_CONVERTERS:
                continue
            
            converter = SOURCE_PLUGIN_CONVERTERS[plugin_type]
            
            for file_name in os.listdir(plugin_path):
                if not file_name.endswith('.yml'):
                    continue
                
                shop_name = Path(file_name).stem
                input_path = os.path.join(plugin_path, file_name)
                
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        source_data = yaml.safe_load(f) or {}
                    
                    items = []
                    pages = source_data.get('pages', {})
                    
                    for page_name, page_data in pages.items():
                        if not isinstance(page_data, dict):
                            continue
                        for item_slot, item_data in page_data.get('items', {}).items():
                            if not isinstance(item_data, dict):
                                continue
                            item_config = converter.convert_item(item_data)
                            
                            if item_config and item_config.material:
                                try:
                                    items.append({
                                        'material': item_config.material,
                                        'buy_price': float(item_config.buy_price) if item_config.buy_price is not None else 0.0,
                                        'sell_price': float(item_config.sell_price) if item_config.sell_price is not None else 0.0,
                                        'slot': int(item_slot) - 1,
                                        'page': self._extract_page_number(page_name)
                                    })
                                except (ValueError, TypeError) as ve:
                                    logger.warning(f"Invalid data for item in {shop_name}: {ve}")
                                    continue
                    
                    shops_data[shop_name] = {
                        'items': items,
                        'item_count': len(items),
                        'plugin_type': plugin_type,
                        'input_path': input_path
                    }
                
                except (yaml.YAMLError, IOError, OSError) as e:
                    logger.error(f"Failed to collect data for {shop_name}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error collecting data for {shop_name}: {e}")
        
        return shops_data
    
    def convert_shops(self) -> None:
        """Convert all shops with real-time TUI updates"""
        if not os.path.exists(self.source_folder):
            msg = f"Source folder '{self.source_folder}' not found"
            logger.error(msg)
            if self.tui:
                self.tui.add_log(msg, "ERROR")
                self.tui.draw_dashboard()
                time.sleep(2)
            return
        
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Collect shop data
        if self.tui:
            self.tui.update_operation("Collecting shop data...")
            self.tui.draw_dashboard()
        
        shops_data = self.collect_shop_data()
        total_shops = len(shops_data)
        
        if total_shops == 0:
            if self.tui:
                self.tui.add_log("No shops found to convert", "WARNING")
                self.tui.draw_dashboard()
                time.sleep(2)
            return
        
        if self.tui:
            self.tui.add_log(f"Found {total_shops} shops to convert", "INFO")
            self.tui.draw_dashboard()
            time.sleep(0.5)
            
            # Show preview
            self.tui.show_shop_items_preview(shops_data)
            
            # Ask if user wants to edit items
            if self.tui.show_yes_no("Edit Items?", 
                                   "Do you want to edit items before conversion?"):
                shops_data = self.tui.edit_shop_items(shops_data)
            
            self.tui.update_progress(0, total_shops, "Starting conversion...")
            self.tui.draw_dashboard()
            time.sleep(0.5)
        
        current_shop = 0
        
        # Convert shops
        for shop_name, shop_info in shops_data.items():
            current_shop += 1
            
            if self.tui:
                self.tui.update_operation(f"Converting: {shop_name}")
                self.tui.update_progress(current_shop, total_shops, shop_name)
                self.tui.draw_dashboard()
            
            try:
                self._convert_shop_from_data(shop_name, shop_info)
            except Exception as e:
                msg = f"Failed to convert {shop_name}: {e}"
                logger.error(msg)
                if self.tui:
                    self.tui.add_log(msg, "ERROR")
                    self.tui.draw_dashboard()
        
        if self.tui:
            self.tui.update_operation("Conversion complete!")
            self.tui.draw_dashboard()
            time.sleep(1)
            self.tui.show_completion()
        else:
            self._print_console_stats()
    
    def _convert_shop_from_data(self, shop_name: str, shop_info: Dict) -> None:
        """Convert a shop from collected data"""
        items = shop_info.get('items', [])
        
        if not items:
            if self.tui:
                self.tui.add_log(f"Skipped {shop_name} (no items)", "WARNING")
            return
        
        # Get price configuration
        price_config, scope = self._get_or_cache_price_config(shop_name)
        
        # Determine page count
        max_page = max((item.get('page', 0) for item in items), default=0)
        page_count = max_page + 1
        
        # Create shop structure
        excellent_shop = self._create_shop_structure(shop_name, page_count, price_config)
        
        # Add items
        item_count = 0
        for item_data in items:
            material = item_data.get('material')
            if not material:
                continue
            
            item_config = ItemConfig(
                material=material,
                buy_price=item_data.get('buy_price', price_config.buy_price),
                sell_price=item_data.get('sell_price', price_config.sell_price),
                slot=item_data.get('slot', 0),
                page=item_data.get('page', 0)
            )
            
            item_key = self._get_unique_item_key(material, str(item_config.slot), excellent_shop)
            
            created_item = create_excellent_shop_item(item_config, self.currency, price_config)
            if created_item:
                excellent_shop['Items'][item_key] = created_item
                item_count += 1
        
        # Write output
        output_path = os.path.join(self.output_folder, f"{shop_name}.yml")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(excellent_shop, f, default_flow_style=False,
                         sort_keys=False, allow_unicode=True)
        except (IOError, OSError) as e:
            msg = f"Failed to write output for {shop_name}: {e}"
            logger.error(msg)
            if self.tui:
                self.tui.add_log(msg, "ERROR")
                self.tui.draw_dashboard()
            return
        
        msg = f"✓ {shop_name} ({item_count} items)"
        logger.info(msg)
        if self.tui:
            self.tui.add_log(msg, "SUCCESS")
            self.tui.draw_dashboard()
    
    def _get_or_cache_price_config(self, shop_name: str) -> Tuple[PriceConfig, str]:
        """Get or create cached price configuration"""
        if shop_name not in self.price_cache:
            price_config, scope = get_price_config_interactive(shop_name, self.tui)
            
            if scope == 'all':
                from .constants import SUPPORTED_PLUGINS
                for plugin in SUPPORTED_PLUGINS:
                    self.price_cache[plugin] = price_config
            
            self.price_cache[shop_name] = price_config
        
        return self.price_cache[shop_name], scope if shop_name in self.price_cache else 'this'
    
    def _create_shop_structure(self, shop_name: str, page_count: int, 
                               price_config: PriceConfig) -> Dict[str, Any]:
        """Create the ExcellentShop structure"""
        metadata = SHOP_METADATA.get(shop_name, {})
        
        return {
            'Settings': {
                'Aliases': [],
                'Name': f'<soft_yellow><b>{shop_name}</b></soft_yellow>',
                'Description': [],
                'Icon': {
                    'Material': metadata.get('icon', 'minecraft:chest'),
                    'Lore': []
                },
                'Permission_Required': False,
                'Buying': True,
                'Selling': True,
                'Pages': page_count,
                'MainMenu': {'Slot': metadata.get('slot', 10)},
                'Layout': {
                    'Paginated': False,
                    'ByPage': {str(i): 'default' for i in range(page_count)}
                }
            },
            'Items': {}
        }
    
    @staticmethod
    def _extract_page_number(page_name: str) -> int:
        """Extract page number from page name"""
        digits = ''.join(filter(str.isdigit, page_name))
        return int(digits) if digits else 0
    
    @staticmethod
    def _get_unique_item_key(material: str, slot: str, shop: Dict) -> str:
        """Generate unique key for item"""
        if not material:
            return f"unknown_{slot}"
        
        base_key = material.lower()
        
        if base_key not in shop['Items']:
            return base_key
        
        return f"{base_key}_{slot}"
    
    def _print_console_stats(self):
        """Print stats to console (fallback)"""
        if not self.tui:
            return
            
        total = (self.tui.stats['success'] + self.tui.stats['skipped'] + 
                self.tui.stats['errors'])
        
        print("\n" + "="*50)
        print("CONVERSION COMPLETE")
        print("="*50)
        print(f"Successful: {self.tui.stats['success']}")
        print(f"Skipped: {self.tui.stats['skipped']}")
        print(f"Errors: {self.tui.stats['errors']}")
        print(f"Total: {total}")
        print("="*50)
