import re
from datetime import datetime, timedelta, timezone

def parseMETAR(metar):
    """
    Parses a METAR string into a human-readable dictionary.

    Args:
        metar: The METAR string.

    Returns:
        A dictionary containing parsed METAR data, or None if parsing fails.
    """

    metar = metar.upper().strip()  # Standardize input
    parts = metar.split()

    parsed_data = {}
    nextIdx = 0

    try:
        # Station Identifier
        parsed_data["station"] = parts[nextIdx]
        nextIdx += 1

        # Date and Time
        parsed_data["time"] = parseTime(parts[nextIdx])
        nextIdx += 1

        # update information are optional
        if re.match(r"^(AUTO|COR)$", parts[nextIdx].upper()):
            parsed_data["update"] = parts[nextIdx]
            nextIdx += 1

        # wind
        parsed_data["wind"] = parseWind(parts[nextIdx])
        nextIdx += 1

        # optional wind variation
        if re.match(r"(\d{3})V(\d{3})", parts[nextIdx]):
            parsed_data["wind_variation"] = parseWindVariation(parts[nextIdx])
            nextIdx += 1

        # Visibility
        parsed_data["visibility"] = parseVisibility(parts[nextIdx])
        nextIdx += 1

        # optional Runway Visual Range (RVR) - more complex and optional, needs further refinement
        rvrs = []
        while (parts[nextIdx].startswith("R")):
            rvrs.append(parseRVR(parts[nextIdx]))
            nextIdx += 1
        parsed_data["rvr"] = rvrs

        # optional present weather
        parsed_data["weather"] = parseWeatherCodes(parts[nextIdx])
        if (parsed_data["weather"] != ""):
            nextIdx += 1

        # optional Cloud Cover
        clouds = []
        while (re.match(r"(SKC|CLR|FEW|SCT|BKN|OVC)(\d{3})?", parts[nextIdx])):
            clouds.append(parseClouds(parts[nextIdx]))
            nextIdx += 1
        parsed_data["clouds"] = clouds

        # Temperature and Dew Point
        parsed_data["temperatures"] = parseTemperatures(parts[nextIdx])
        nextIdx += 1

        # QNH
        parsed_data["QNH"] = parseQNH(parts[nextIdx])
        nextIdx += 1
       
        return parsed_data
    except Exception as e:
        print(f"Error parsing METAR {metar}: {e}")
        return None

def parseTemperatures(metar):
    """
    Parses temperature and dew point from a METAR temperature string.

    Args:
        metar: The temperature string (e.g., "12/11", "M02/M05", "00/M01").

    Returns:
        A tuple containing temperature and dew point as floats, or None if parsing fails.
    """
    try:
        temp_dew = metar.split("/")
        if len(temp_dew) != 2:
            return None  # Invalid format

        temperature_str = temp_dew[0]
        dew_point_str = temp_dew[1]

        temperature = convertTemp(temperature_str)
        dew_point = convertTemp(dew_point_str)

        return {"temperature": temperature, "dew_point": dew_point}

    except (ValueError, AttributeError):
        return None  # Parsing error

def convertTemp(temperature_str):
    """
    Converts a temperature string to a float value.

    Args:
        temperature_str: The temperature string (e.g., "12", "M02").

    Returns:
        The temperature as a int.
    """
    if temperature_str.startswith("M"):
        return -int(temperature_str[1:])
    else:
        return int(temperature_str)

def parseClouds(metar):
    """
    Parses a single cloud ceiling code from a METAR.

    Args:
        metar: The cloud ceiling code (e.g., "OVC008").

    Returns:
        A descriptive string of the cloud ceiling.
    """

    cloud_types = {
        "CLR": "clear",
        "SKC": "sky clear",
        "FEW": "few clouds at",
        "SCT": "scattered clouds at",
        "BKN": "broken clouds at",
        "OVC": "overcast at",
        "VV": "vertical visibility",
    }

    if metar[:2] == "VV":
        height = int(metar[2:]) * 100
        return f"vertical visibility {height}ft"
    
    if (metar[:3] == "CLR"):
        return f"clear of clouds below 12000ft"

    if metar[:3] in cloud_types:
        cloud_type = cloud_types[metar[:3]]
        height = int(metar[3:]) * 100
        return f"{cloud_type} {height}ft"

    return "unknown cloud condition"

def parseWeatherCodes(metar):
    """
    Parses weather codes from a METAR and returns a descriptive string.

    Args:
        metar: The weather code string (e.g., "-RABR").

    Returns:
        A descriptive string of the weather conditions.
    """

    weather_map = {
        "-": "light ",
        "+": "heavy ",
        "VC": "vicinity ",
        "MI": "shallow ",
        "BC": "patches of ",
        "DR": "low drifting ",
        "BL": "blowing ",
        "SH": "showers ",
        "TS": "thunderstorm ",
        "FZ": "freezing ",
        "DZ": "drizzle",
        "RA": "rain",
        "SN": "snow",
        "SG": "snow grains",
        "IC": "ice crystals",
        "PL": "ice pellets",
        "GR": "hail",
        "GS": "small hail/snow pellets",
        "UP": "unknown precipitation",
        "BR": "mist",
        "FG": "fog",
        "FU": "smoke",
        "VA": "volcanic ash",
        "DU": "widespread dust",
        "SA": "sand",
        "HZ": "haze",
        "PO": "dust/sand whirls",
        "SQ": "squalls",
        "FC": "funnel cloud/tornado/waterspout",
        "SS": "sandstorm",
        "DS": "duststorm",
    }

    description = ""
    i = 0
    while i < len(metar):
        if metar[i:i + 2] in weather_map:
            description += weather_map[metar[i:i + 2]]
            i += 2
        elif metar[i] in weather_map:
            description += weather_map[metar[i]]
            i += 1
        else:
            i += 1 #handle unexpected characters, just in case.

    return description.strip()

def parseRVR(metar):
    """
    Parses a single RVR string into a dictionary and converts distances to meters.

    Args:
        metar: The RVR string (e.g., "R04R/2600FT/D", "R28R/2000V3000FT").

    Returns:
        A dictionary containing RVR data with distances in meters, or None if parsing fails.
    """
    metar = metar.upper()

    rvr_match = re.match(r"R(\d{2}[LCR]?)/P?(\d{4})V?P?(\d{4})?(FT|M)?(/U|/D|/N)?", metar)

    if not rvr_match:
        return None

    runway = rvr_match.group(1)
    min_range = int(rvr_match.group(2))
    max_range = int(rvr_match.group(3)) if rvr_match.group(3) else min_range
    unit = rvr_match.group(4) if rvr_match.group(4) else "FT"
    trend = rvr_match.group(5)

    if unit == "FT":
        min_range = round(min_range * 0.3048)  # Convert feet to meters
        max_range = round(max_range * 0.3048)
        unit = "M" #set unit to M

    rvr_dict = {
        "runway": runway,
        "min_range": min_range,
        "max_range": max_range,
        "unit": unit,
        "trend": trend[1] if trend else None, #remove leading slash
    }

    return rvr_dict

def parseVisibility(metar):
    """
    Normalizes visibility to meters.

    Args:
        visibilimetarty_str: The visibility string (e.g., "10SM", "9999", "1600", "1/2SM").

    Returns:
        The visibility in meters as an integer, or None if parsing fails.
    """
    metar = metar.upper()

    if metar == "9999" or metar == "CAVOK":
        return 10000  # 10km+ is considered 10000 meters
    elif re.match(r"^\d{4}$", metar):
        return int(metar)  # Already in meters
    elif re.match(r"^\d+SM$", metar):
        sm_value = int(re.match(r"^\d+SM$", metar).group(0)[:-2]) #remove SM, and convert to int
        return round(sm_value * 1609.34)  # Convert statute miles to meters
    elif re.match(r"^\d+\/\d+SM$", metar):
        numerator, denominator = map(int, re.match(r"(\d+)/(\d+)SM$", metar).groups())
        sm_value = numerator / denominator
        return round(sm_value * 1609.34)  # Convert statute miles to meters
    else:
        return None
    
def parseWindVariation(metar):
    """
    Parses wind variation data from a METAR string.

    Args:
        metar: The wind variation part of the METAR string (e.g., "200V280").

    Returns:
        A dictionary containing the minimum and maximum wind directions,
        or None if parsing fails.
    """
    metar = metar.upper()

    variation_match = re.match(r"(\d{3})V(\d{3})", metar)
    if variation_match:
        variation_data = {
            "min_direction": int(variation_match.group(1)),
            "max_direction": int(variation_match.group(2)),
        }
        return variation_data
    else:
        return None

def parseWind(metar):
    """
    Parses wind data from a METAR string.

    Args:
        metar: The wind part of the METAR string (e.g., "25012KT", "VRB05KT").

    Returns:
        A dictionary containing wind direction, speed, unit, and gust (if present),
        or None if parsing fails.
    """
    metar = metar.upper()

    # Variable wind direction
    if metar.startswith("VRB"):
        wind_match = re.match(r"VRB(\d{2,3})(G(\d{2,3}))?(KT|MPS|KMH)", metar)
        if wind_match:
            wind_data = {
                "direction": "VRB",
                "speed": int(wind_match.group(1)),
                "unit": wind_match.group(2),
                "gust": int(wind_match.group(4)) if wind_match.group(4) else None,
            }
            return convertSpeedsToKT(wind_data)
        else:
            return {"direction": "VRB", "speed": None, "unit": None, "gust": None}

    # Regular wind direction
    wind_match = re.match(r"(\d{3})(\d{2,3})(G(\d{2,3}))?(KT|MPS|KMH)", metar)
    if wind_match:
        wind_data = {
            "direction": int(wind_match.group(1)),
            "speed": int(wind_match.group(2)),
            "unit": wind_match.group(3),
            "gust": int(wind_match.group(4)) if wind_match.group(4) else None,
        }
        return convertSpeedsToKT(wind_data)
    else:
        return None
    
def convertSpeedsToKT(wind_data):
    """
    Converts wind speeds from MPS or KMH to KT.

    Args:
        wind_data: A dictionary containing wind data.

    Returns:
        The wind data dictionary with speeds converted to KT.
    """
    if wind_data["unit"] == "MPS":
        wind_data["speed"] = int(wind_data["speed"] * 1.94384)
        wind_data["unit"] = "KT"
    elif wind_data["unit"] == "KMH":
        wind_data["speed"] = int(wind_data["speed"] * 0.539957)
        wind_data["unit"] = "KT"
    return wind_data

def parseTime(metar):
    """
    Parses a METAR time string (DDHHMMZ) into a datetime object.

    Args:
        metar: The METAR time string (e.g., "202200Z").

    Returns:
        A datetime object in UTC, or None if parsing fails.
    """
    try:
        day = int(metar[:2])
        hour = int(metar[2:4])
        minute = int(metar[4:6])

        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month

        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    except (ValueError, IndexError):
        return None

def parseQNH(metar):
    """
    Parses the QNH (altimeter setting) from a METAR and converts it to millibars (mbar).

    Args:
        metar: The QNH string (e.g., "A3015", "Q1013").

    Returns:
        The QNH in millibars as a float, or None if parsing fails.
    """
    try:
        if metar.startswith("A"):
            inches_hg = int(metar[1:])
            mbar = inches_hg * 0.338639
            return int(round(mbar, 0)) #round to 1 decimal place.
        elif metar.startswith("Q"):
            return int(metar[1:])
        else:
            return None  # Invalid format

    except (ValueError, AttributeError):
        return None  # Parsing error