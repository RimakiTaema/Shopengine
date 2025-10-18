"""
ExcellentShop Converter Package
Converts shop configurations from various Minecraft economy plugins to ExcellentShop format.
"""

from .models import PriceFormat, PriceConfig, ItemConfig
from .engine import ShopConverterEngine
from .ui import ShopConverterTUI
from .parsers import SOURCE_PLUGIN_CONVERTERS
from .constants import SUPPORTED_PLUGINS

__version__ = "2.0.0"
__all__ = [
    'PriceFormat',
    'PriceConfig', 
    'ItemConfig',
    'ShopConverterEngine',
    'ShopConverterTUI',
    'SOURCE_PLUGIN_CONVERTERS',
    'SUPPORTED_PLUGINS'
]
