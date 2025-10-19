"""Utility functions for shop conversion"""

from typing import Dict, List, Optional, Any
from .models import ItemConfig, PriceConfig


def convert_material_to_item_id(material: str) -> Optional[str]:
    """Convert material name to Minecraft item ID"""
    if not material or not isinstance(material, str):
        return None
    
    # Clean the material name
    clean_material = material.strip().lower()
    
    # If it already has minecraft: prefix, return as is
    if clean_material.startswith('minecraft:'):
        return clean_material
    
    return f"minecraft:{clean_material}"


def format_enchantments(enchantments: Optional[Dict[str, int]]) -> List[Dict[str, Any]]:
    """Format enchantments for ExcellentShop"""
    if not enchantments or not isinstance(enchantments, dict):
        return []
    
    result = []
    for name, level in enchantments.items():
        if not isinstance(name, str) or not isinstance(level, (int, float)):
            continue
        
        try:
            clean_name = name.strip().lower()
            if not clean_name:
                continue
                
            # If it already has minecraft: prefix, use as is
            if clean_name.startswith('minecraft:'):
                enchant_id = clean_name
            else:
                enchant_id = f'minecraft:{clean_name}'
            
            result.append({
                'id': enchant_id,
                'lvl': int(level)
            })
        except (ValueError, TypeError):
            continue
    
    return result


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
        'Price': _create_price_structure(price_format, buy_price, sell_price, extra_params),
        'Stock': {
            'GLOBAL': {'BuyAmount': -1, 'SellAmount': -1, 'RestockTime': 0},
            'PLAYER': {'BuyAmount': -1, 'SellAmount': -1, 'RestockTime': 0}
        },
        'Shop_View': {'Slot': item_config.slot, 'Page': item_config.page}
    }


def _create_price_structure(price_format: str, buy_price: float, sell_price: float, extra_params: Dict[str, Any]) -> Dict[str, Any]:
    """Create price structure based on format"""
    if price_format == 'FLAT':
        return {
            'Type': 'FLAT',
            'BUY': buy_price,
            'SELL': sell_price
        }
    elif price_format == 'FLOAT':
        return {
            'Type': 'FLOAT',
            'BUY': {
                'Min': extra_params.get('MIN', buy_price),
                'Max': extra_params.get('MAX', buy_price)
            },
            'SELL': {
                'Min': extra_params.get('MIN', sell_price),
                'Max': extra_params.get('MAX', sell_price)
            },
            'Refresh': {
                'Type': 'INTERVAL',
                'Interval': extra_params.get('TIMER', 60),
                'Days': 'THURSDAY,WEDNESDAY,SUNDAY,FRIDAY,MONDAY,TUESDAY,SATURDAY',
                'Times': []
            },
            'Round_Decimals': False
        }
    elif price_format == 'FLOAT_INTERVAL':
        return {
            'Type': 'FLOAT',
            'BUY': {
                'Min': extra_params.get('MIN', buy_price),
                'Max': extra_params.get('MAX', buy_price)
            },
            'SELL': {
                'Min': extra_params.get('MIN', sell_price),
                'Max': extra_params.get('MAX', sell_price)
            },
            'Refresh': {
                'Type': 'INTERVAL',
                'Interval': extra_params.get('TIMER', 60),
                'Days': 'THURSDAY,WEDNESDAY,SUNDAY,FRIDAY,MONDAY,TUESDAY,SATURDAY',
                'Times': []
            },
            'Round_Decimals': extra_params.get('Round_Decimals', False)
        }
    elif price_format == 'FLOAT_FIXED':
        # Parse day configuration
        day_config = extra_params.get('Day_Config', 'all')
        if day_config.lower() == 'all':
            days = 'THURSDAY,WEDNESDAY,SUNDAY,FRIDAY,MONDAY,TUESDAY,SATURDAY'
        else:
            days = day_config.upper()
        
        return {
            'Type': 'FLOAT',
            'BUY': {
                'Min': extra_params.get('MIN', buy_price),
                'Max': extra_params.get('MAX', buy_price)
            },
            'SELL': {
                'Min': extra_params.get('MIN', sell_price),
                'Max': extra_params.get('MAX', sell_price)
            },
            'Refresh': {
                'Type': 'FIXED',
                'Days': days,
                'Times': [
                    extra_params.get('Start_Time', '00:00'),
                    extra_params.get('End_Time', '23:59')
                ]
            },
            'Round_Decimals': extra_params.get('Round_Decimals', False)
        }
    elif price_format == 'DYNAMIC':
        return {
            'Type': 'DYNAMIC',
            'BUY': {
                'StartValue': extra_params.get('INITIAL', buy_price),
                'BuyOffset': extra_params.get('STEP', 0.0),
                'SellOffset': 0.0,
                'MinOffset': extra_params.get('MIN', 0.0),
                'MaxOffset': extra_params.get('MAX', 0.0)
            },
            'SELL': {
                'StartValue': extra_params.get('INITIAL', sell_price),
                'BuyOffset': extra_params.get('STEP', 0.0),
                'SellOffset': 0.0,
                'MinOffset': extra_params.get('MIN', 0.0),
                'MaxOffset': extra_params.get('MAX', 0.0)
            },
            'Stabilization': {
                'Interval': 0,
                'Amount': 0.0
            }
        }
    else:
        # Default to FLAT
        return {
            'Type': 'FLAT',
            'BUY': buy_price,
            'SELL': sell_price
        }


def validate_price_input(value: str, default: float, min_val: float = 0.0) -> float:
    """Validate and convert price input to float"""
    try:
        result = float(value) if value else default
        if result < min_val:
            return min_val
        return result
    except (ValueError, TypeError):
        return default


def validate_positive_int(value: str, default: int, min_val: int = 1) -> int:
    """Validate and convert positive integer input"""
    try:
        result = int(value) if value else default
        if result < min_val:
            return min_val
        return result
    except (ValueError, TypeError):
        return default


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
