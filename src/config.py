import os
from pathlib import Path

# Flight definitions: 3 roundtrip options sharing the same outbound
FLIGHTS = [
    {
        "id": "sep13",
        "label": "VCP\u2192MAD 2/set \u2013 MAD\u2192VCP 13/set (AD 8755)",
        "outbound_date": "2026-09-02",
        "return_date": "2026-09-13",
        "from_airport": "VCP",
        "to_airport": "MAD",
        "outbound_flight": "AD 8754",
        "outbound_departure": "20:15",
        "return_flight": "AD 8755",
        "return_departure": "13:30",
    },
    {
        "id": "sep14",
        "label": "VCP\u2192MAD 2/set \u2013 MAD\u2192VCP 14/set (AD 8001+4345)",
        "outbound_date": "2026-09-02",
        "return_date": "2026-09-14",
        "from_airport": "VCP",
        "to_airport": "MAD",
        "outbound_flight": "AD 8754",
        "outbound_departure": "20:15",
        "return_flight": "AD 8001 + AD 4345",
        "return_departure": "10:55",
    },
    {
        "id": "sep15",
        "label": "VCP\u2192MAD 2/set \u2013 MAD\u2192VCP 15/set (AD 8755)",
        "outbound_date": "2026-09-02",
        "return_date": "2026-09-15",
        "from_airport": "VCP",
        "to_airport": "MAD",
        "outbound_flight": "AD 8754",
        "outbound_departure": "20:15",
        "return_flight": "AD 8755",
        "return_departure": "13:30",
    },
]

# Price thresholds (BRL)
PRICE_MIN = 6000
PRICE_MAX = 7000

# Notify on significant price changes (BRL)
PRICE_CHANGE_THRESHOLD = 500

# Project root (two levels up from src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_ROOT / "price_history.csv"

# Telegram (from environment)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
