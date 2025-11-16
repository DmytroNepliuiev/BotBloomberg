"""
shared/constants.py

Загальні константи, які використовуються у всіх модулях проєкту.
"""

from typing import Final, List

# Статуси контракту (використовуються в БД і у відповілях API)
STATUS_CLOSED: Final[str] = "closed"
STATUS_OPEN: Final[str] = "open"
STATUS_IN_PROGRESS: Final[str] = "in_progress"
STATUS_COMPLETED: Final[str] = "completed"

ALL_STATUSES: Final[List[str]] = [
    STATUS_CLOSED,
    STATUS_OPEN,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
]

# Поля у JSONB об'єктах participants/reservations
PARTICIPANT_DISCORD_ID_FIELD: Final[str] = "discord_id"
PARTICIPANT_NICKNAME_FIELD: Final[str] = "nickname"

# Імена заголовків/ключів для internal-auth (якщо використовується)
INTERNAL_AUTH_HEADER: Final[str] = "Authorization"
INTERNAL_AUTH_PREFIX: Final[str] = "Bearer "

# Формати часу/дата (для UI або логів)
ISO_DATETIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S%z"

# Налаштування WebSocket повідомлень (типи подій)
WS_EVENT_CONTRACT_UPDATED: Final[str] = "contract_updated"
WS_EVENT_CONTRACT_CREATED: Final[str] = "contract_created"
WS_EVENT_CONTRACT_CLOSED: Final[str] = "contract_closed"
WS_EVENT_PING: Final[str] = "ping"

# Полиці/namespace для логів або redis (якщо згодом додамо)
REDIS_NAMESPACE_PREFIX: Final[str] = "bot_contracts:"

# Назви таблиць (тільки для зручності)
TABLE_CONTRACTS: Final[str] = "contracts"

# Дефолтні значення для бекенду/бота
DEFAULT_MAX_PARTICIPANTS: Final[int] = 5

# Корисна утиліта для перевірки статусів
def is_valid_status(status: str) -> bool:
    return status in ALL_STATUSES
