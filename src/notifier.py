import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(message: str) -> None:
    """Send a message via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[telegram disabled] {message}")
        return

    url = TELEGRAM_API.format(token=TELEGRAM_BOT_TOKEN)
    resp = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        },
        timeout=10,
    )
    resp.raise_for_status()


def format_price_alert(
    flight_label: str,
    price: float,
    previous_price: float | None,
    price_min: float,
    price_max: float,
) -> str:
    """Format a price notification message."""
    if price <= price_max:
        header = "DENTRO DO ALVO"
    elif previous_price and price < previous_price:
        header = "Preco caiu"
    elif previous_price and price > previous_price:
        header = "Preco subiu"
    else:
        header = "Atualizacao de preco"

    lines = [
        f"*{header}*",
        f"Voo: {flight_label}",
        f"Preco: R$ {price:,.0f}",
        f"Alvo: R$ {price_min:,.0f} - R$ {price_max:,.0f}",
    ]

    if previous_price:
        diff = price - previous_price
        direction = "+" if diff > 0 else ""
        lines.append(f"Anterior: R$ {previous_price:,.0f} ({direction}{diff:,.0f})")

    return "\n".join(lines)


def format_error(errors: list[str]) -> str:
    """Format an error notification."""
    return "*Erro no monitoramento*\n" + "\n".join(f"- {e}" for e in errors)
