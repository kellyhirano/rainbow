#!/usr/bin/env python3

import configparser
import json
import time
import paho.mqtt.client as mqtt
import rainbowhat

# Global for data storage
g_mqtt_data = {}


@rainbowhat.touch.A.press()
def touch_a(channel):
    rainbowhat.lights.rgb(1, 0, 0)


@rainbowhat.touch.A.release()
def release_a(channel):
    rainbowhat.rainbow.set_all(0, 0, 0)
    rainbowhat.rainbow.show()
    rainbowhat.lights.rgb(0, 0, 0)


@rainbowhat.touch.B.press()
def touch_b(channel):
    rainbowhat.lights.rgb(0, 1, 0)


@rainbowhat.touch.B.release()
def release_a(channel):
    rainbowhat.rainbow.set_all(64, 64, 64)
    rainbowhat.rainbow.show()
    rainbowhat.lights.rgb(0, 0, 0)


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK from the server."""
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([("weewx/sensor", 0),
                      ("purpleair/sensor", 0),
                      ("purpleair/last_hour", 0)])


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global g_mqtt_data

    print(msg.topic+" -> "+str(msg.payload.decode('UTF-8')))
    message_data = json.loads(str(msg.payload.decode('UTF-8')))

    g_mqtt_data[msg.topic] = message_data

    # Flash the rightmost decimal to show receipt of a message
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
    """Display messaages with different timings for titles vs numbers."""

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

    if (show_title_at_end):
        for title in titles:
            rainbowhat.display.clear()
            rainbowhat.display.print_str(title)
            rainbowhat.display.show()
            time.sleep(title_sleep)


config = configparser.ConfigParser()
config.read('mqtt.conf')

mqtt_host = config.get('ALL', 'mqtt_host')
mqtt_host_port = int(config.get('ALL', 'mqtt_host_port'))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect_async(mqtt_host, mqtt_host_port, 60)
client.loop_start()

while(1):
    if ('weewx/sensor' not in g_mqtt_data):
        time.sleep(5)
        client.loop()
        print('loop')
        continue

    temp = g_mqtt_data['weewx/sensor']['outdoor_temperature']
    temp_change = g_mqtt_data['weewx/sensor']['outdoor_temp_change']
    temp_change_24h = g_mqtt_data['weewx/sensor']['outdoor_24h_temp_change']
    rain_rate = g_mqtt_data['weewx/sensor']['rain_rate']
    wind_gust = g_mqtt_data['weewx/sensor']['wind_gust']

    aqi = 0
    last_1hr_aqi = 0
    if ('purpleair/sensor' in g_mqtt_data):
        aqi = g_mqtt_data['purpleair/sensor']['st_aqi']

    if ('purpleair/last_hour' in g_mqtt_data):
        last_1hr_aqi = g_mqtt_data['purpleair/last_hour']['st_aqi']

    current_hour = int(time.strftime("%H", time.localtime()))
    if (current_hour >= 7 and current_hour <= 23):

        if (aqi >= 100):
            display_message(['AQI'], [aqi, last_1hr_aqi])

        if (wind_gust >= 10):
            display_message(['GUST'], [wind_gust])

        if (rain_rate > 0):
            display_message(['RAIN', 'RATE'], [rain_rate])

        display_message(['TEMP'], [temp], number_sleep=2)

        display_message(['1H'], [temp_change], show_title_at_end=True)

        display_message([], [temp], number_sleep=2)

        display_message(['24H'], [temp_change_24h], show_title_at_end=True)

        display_message([], [temp], number_sleep=0)

    # Give the main display a rest at night and show a blinky pattern
    else:
        rainbowhat.display.clear()
        for i in range(4):
            rainbowhat.display.set_decimal(i, True)
            rainbowhat.display.show()
            time.sleep(.1)
            rainbowhat.display.set_decimal(i, False)
            rainbowhat.display.show()
        time.sleep(8) # Total = 10s of sleep

    time.sleep(2)
