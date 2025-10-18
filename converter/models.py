"""Data models for shop converter"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class PriceFormat(Enum):
    """Price format types for ExcellentShop"""
    FLAT = 'FLAT'
    FLOAT = 'FLOAT'
    DYNAMIC = 'DYNAMIC'


@dataclass
class PriceConfig:
    """Price configuration for shop items"""
    format: PriceFormat
    buy_price: float
    sell_price: float
    extra: Dict[str, Any]


@dataclass
class ItemConfig:
    """Item configuration from source plugin"""
    material: str
    buy_price: float
    sell_price: float
    enchantments: Optional[Dict[str, int]] = None
    slot: int = 0
    page: int = 0
