# CLAUDE.md

## Overview

Multi-mode display for Pimoroni Rainbow HAT (4-digit 7-segment + RGB LED + touch buttons) on Raspberry Pi. Shows weather or energy data; modes switched via physical buttons.

## Running / Deployment

```bash
# Deploy via Ansible
cd /home/hirano/dev/ansible && ./deploy.sh rainbow
```

## Configuration (`mqtt.conf`, gitignored)

```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```

## Display Modes

| Button | Mode | Auto-activation |
|--------|------|-----------------|
| A | Weather (temp, AQI, wind, rain) | Default on startup |
| B | Energy (load, daily kWh, peak) | Manual only |
| C | Night (blinky) | Auto 10:30 PM–6:30 AM |

## Architecture

Single file `rainbow.py`. Global state + callback pattern required by hardware library. `g_mqtt_data` dict holds latest values. MQTT runs in background via `client.loop_start()`. Main loop calls display function based on `g_current_mode`.

**4-character limit**: all display values must fit in 4 chars. Label shown briefly, then value.

## Key Constraints

- **Single file** — keep all logic in `rainbow.py`
- **No automated tests** — requires physical Rainbow HAT hardware
- **Global state** — necessary for hardware button callbacks; don't remove

## MQTT Topics

Weather: `weewx/sensor`, `purpleair/sensor`, `purpleair/last_hour`
Energy: `rainforest/load`, `rainforest/hourly`, `rainforest/24h_compare`, `rainforest/daily`, `rainforest/peak`
