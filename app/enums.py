"""Fichier pour déterminer les structures de données"""

from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"

class Item(str, Enum):
    T_SHIRT = "T_SHIRT"
    SWEATS = "SWEATS"
    JACKETS = "JACKETS"
    PANTS = "PANTS"
    SHORTS = "SHORTS"
    UNDERWEAR = "UNDERWEAR"
    ACCESSORIES = "ACCESSORIES"


class Size(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"