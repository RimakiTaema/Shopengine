"""ExcellentShop parser for converting back to other plugin formats"""

import re
from typing import Dict, Any, Optional, Tuple, List
from .models import ItemConfig, PriceConfig, PriceFormat


class ExcellentShopParser:
    """Parser for ExcellentShop configuration files"""
    
    def __init__(self):
        self.price_cache = {}
    
    def parse_shop_file(self, file_path: str) -> Dict[str, Any]:
        """Parse an ExcellentShop YAML file and extract shop data"""
        import yaml
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            return self._extract_shop_data(data)
        except Exception as e:
            raise ValueError(f"Failed to parse ExcellentShop file {file_path}: {e}")
    
    def _extract_shop_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract shop data from ExcellentShop structure"""
        settings = data.get('Settings', {})
        items = data.get('Items', {})
        
        shop_data = {
            'name': self._extract_shop_name(settings),
            'pages': self._extract_page_count(settings),
            'items': []
        }
        
        # Process items
        for item_key, item_data in items.items():
            item_config = self._parse_item(item_data, item_key)
            if item_config:
                shop_data['items'].append(item_config)
        
        return shop_data
    
    def _extract_shop_name(self, settings: Dict[str, Any]) -> str:
        """Extract clean shop name from settings"""
        name = settings.get('Name', 'Unknown')
        # Remove color codes and formatting
        clean_name = re.sub(r'<[^>]+>', '', name)
        return clean_name.strip()
    
    def _extract_page_count(self, settings: Dict[str, Any]) -> int:
        """Extract page count from settings"""
        return settings.get('Pages', 1)
    
    def _parse_item(self, item_data: Dict[str, Any], item_key: str) -> Optional[ItemConfig]:
        """Parse individual item from ExcellentShop format"""
        try:
            # Extract material from item data
            material = self._extract_material(item_data)
            if not material:
                return None
            
            # Extract prices
            buy_price, sell_price = self._extract_prices(item_data)
            
            # Extract slot and page
            shop_view = item_data.get('Shop_View', {})
            slot = shop_view.get('Slot', 0)
            page = shop_view.get('Page', 0)
            
            # Extract enchantments
            enchantments = self._extract_enchantments(item_data)
            
            return ItemConfig(
                material=material,
                buy_price=buy_price,
                sell_price=sell_price,
                slot=slot,
                page=page,
                enchantments=enchantments
            )
        except Exception:
            return None
    
    def _extract_material(self, item_data: Dict[str, Any]) -> Optional[str]:
        """Extract material name from item data"""
        try:
            item_info = item_data.get('Item', {})
            data_info = item_info.get('Data', {})
            value = data_info.get('Value', '')
            
            # Parse the Value string to extract item ID
            # Format: {count:1,id:"minecraft:item_name"}
            id_match = re.search(r'id:"minecraft:([^"]+)"', value)
            if id_match:
                return id_match.group(1)
            
            # Fallback: try to extract from components
            components_match = re.search(r'"minecraft:([^"]+)"', value)
            if components_match:
                return components_match.group(1)
            
            return None
        except Exception:
            return None
    
    def _extract_prices(self, item_data: Dict[str, Any]) -> Tuple[float, float]:
        """Extract buy and sell prices from item data"""
        price_data = item_data.get('Price', {})
        price_type = price_data.get('Type', 'FLAT')
        
        if price_type == 'FLAT':
            return self._extract_flat_prices(price_data)
        elif price_type == 'FLOAT':
            return self._extract_float_prices(price_data)
        elif price_type == 'DYNAMIC':
            return self._extract_dynamic_prices(price_data)
        elif price_type == 'PLAYER_AMOUNT':
            return self._extract_player_amount_prices(price_data)
        else:
            # Default fallback
            return 0.0, 0.0
    
    def _extract_flat_prices(self, price_data: Dict[str, Any]) -> Tuple[float, float]:
        """Extract prices from FLAT pricing"""
        buy_price = price_data.get('BUY', 0.0)
        sell_price = price_data.get('SELL', 0.0)
        
        if isinstance(buy_price, (int, float)):
            buy_price = float(buy_price)
        else:
            buy_price = 0.0
            
        if isinstance(sell_price, (int, float)):
            sell_price = float(sell_price)
        else:
            sell_price = 0.0
        
        return buy_price, sell_price
    
    def _extract_float_prices(self, price_data: Dict[str, Any]) -> Tuple[float, float]:
        """Extract prices from FLOAT pricing (use average of min/max)"""
        buy_data = price_data.get('BUY', {})
        sell_data = price_data.get('SELL', {})
        
        # Calculate average price for FLOAT pricing
        buy_min = buy_data.get('Min', 0.0) if isinstance(buy_data, dict) else 0.0
        buy_max = buy_data.get('Max', 0.0) if isinstance(buy_data, dict) else 0.0
        buy_price = (buy_min + buy_max) / 2.0 if buy_min > 0 or buy_max > 0 else 0.0
        
        sell_min = sell_data.get('Min', 0.0) if isinstance(sell_data, dict) else 0.0
        sell_max = sell_data.get('Max', 0.0) if isinstance(sell_data, dict) else 0.0
        sell_price = (sell_min + sell_max) / 2.0 if sell_min > 0 or sell_max > 0 else 0.0
        
        return buy_price, sell_price
    
    def _extract_dynamic_prices(self, price_data: Dict[str, Any]) -> Tuple[float, float]:
        """Extract prices from DYNAMIC pricing (use start values)"""
        buy_data = price_data.get('BUY', {})
        sell_data = price_data.get('SELL', {})
        
        buy_price = buy_data.get('StartValue', 0.0) if isinstance(buy_data, dict) else 0.0
        sell_price = sell_data.get('StartValue', 0.0) if isinstance(sell_data, dict) else 0.0
        
        return buy_price, sell_price
    
    def _extract_player_amount_prices(self, price_data: Dict[str, Any]) -> Tuple[float, float]:
        """Extract prices from PLAYER_AMOUNT pricing (use start values)"""
        buy_data = price_data.get('BUY', {})
        sell_data = price_data.get('SELL', {})
        
        buy_price = buy_data.get('StartValue', 0.0) if isinstance(buy_data, dict) else 0.0
        sell_price = sell_data.get('StartValue', 0.0) if isinstance(sell_data, dict) else 0.0
        
        return buy_price, sell_price
    
    def _extract_enchantments(self, item_data: Dict[str, Any]) -> Optional[Dict[str, int]]:
        """Extract enchantments from item data"""
        try:
            item_info = item_data.get('Item', {})
            data_info = item_info.get('Data', {})
            enchantments = data_info.get('Enchantments', [])
            
            if not enchantments or not isinstance(enchantments, list):
                return None
            
            result = {}
            for enchant in enchantments:
                if isinstance(enchant, dict):
                    enchant_id = enchant.get('id', '')
                    level = enchant.get('lvl', 1)
                    
                    # Convert minecraft:enchantment_name to enchantment_name
                    if enchant_id.startswith('minecraft:'):
                        enchant_name = enchant_id[10:]  # Remove 'minecraft:' prefix
                        result[enchant_name] = int(level)
            
            return result if result else None
        except Exception:
            return None


class ReverseConverter:
    """Converts ExcellentShop data back to other plugin formats"""
    
    def __init__(self):
        self.parser = ExcellentShopParser()
    
    def convert_to_esgui(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert shop data to ESGUI format"""
        esgui_data = {
            'pages': {}
        }
        
        # Group items by page
        pages = {}
        for item in shop_data.get('items', []):
            page_num = item.page
            if page_num not in pages:
                pages[page_num] = {'items': {}}
            
            # Convert to ESGUI format
            esgui_item = {
                'material': item.material,
                'buy': item.buy_price,
                'sell': item.sell_price
            }
            
            if item.enchantments:
                esgui_item['enchantments'] = item.enchantments
            
            # Use slot + 1 for ESGUI (1-indexed)
            pages[page_num]['items'][str(item.slot + 1)] = esgui_item
        
        # Convert pages to ESGUI format
        for page_num, page_data in pages.items():
            page_name = f"page{page_num + 1}" if page_num > 0 else "page1"
            esgui_data['pages'][page_name] = page_data
        
        return esgui_data
    
    def convert_to_dshop3(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert shop data to DShop3 format"""
        dshop3_data = {
            'pages': {}
        }
        
        # Group items by page
        pages = {}
        for item in shop_data.get('items', []):
            page_num = item.page
            if page_num not in pages:
                pages[page_num] = {'items': {}}
            
            # Convert to DShop3 format
            dshop3_item = {
                'id': item.material,
                'price_buy': item.buy_price,
                'price_sell': item.sell_price
            }
            
            if item.enchantments:
                dshop3_item['enchants'] = item.enchantments
            
            # Use slot + 1 for DShop3 (1-indexed)
            pages[page_num]['items'][str(item.slot + 1)] = dshop3_item
        
        # Convert pages to DShop3 format
        for page_num, page_data in pages.items():
            page_name = f"page{page_num + 1}" if page_num > 0 else "page1"
            dshop3_data['pages'][page_name] = page_data
        
        return dshop3_data
    
    def convert_to_ultimateshop(self, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert shop data to UltimateShop format"""
        ultimateshop_data = {
            'pages': {}
        }
        
        # Group items by page
        pages = {}
        for item in shop_data.get('items', []):
            page_num = item.page
            if page_num not in pages:
                pages[page_num] = {'items': {}}
            
            # Convert to UltimateShop format
            ultimateshop_item = {
                'item_name': item.material,
                'buy': item.buy_price,
                'sell': item.sell_price
            }
            
            if item.enchantments:
                ultimateshop_item['enchants'] = item.enchantments
            
            # Use slot + 1 for UltimateShop (1-indexed)
            pages[page_num]['items'][str(item.slot + 1)] = ultimateshop_item
        
        # Convert pages to UltimateShop format
        for page_num, page_data in pages.items():
            page_name = f"page{page_num + 1}" if page_num > 0 else "page1"
            ultimateshop_data['pages'][page_name] = page_data
        
        return ultimateshop_data