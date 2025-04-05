import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetchMETAR(icao):
    """
    Retrieves METAR data from aviationweather.gov API.

    Args:
        icao: The ICAO airport code (e.g., "KJFK").

    Returns:
        The METAR data as a string, or None if an error occurs.
    """
    url = f"https://aviationweather.gov/api/data/metar?ids={icao}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        logging.info(f"Successfully fetched METAR for {icao}")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching METAR: {e}")
        return None