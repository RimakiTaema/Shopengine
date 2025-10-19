"""Utility functions for shop conversion"""

from typing import Dict, List, Optional, Any
from .models import ItemConfig, PriceConfig


def convert_material_to_item_id(material: str) -> Optional[str]:
    """Convert material name to Minecraft item ID"""
    if not material:
        return None
    return f"minecraft:{material.lower()}"


def format_enchantments(enchantments: Optional[Dict[str, int]]) -> List[Dict[str, Any]]:
    """Format enchantments for ExcellentShop"""
    if not enchantments:
        return []
    return [
        {'id': f'minecraft:{name.lower()}', 'lvl': int(level)}
        for name, level in enchantments.items()
    ]


def create_excellent_shop_item(
    item_config: ItemConfig,
    currency: str = 'coins',
    price_config: Optional[PriceConfig] = None
) -> Optional[Dict[str, Any]]:
    """Create ExcellentShop item structure"""
    
    if not item_config or not item_config.material:
        return None
    
    # Validate prices
    buy_price = float(item_config.buy_price) if item_config.buy_price is not None else 0.0
    sell_price = float(item_config.sell_price) if item_config.sell_price is not None else 0.0
    
    if buy_price < 0 or sell_price < 0:
        return None
    
    price_format = price_config.format.value if price_config else 'FLAT'
    extra_params = price_config.extra if price_config else {}
    
    item_id = convert_material_to_item_id(item_config.material)
    if not item_id:
        return None
    
    return {
        'Type': 'ITEM',
        'Item': {
            'Provider': 'vanilla',
            'Data': {
                'Value': f'{{count:1,id:"{item_id}"}}',
                'DataVersion': 4189,
                'Enchantments': format_enchantments(item_config.enchantments)
            },
            'CompareNBT': False
        },
        'Rotating': False,
        'Allowed_Ranks': [],
        'Required_Permissions': [],
        'Forbidden_Permissions': [],
        'Currency': currency,
        'Price': {
            'Type': price_format,
            'BUY': buy_price,
            'SELL': sell_price,
            **extra_params
        },
        'Stock': {
            'GLOBAL': {'BuyAmount': -1, 'SellAmount': -1, 'RestockTime': 0},
            'PLAYER': {'BuyAmount': -1, 'SellAmount': -1, 'RestockTime': 0}
        },
        'Shop_View': {'Slot': item_config.slot, 'Page': item_config.page}
    }


def init_folders(base_folder: str = 'shops_to_convert') -> None:
    """Initialize folder structure for shop conversion"""
    import os
    import logging
    from .constants import SUPPORTED_PLUGINS
    
    logger = logging.getLogger(__name__)
    
    try:
        os.makedirs(base_folder, exist_ok=True)
        for plugin in SUPPORTED_PLUGINS:
            plugin_path = os.path.join(base_folder, plugin)
            os.makedirs(plugin_path, exist_ok=True)
            # Create a README file in each plugin folder
            readme_path = os.path.join(plugin_path, 'README.txt')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"Place your {plugin} shop configuration files here.\n")
                    f.write(f"Supported formats: .yml, .yaml\n")
        logger.info(f"Initialized folder structure in '{base_folder}'")
    except (OSError, IOError) as e:
        logger.error(f"Failed to initialize folders: {e}")
        raise
