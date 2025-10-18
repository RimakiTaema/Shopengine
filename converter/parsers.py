"""Plugin-specific parsers for converting shop formats"""

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
        return bool(item_data)


class ESGUIConverter(SourcePluginConverter):
    """Converter for ESGUI plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        buy_price = item_data.get('buy', 0)
        sell_price = item_data.get('sell', 0)
        
        return ItemConfig(
            material=item_data.get('material'),
            buy_price=float(buy_price) if buy_price is not None else 0.0,
            sell_price=float(sell_price) if sell_price is not None else 0.0,
            enchantments=item_data.get('enchantments'),
        )


class DShop3Converter(SourcePluginConverter):
    """Converter for DShop3 plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        buy_price = item_data.get('price_buy', 0)
        sell_price = item_data.get('price_sell', 0)
        
        return ItemConfig(
            material=item_data.get('id'),
            buy_price=float(buy_price) if buy_price is not None else 0.0,
            sell_price=float(sell_price) if sell_price is not None else 0.0,
            enchantments=item_data.get('enchants'),
        )


class UltimateShopConverter(SourcePluginConverter):
    """Converter for UltimateShop plugin format"""
    
    def convert_item(self, item_data: Dict[str, Any]) -> Optional[ItemConfig]:
        if not self.validate(item_data):
            return None
        
        buy_price = item_data.get('buy', 0)
        sell_price = item_data.get('sell', 0)
        
        return ItemConfig(
            material=item_data.get('item_name'),
            buy_price=float(buy_price) if buy_price is not None else 0.0,
            sell_price=float(sell_price) if sell_price is not None else 0.0,
            enchantments=item_data.get('enchants'),
        )


# Converter registry
SOURCE_PLUGIN_CONVERTERS = {
    'esgui': ESGUIConverter(),
    'dshop3': DShop3Converter(),
    'ultimateshop': UltimateShopConverter(),
}
