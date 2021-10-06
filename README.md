# rainbow
A script designed to display weather information on a [Rainbow HAT](https://shop.pimoroni.com/products/rainbow-hat-for-android-things). It's reading data from my local mqtt server that's using specific topic names. I need to clean up that code and will link to that as well.

A mqtt.conf file must be created. It's a standard configparser doc that must define a MQTT server and it's port (default port is 1883).

This is currently too much of a copy and paste from the flp implementation. All
of this needs to be refactored.

### Running automatically on boot

```
sudo cp etc/systemd/system/rainbow-weather.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rainbow-weather
sudo systemctl start rainbow-weather
```
