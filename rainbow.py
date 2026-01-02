#!/usr/bin/env python3
"""Rainbow HAT display with weather, energy, and night modes.

Button controls:
  A - Weather mode (temperature, AQI, wind, rain)
  B - Energy mode (power load, hourly avg, daily total, peak)
  C - Night mode (dim blinky pattern)
"""

import configparser
import json
import time
import paho.mqtt.client as mqtt
import rainbowhat

# Display modes
MODE_WEATHER = 'weather'
MODE_ENERGY = 'energy'
MODE_NIGHT = 'night'

# Global state
g_mqtt_data = {}
g_current_mode = MODE_WEATHER


def set_mode(mode):
    """Set the current display mode."""
    global g_current_mode
    g_current_mode = mode
    print(f"Mode changed to: {mode}")


@rainbowhat.touch.A.press()
def touch_a(channel):
    """Switch to weather mode."""
    rainbowhat.lights.rgb(1, 0, 0)
    set_mode(MODE_WEATHER)


@rainbowhat.touch.A.release()
def release_a(channel):
    rainbowhat.lights.rgb(0, 0, 0)


@rainbowhat.touch.B.press()
def touch_b(channel):
    """Switch to energy mode."""
    rainbowhat.lights.rgb(0, 1, 0)
    set_mode(MODE_ENERGY)


@rainbowhat.touch.B.release()
def release_b(channel):
    rainbowhat.lights.rgb(0, 0, 0)


@rainbowhat.touch.C.press()
def touch_c(channel):
    """Switch to night mode."""
    rainbowhat.lights.rgb(0, 0, 1)
    set_mode(MODE_NIGHT)


@rainbowhat.touch.C.release()
def release_c(channel):
    rainbowhat.lights.rgb(0, 0, 0)


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK from the server."""
    print("Connected with result code " + str(rc))

    # Subscribe to all topics for both weather and energy modes
    client.subscribe([
        # Weather topics
        ("weewx/sensor", 0),
        ("purpleair/sensor", 0),
        ("purpleair/last_hour", 0),
        # Energy topics
        ("rainforest/load", 0),
        ("rainforest/hourly", 0),
        ("rainforest/24h_compare", 0),
        ("rainforest/daily", 0),
        ("rainforest/peak", 0),
    ])


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global g_mqtt_data

    print(msg.topic + " -> " + str(msg.payload.decode('UTF-8')))
    message_data = json.loads(str(msg.payload.decode('UTF-8')))

    g_mqtt_data[msg.topic] = message_data

    # Flash the rightmost decimal to show receipt of a message
    flash_decimal()


def flash_decimal():
    """Flash the rightmost decimal point to indicate message received."""
    rainbowhat.display.set_decimal(3, True)
    rainbowhat.display.show()
    time.sleep(.5)
    rainbowhat.display.set_decimal(3, False)
    rainbowhat.display.show()
    time.sleep(.25)
    rainbowhat.display.set_decimal(3, True)
    rainbowhat.display.show()
    time.sleep(.5)
    rainbowhat.display.set_decimal(3, False)
    rainbowhat.display.show()


def display_message(titles, numbers, show_title_at_end=False,
                    number_sleep=1, title_sleep=.5):
    """Display messages with different timings for titles vs numbers."""
    for title in titles:
        rainbowhat.display.clear()
        rainbowhat.display.print_str(title)
        rainbowhat.display.show()
        time.sleep(title_sleep)

    for number in numbers:
        rainbowhat.display.clear()
        rainbowhat.display.print_number_str(str(number))
        rainbowhat.display.show()
        time.sleep(number_sleep)

    if show_title_at_end:
        for title in titles:
            rainbowhat.display.clear()
            rainbowhat.display.print_str(title)
            rainbowhat.display.show()
            time.sleep(title_sleep)


def format_kw(value):
    """Format kW value for 4-char display (4 digits + decimal point)."""
    if value < 10:
        return f"{value:.3f}"
    elif value < 100:
        return f"{value:.2f}"
    return f"{int(value)}"


def display_weather():
    """Display weather and AQI data."""
    if 'weewx/sensor' not in g_mqtt_data:
        display_message(['WAIT'], [])
        return

    weewx = g_mqtt_data['weewx/sensor']
    temp = weewx['outdoor_temperature']

    temp_change = weewx.get('outdoor_temp_change', 0)
    temp_change_24h = weewx.get('outdoor_24h_temp_change', 0)
    rain_rate = weewx['rain_rate']
    wind_gust = weewx['wind_gust']

    aqi = 0
    last_1hr_aqi = 0
    if 'purpleair/sensor' in g_mqtt_data:
        aqi = g_mqtt_data['purpleair/sensor']['st_aqi']

    if 'purpleair/last_hour' in g_mqtt_data:
        last_1hr_aqi = g_mqtt_data['purpleair/last_hour']['st_aqi']

    if aqi >= 100:
        display_message(['AQI'], [aqi, last_1hr_aqi])

    if wind_gust >= 10:
        display_message(['GUST'], [wind_gust])

    if rain_rate > 0:
        display_message(['RAIN', 'RATE'], [rain_rate])

    display_message(['TEMP'], [temp], number_sleep=2)

    if temp_change != 0:
        display_message(['1H'], [temp_change], show_title_at_end=True)
        display_message([], [temp], number_sleep=2)

    if temp_change_24h != 0:
        display_message(['24H'], [temp_change_24h], show_title_at_end=True)
        display_message([], [temp], number_sleep=0)


def display_energy():
    """Display energy consumption data."""
    if 'rainforest/load' not in g_mqtt_data:
        display_message(['WAIT'], [])
        return

    load = g_mqtt_data['rainforest/load']['instantaneous']

    # Current load
    display_message(['LOAD'], [format_kw(load)])

    # Hourly average (if available)
    if 'rainforest/hourly' in g_mqtt_data:
        hourly = g_mqtt_data['rainforest/hourly']['avg_kw']
        display_message(['1H'], [format_kw(hourly)])

    # Show current load again
    display_message([], [format_kw(load)])

    # 24h comparison (if available)
    if 'rainforest/24h_compare' in g_mqtt_data:
        diff = g_mqtt_data['rainforest/24h_compare']['diff_kw']
        display_message(['24H'], [format_kw(diff)])

    # Show current load again
    display_message([], [format_kw(load)])

    # Daily total (if available)
    if 'rainforest/daily' in g_mqtt_data:
        daily = g_mqtt_data['rainforest/daily']['total_kwh']
        display_message(['DAY'], [format_kw(daily)])

    # Show current load again
    display_message([], [format_kw(load)])

    # Peak usage today (if available)
    if 'rainforest/peak' in g_mqtt_data:
        peak = g_mqtt_data['rainforest/peak']['peak_kw']
        display_message(['PEAK'], [format_kw(peak)])

    # Show current load again
    display_message([], [format_kw(load)])


def display_night():
    """Display dim blinky pattern for night mode."""
    rainbowhat.display.clear()
    rainbowhat.rainbow.set_all(0, 0, 0)
    rainbowhat.rainbow.show()

    for i in range(4):
        rainbowhat.display.set_decimal(i, True)
        rainbowhat.display.show()
        time.sleep(.1)
        rainbowhat.display.set_decimal(i, False)
        rainbowhat.display.show()

    time.sleep(8)


def is_night_hours():
    """Check if current time is in night hours (11 PM - 7 AM)."""
    current_hour = int(time.strftime("%H", time.localtime()))
    return current_hour < 7 or current_hour >= 23


def main():
    """Main entry point."""
    global g_current_mode

    config = configparser.ConfigParser()
    config.read('mqtt.conf')

    mqtt_host = config.get('ALL', 'mqtt_host')
    mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect_async(mqtt_host, mqtt_host_port, 60)
    client.loop_start()

    print("Rainbow HAT display started")
    print("Press A for weather, B for energy, C for night mode")

    while True:
        # Night mode takes precedence during night hours unless manually set
        if g_current_mode == MODE_NIGHT or (g_current_mode != MODE_NIGHT and is_night_hours()):
            if g_current_mode == MODE_NIGHT:
                display_night()
            else:
                # Auto night mode during night hours, but allow button override
                display_night()
        elif g_current_mode == MODE_WEATHER:
            display_weather()
        elif g_current_mode == MODE_ENERGY:
            display_energy()

        time.sleep(2)


if __name__ == '__main__':
    main()
