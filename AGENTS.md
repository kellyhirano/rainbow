# Repository Guidelines

## Project Structure & Module Organization
This repo is a single-file Python 3 app for the Pimoroni Rainbow HAT.

- `rainbow.py`: main application, MQTT handlers, and display modes.
- `requirements.txt`: Python dependencies.
- `etc/systemd/system/rainbow.service`: systemd unit for boot startup.
- `mqtt.conf`: runtime config (not tracked).

## Build, Test, and Development Commands
- Install deps (on Raspberry Pi): `sudo pip3 install -r requirements.txt`.
- Run locally: `python3 rainbow.py`.
- Enable service: `sudo cp etc/systemd/system/rainbow.service /etc/systemd/system/` and `sudo systemctl enable --now rainbow`.

## Coding Style & Naming Conventions
- Python 3, 4-space indentation, snake_case for functions, constants in SCREAMING_SNAKE_CASE.
- Keep MQTT subscriptions in `on_connect()` and update global state in `on_message()`.
- Maintain 4-character display constraints; use label-then-value patterns.

## MQTT Topics
| Mode | Topic | Purpose |
| --- | --- | --- |
| Weather | `weewx/sensor` | Temperature, wind, rain. |
| Weather | `purpleair/sensor` | AQI values. |
| Weather | `purpleair/last_hour` | AQI delta. |
| Energy | `rainforest/load` | Instantaneous kW. |
| Energy | `rainforest/hourly` | 60-minute average kW. |
| Energy | `rainforest/24h_compare` | Current vs 24h-ago. |
| Energy | `rainforest/daily` | Daily kWh total. |
| Energy | `rainforest/peak` | Peak kW today. |

## Testing Guidelines
- No automated tests; validate on real Rainbow HAT hardware.
- Verify button mode switching (A/B/C), night mode (11 PM–7 AM), and MQTT topic handling.

## Commit & Pull Request Guidelines
- Use short, imperative commit messages (“Remove old service”, “Add mode display”).
- PRs should describe the mode(s) affected, MQTT topics, and validation steps.

## Configuration & Ops Notes
- `mqtt.conf` is required; document new keys in `README.md`.
- Service file assumes `/home/pi/rainbow` as working directory; update if deployment path changes.
