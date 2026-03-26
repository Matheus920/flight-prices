import csv
import time
from datetime import datetime, timezone

from config import (
    FLIGHTS,
    HISTORY_FILE,
    PRICE_CHANGE_THRESHOLD,
    PRICE_MAX,
    PRICE_MIN,
)
from notifier import format_error, format_price_alert, send_telegram
from scraper import fetch_price

NA = "N/A"


def get_last_entry(flight_id: str) -> str | None:
    """Read the last recorded price (or 'N/A') for a flight from the CSV."""
    if not HISTORY_FILE.exists():
        return None
    with open(HISTORY_FILE, newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["flight_id"] == flight_id]
    if rows:
        return rows[-1]["price_brl"]
    return None


def append_entry(flight_id: str, value: str) -> None:
    """Append a price observation (or 'N/A') to the CSV history file."""
    exists = HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "flight_id", "price_brl"])
        writer.writerow([
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            flight_id,
            value,
        ])


def should_notify(price: float, previous_entry: str | None) -> bool:
    """Decide whether to send a notification for this price."""
    if price <= PRICE_MAX:
        return True
    if previous_entry is None or previous_entry == NA:
        # First time seeing a price, or flight just became available again
        return True
    previous = float(previous_entry)
    if abs(price - previous) >= PRICE_CHANGE_THRESHOLD:
        return True
    return False


def main() -> None:
    results: list[tuple[dict, float | None]] = []
    errors: list[str] = []

    for flight in FLIGHTS:
        try:
            match = fetch_price(flight)

            if match is None:
                append_entry(flight["id"], NA)
                results.append((flight, None))
                time.sleep(5)
                continue

            price = match["price"]
            results.append((flight, price))

            previous = get_last_entry(flight["id"])
            append_entry(flight["id"], f"{price:.0f}")

            if should_notify(price, previous):
                msg = format_price_alert(
                    flight["label"], price,
                    float(previous) if previous and previous != NA else None,
                    PRICE_MIN, PRICE_MAX,
                )
                send_telegram(msg)

            time.sleep(5)

        except Exception as e:
            msg = str(e)
            if len(msg) > 200:
                msg = msg[:200] + "..."
            errors.append(f"{flight['label']}: {msg}")

    if errors:
        try:
            send_telegram(format_error(errors))
        except Exception as e:
            print(f"Failed to send error notification: {e}")

    print("=== Price Check Summary ===")
    for flight, price in results:
        if price is None:
            print(f"  {flight['id']}: Preco indisponivel")
        else:
            tag = " << ALVO" if PRICE_MIN <= price <= PRICE_MAX else ""
            print(f"  {flight['id']}: R$ {price:,.0f}{tag}")
    for err in errors:
        print(f"  ERROR: {err}")
    if not results and not errors:
        print("  No data collected")


if __name__ == "__main__":
    main()
