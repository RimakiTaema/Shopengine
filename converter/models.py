"""
Data models for shop converter.

This module defines the core data structures used throughout the shop conversion
process, including price configurations, item configurations, and price format
enumerations.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class PriceFormat(Enum):
    """Price format types for ExcellentShop"""
    FLAT = 'FLAT'
    FLOAT = 'FLOAT'
    FLOAT_INTERVAL = 'FLOAT_INTERVAL'
    FLOAT_FIXED = 'FLOAT_FIXED'
    DYNAMIC = 'DYNAMIC'


@dataclass
class PriceConfig:
    """Price configuration for shop items"""
    format: PriceFormat
    buy_price: float
    sell_price: float
    extra: Dict[str, Any]
    
    def __post_init__(self):
        """Validate price configuration after initialization"""
        if self.buy_price < 0 or self.sell_price < 0:
            raise ValueError("Prices must be non-negative")


@dataclass
class ItemConfig:
    """Item configuration from source plugin"""
    material: str
    buy_price: float
    sell_price: float
    enchantments: Optional[Dict[str, int]] = None
    slot: int = 0
    page: int = 0
