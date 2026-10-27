# AGENTS.md

## System diagnostics

Machine state (CPU, memory, disk, uptime, processes, ports, benchmark) is
collected only via the `system-stats` skill. Never gather these metrics
with ad-hoc shell commands; read-only: never kill processes or change
system settings.

## Weather

For current weather and short forecast requests in this project (including
Russian requests such as "Какая погода в Нижнем Новгороде?" or "погода в Новом
Уренгое"), use the `weather` skill. Read `.agents/skills/weather/SKILL.md`
and run `tools/weather/weather.py` against Open-Meteo before answering.
If the skill is missing from the available-skills list, read that file directly.
Follow its Python runtime and sandbox retry instructions on launch failure.
Do not replace this workflow with web search, another weather provider, or
weather from an earlier response unless the user explicitly requests that.
If execution remains unavailable, report the actual failure instead of weather.
