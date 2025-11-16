"""
shared/contract_types.py

Опис типів контрактів, їхніх налаштувань (capacity, іконка, короткий опис).
Цей модуль спільний — імпортується backend, bot і client.
"""

from typing import TypedDict, Dict, Any

class ContractTypeConfig(TypedDict, total=False):
    """Конфіг для типу контракту."""
    id: str
    display_name: str
    description: str
    default_capacity: int
    icon: str  # шлях/ім'я іконки у client/assets/icons
    color_hex: str  # кольори можна використовувати для embed/UI

# Перелік доступних типів контрактів з дефолтними налаштуваннями.
# Ключі повинні бути унікальні і використовуватись як type_contract у БД.
CONTRACT_TYPES: Dict[str, ContractTypeConfig] = {
    "medical": {
        "id": "medical",
        "display_name": "Медичний вантаж",
        "description": "Доставити медичні припаси до точки здачі.",
        "default_capacity": 5,
        "icon": "medical.png",
        "color_hex": "#E74C3C",
    },
    "ammunition": {
        "id": "ammunition",
        "display_name": "Боєприпаси",
        "description": "Перевезти боєприпаси для бойової одиниці.",
        "default_capacity": 5,
        "icon": "ammo.png",
        "color_hex": "#F39C12",
    },
    "food": {
        "id": "food",
        "display_name": "Продовольство",
        "description": "Доставка продовольства.",
        "default_capacity": 6,
        "icon": "food.png",
        "color_hex": "#27AE60",
    },
    "rare_supply": {
        "id": "rare_supply",
        "display_name": "Рарний вантаж",
        "description": "Особливий вантаж — обмежена кількість місць.",
        "default_capacity": 3,
        "icon": "rare.png",
        "color_hex": "#8E44AD",
    },
    # "default" тип для невідомих записів
    "default": {
        "id": "default",
        "display_name": "Стандартний контракт",
        "description": "Стандартний контракт.",
        "default_capacity": 5,
        "icon": "default.png",
        "color_hex": "#3498DB",
    },
}

def get_type_config(type_key: str) -> ContractTypeConfig:
    """
    Повертає конфіг для заданого type_contract.
    Якщо тип не знайдено — повертає конфіг для 'default'.
    """
    return CONTRACT_TYPES.get(type_key, CONTRACT_TYPES["default"])
