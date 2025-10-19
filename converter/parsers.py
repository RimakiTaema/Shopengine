"""
Plugin-specific parsers for converting shop formats.

This module provides abstract base classes and concrete implementations for
converting shop configurations between different Minecraft economy plugins.
Supports both forward conversion (to ExcellentShop) and reverse conversion
(from ExcellentShop to other formats).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .models import ItemConfig


class SourcePluginConverter(ABC):
    """Abstract base class for plugin converters"""
    
    @abstractmethod
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        """Convert item from source format to ItemConfig"""
        pass
    
    def validate(self, item_data: Dict[str, Any]) -> bool:
        """Validate item data before conversion"""
        return bool(item_data) and isinstance(item_data, dict)


class ESGUIConverter(SourcePluginConverter):
    """Converter for ESGUI plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        material = item_data.get('material')
        if not material or not isinstance(material, str):
            return None
        
        try:
            buy_price = item_data.get('buy', 0)
            sell_price = item_data.get('sell', 0)
            
            buy_price = float(buy_price) if buy_price is not None else 0.0
            sell_price = float(sell_price) if sell_price is not None else 0.0
            
            # Validate prices
            if buy_price < 0 or sell_price < 0:
                return None
            
            return ItemConfig(
                material=material,
                buy_price=buy_price,
                sell_price=sell_price,
                enchantments=item_data.get('enchantments'),
            )
        except (ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to convert ESGUI item: {e}")
            return None


class DShop3Converter(SourcePluginConverter):
    """Converter for DShop3 plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        material = item_data.get('id')
        if not material or not isinstance(material, str):
            return None
        
        try:
            buy_price = item_data.get('price_buy', 0)
            sell_price = item_data.get('price_sell', 0)
            
            buy_price = float(buy_price) if buy_price is not None else 0.0
            sell_price = float(sell_price) if sell_price is not None else 0.0
            
            # Validate prices
            if buy_price < 0 or sell_price < 0:
                return None
            
            return ItemConfig(
                material=material,
                buy_price=buy_price,
                sell_price=sell_price,
                enchantments=item_data.get('enchants'),
            )
        except (ValueError, TypeError):
            return None


class UltimateShopConverter(SourcePluginConverter):
    """Converter for UltimateShop plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        material = item_data.get('item_name')
        if not material or not isinstance(material, str):
            return None
        
        try:
            buy_price = item_data.get('buy', 0)
            sell_price = item_data.get('sell', 0)
            
            buy_price = float(buy_price) if buy_price is not None else 0.0
            sell_price = float(sell_price) if sell_price is not None else 0.0
            
            # Validate prices
            if buy_price < 0 or sell_price < 0:
                return None
            
            return ItemConfig(
                material=material,
                buy_price=buy_price,
                sell_price=sell_price,
                enchantments=item_data.get('enchants'),
            )
        except (ValueError, TypeError):
            return None


# Converter registry
SOURCE_PLUGIN_CONVERTERS = {
    'esgui': ESGUIConverter(),
    'dshop3': DShop3Converter(),
    'ultimateshop': UltimateShopConverter(),
}

# Reverse converter registry (from ExcellentShop to other formats)
REVERSE_CONVERTERS = {
    'esgui': 'convert_to_esgui',
    'dshop3': 'convert_to_dshop3', 
    'ultimateshop': 'convert_to_ultimateshop',
}
