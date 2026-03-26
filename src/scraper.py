import time

from fli.models import (
    Airline,
    Airport,
    FlightSearchFilters,
    FlightSegment,
    PassengerInfo,
    TripType,
)
from fli.search.flights import SearchFlights

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def fetch_price(flight_config: dict) -> dict | None:
    """Fetch the round-trip price for a specific Azul flight configuration.

    Calls Google Flights' internal API via fli, filtered to Azul only.
    Matches the exact return flight by flight number(s) and departure time.
    Returns the best matching result or None if unavailable.
    """
    filters = FlightSearchFilters(
        trip_type=TripType.ROUND_TRIP,
        passenger_info=PassengerInfo(adults=1),
        flight_segments=[
            FlightSegment(
                departure_airport=[[Airport.VCP, 0]],
                arrival_airport=[[Airport.MAD, 0]],
                travel_date=flight_config["outbound_date"],
            ),
            FlightSegment(
                departure_airport=[[Airport.MAD, 0]],
                arrival_airport=[[Airport.VCP, 0]],
                travel_date=flight_config["return_date"],
            ),
        ],
        airlines=[Airline.AD],
    )

    last_error = None
    results = None
    for attempt in range(MAX_RETRIES):
        try:
            client = SearchFlights()
            results = client.search(filters, top_n=5)
            if results:
                break
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    if not results:
        if last_error:
            raise last_error
        return None

    target_numbers = _parse_flight_numbers(flight_config["return_flight"])
    target_dep = flight_config["return_departure"]

    for item in results:
        outbound, ret = item if isinstance(item, tuple) else (item, None)
        if ret is None:
            continue

        ret_numbers = [leg.flight_number for leg in ret.legs]
        ret_dep = ret.legs[0].departure_datetime.strftime("%H:%M")

        if ret_numbers == target_numbers and ret_dep == target_dep:
            # fli reports the full round-trip price on each leg, not per-leg
            return {
                "price": ret.price,
                "outbound_flight": outbound.legs[0].flight_number,
                "return_flights": " -> ".join(ret_numbers),
                "return_departure": ret_dep,
            }

    # Exact flight not found in results
    return None


def _parse_flight_numbers(flight_str: str) -> list[str]:
    """Parse 'AD 8001 + AD 4345' into ['8001', '4345']."""
    parts = flight_str.replace("AD ", "").split(" + ")
    return [p.strip() for p in parts]
