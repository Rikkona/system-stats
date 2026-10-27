---
name: weather
description: Check current weather and a 1–7 day forecast for a city or coordinates using Open-Meteo. Use for weather, temperature, rain or wind requests, including Russian queries such as какая погода, погода в городе, будет ли дождь, прогноз на завтра.
---

# Weather

Use `tools/weather/weather.py` from the project root. It needs Python 3 and internet access, with no packages or API key for the public non-commercial API.

## Execution on Windows / Codex desktop

Use an available Python 3 executable. If `python` is not found, use the desktop
`load_workspace_dependencies` tool to obtain the bundled Python executable and
invoke its full path in PowerShell with `& "PATH/TO/python.exe"` followed by
the script and arguments. Do not install Python or change PATH just for this.

If the command runner fails before Python starts with `CreateProcess`,
`helper_unknown_error` or `setup refresh had errors`, this is a sandbox startup
failure, not a weather-tool failure. Retry the same read-only command using
`sandbox_permissions="require_escalated"` and an explanation in `justification`.
The same normal approval mechanism applies to sandbox network failures.
If approval is denied or the retry fails, report the exact error and stop.
Do not substitute web search or another weather provider for this skill's
Open-Meteo execution unless the user asks for that fallback. A successful web
search does not count as a successful test of this skill.

## Weather workflow

1. Use the city or coordinates supplied by the user or already explicitly established in the conversation. For “weather here” with no known location, ask for the city. Do not infer location from the computer timezone or silently use IP geolocation.
2. Run `python tools/weather/weather.py --city "CITY"`. Optional `--country RU` filters by ISO country code. If the response contains `candidates`, show their city, region and country and ask the user to choose; repeat with the same query and `--choice N`. Never silently choose the first ambiguous result.
3. For known coordinates, run `python tools/weather/weather.py --latitude 55.75 --longitude 37.62`. Coordinates are examples, not a default location. `--days N` selects 1–7 days (default: 1).
4. Summarize the returned current temperature, feels-like temperature, conditions, wind and precipitation; include daily minimum/maximum and rain probability when relevant. Use the returned units, location, local timestamp and timezone. These are model-based current conditions, not a guaranteed station observation. Treat null values as unavailable, not zero.
5. Attribute [Open-Meteo](https://open-meteo.com/). On failure report the actual error without inventing weather or falling back to stale data. If sandbox networking blocks execution, request the normal execution approval and retry the same tool.

The tool prints JSON. Success and location candidates exit with code 0; invalid arguments and API/network errors exit with code 1 and an `error` field. No files or system settings are changed.

API references: [Forecast](https://open-meteo.com/en/docs), [Geocoding](https://open-meteo.com/en/docs/geocoding-api).
