# rainbow

Display sensor data on a [Pimoroni Rainbow HAT](https://shop.pimoroni.com/products/rainbow-hat-for-android-things) connected to a Raspberry Pi. Data is read from a local MQTT server.

## Features

The Rainbow HAT's three touch buttons control display modes:

| Button | Mode | Description |
|--------|------|-------------|
| A | Weather | Temperature, AQI, wind gusts, rain rate |
| B | Energy | Power load, hourly avg, daily total, peak usage |
| C | Night | Dim blinky pattern (also activates automatically 11 PM - 7 AM) |

## Setup

Create a `mqtt.conf` file with MQTT server settings:
```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```

Install dependencies:
```bash
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
```

## Running

```bash
./rainbow.py
```

## Running automatically on boot

```bash
sudo cp etc/systemd/system/rainbow.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rainbow
sudo systemctl start rainbow
```

## MQTT Topics

### Weather mode
- `weewx/sensor` - Temperature, wind, rain data
- `purpleair/sensor` - AQI values
- `purpleair/last_hour` - Last hour AQI delta

### Energy mode
- `rainforest/load` - Instantaneous kW demand
- `rainforest/hourly` - 60-min average kW
- `rainforest/24h_compare` - Current vs 24h-ago comparison
- `rainforest/daily` - Daily kWh total
- `rainforest/peak` - Peak kW today
