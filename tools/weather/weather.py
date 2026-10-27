#!/usr/bin/env python3
"""Read current weather and daily forecasts from the public Open-Meteo API."""

import argparse
import json
import math
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def request_json(base, params):
    try:
        with urlopen(base + "?" + urlencode(params), timeout=20) as response:
            data = json.load(response)
    except HTTPError as exc:
        raise ValueError("Open-Meteo HTTP error: %s" % exc.code) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError("Open-Meteo network error: %s" % exc) from exc
    if not isinstance(data, dict):
        raise ValueError("Unexpected Open-Meteo response")
    if data.get("error"):
        raise ValueError("Open-Meteo: %s" % data.get("reason", "unknown error"))
    return data


def conditions(code):
    groups = {
        "Clear sky": (0,),
        "Mainly clear": (1,),
        "Partly cloudy": (2,),
        "Overcast": (3,),
        "Fog": (45, 48),
        "Drizzle": (51, 53, 55),
        "Freezing drizzle": (56, 57),
        "Rain": (61, 63, 65),
        "Freezing rain": (66, 67),
        "Snow": (71, 73, 75, 77),
        "Rain showers": (80, 81, 82),
        "Snow showers": (85, 86),
        "Thunderstorm": (95,),
        "Thunderstorm with hail": (96, 99),
    }
    return next((name for name, codes in groups.items() if code in codes),
                "Unavailable" if code is None else "Unknown weather code")


def arguments(argv):
    parser = Parser(description=__doc__)
    parser.add_argument("--city", help="City name; quote names containing spaces")
    parser.add_argument("--country", help="ISO 3166-1 alpha-2 country filter")
    parser.add_argument("--choice", type=int, help="1-based candidate number")
    parser.add_argument("--latitude", type=float)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--days", type=int, default=1, help="Forecast days: 1–7")
    args = parser.parse_args(argv)
    coordinates = args.latitude is not None or args.longitude is not None
    if bool(args.city) == coordinates:
        raise ValueError("Provide either --city or both --latitude and --longitude")
    if args.city and not args.city.strip():
        raise ValueError("City must not be blank")
    if coordinates:
        if args.latitude is None or args.longitude is None:
            raise ValueError("Both latitude and longitude are required")
        if not (math.isfinite(args.latitude) and -90 <= args.latitude <= 90
                and math.isfinite(args.longitude) and -180 <= args.longitude <= 180):
            raise ValueError("Latitude must be -90..90; longitude must be -180..180")
        if args.country or args.choice is not None:
            raise ValueError("--country and --choice require --city")
    if args.country and (len(args.country) != 2 or not args.country.isascii()
                         or not args.country.isalpha()):
        raise ValueError("Country must be a two-letter ISO code, e.g. RU")
    if not 1 <= args.days <= 7:
        raise ValueError("Days must be 1..7")
    if args.choice is not None and args.choice < 1:
        raise ValueError("Choice must be a positive candidate number")
    return args


def weather(args):
    if args.city:
        params = {"name": args.city.strip(), "count": 10, "language": "ru",
                  "format": "json"}
        if args.country:
            params["countryCode"] = args.country.upper()
        results = request_json("https://geocoding-api.open-meteo.com/v1/search",
                               params).get("results", [])
        if not results:
            raise ValueError("Location not found; specify a different city or coordinates")
        if args.choice is None and len(results) > 1:
            return {"candidates": [dict(choice=i, **{key: item.get(key) for key in
                    ("name", "admin1", "country", "latitude", "longitude")})
                    for i, item in enumerate(results, 1)],
                    "message": "Choose a location and repeat with --choice N"}
        choice = args.choice or 1
        if choice > len(results):
            raise ValueError("Choice exceeds the number of candidates")
        location = {key: results[choice - 1].get(key) for key in
                    ("name", "admin1", "country", "latitude", "longitude")}
    else:
        location = {"latitude": args.latitude, "longitude": args.longitude}
    params = {
        "latitude": location["latitude"], "longitude": location["longitude"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_probability_max",
        "timezone": "auto", "temperature_unit": "celsius",
        "wind_speed_unit": "ms", "precipitation_unit": "mm",
        "forecast_days": args.days,
    }
    data = request_json("https://api.open-meteo.com/v1/forecast", params)
    if not isinstance(data.get("current"), dict) or not isinstance(data.get("daily"), dict):
        raise ValueError("Open-Meteo response is missing current or daily weather")
    data["current"]["conditions"] = conditions(data["current"].get("weather_code"))
    return {"source": "https://open-meteo.com/", "location": location,
            "timezone": data.get("timezone"),
            "utc_offset_seconds": data.get("utc_offset_seconds"),
            "current": data["current"], "current_units": data.get("current_units"),
            "daily": data["daily"], "daily_units": data.get("daily_units")}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        result = weather(arguments(argv))
    except (ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
