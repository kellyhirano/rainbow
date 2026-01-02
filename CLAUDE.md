# CLAUDE.md

AI Assistant documentation for the Rainbow HAT Display project.

## Project Overview

This is a **Raspberry Pi hardware project** that displays real-time sensor data on a [Pimoroni Rainbow HAT](https://shop.pimoroni.com/products/rainbow-hat-for-android-things). The application reads environmental and energy data from MQTT topics and presents it through three user-selectable display modes controlled by physical touch buttons.

**Key Purpose**: Real-time monitoring of weather conditions (temperature, AQI, wind, rain) and home energy consumption (power load, daily usage, peak demand) on a 4-digit 7-segment display.

## Codebase Structure

```
rainbow/
├── rainbow.py                          # Main application (single file)
├── requirements.txt                    # Python dependencies
├── README.md                          # User documentation
├── LICENSE                            # MIT license
├── .gitignore                         # Git ignore patterns (*.conf)
└── etc/
    └── systemd/
        └── system/
            └── rainbow.service        # systemd service definition
```

**Important**: This is a **single-file Python application** (rainbow.py). All logic is contained in one module for simplicity.

## Technology Stack

### Hardware Requirements
- **Raspberry Pi** (any model with GPIO pins)
- **Pimoroni Rainbow HAT** (7-segment display, RGB LEDs, touch buttons, LED bar)
- Running on **Linux** with systemd

### Software Dependencies
- **Python 3** (system Python)
- **paho-mqtt** (~1.5.0) - MQTT client library
- **rainbowhat** (~0.1.0) - Pimoroni Rainbow HAT hardware control library
- System packages: `python3-pip`, `python3-smbus`

### External Services
- **MQTT Broker** - Required for receiving sensor data
  - Weather data from WeeWX weather station
  - AQI data from PurpleAir sensor
  - Energy data from Rainforest EMU-2 energy monitor

## Architecture

### Code Organization

The application uses a **global state + callback** architecture:

1. **Global State Variables**
   - `g_mqtt_data` - Dictionary storing latest values from all MQTT topics
   - `g_current_mode` - Current display mode (weather/energy/night)

2. **Hardware Event Callbacks**
   - Touch button decorators (`@rainbowhat.touch.A.press()`)
   - Button press changes mode and lights RGB LED
   - Button release turns off RGB LED

3. **MQTT Event Callbacks**
   - `on_connect()` - Subscribes to all required topics
   - `on_message()` - Updates `g_mqtt_data` dictionary and flashes indicator

4. **Display Functions**
   - `display_weather()` - Shows temp, AQI, wind, rain
   - `display_energy()` - Shows power load, hourly avg, daily total, peak
   - `display_night()` - Minimal blinky pattern for night hours

5. **Main Loop**
   - Continuously calls appropriate display function based on current mode
   - Auto-activates night mode during 11 PM - 7 AM
   - 2-second sleep between display updates

### Display Modes

| Button | Mode | Global Constant | Auto-Activation |
|--------|------|----------------|-----------------|
| A | Weather | `MODE_WEATHER` | Default on startup |
| B | Energy | `MODE_ENERGY` | User-triggered only |
| C | Night | `MODE_NIGHT` | Auto 11 PM - 7 AM, or manual |

### MQTT Data Contract

**Weather Topics:**
```python
'weewx/sensor': {
    'outdoor_temperature': float,
    'outdoor_temp_change': float,       # 1-hour delta
    'outdoor_24h_temp_change': float,   # 24-hour delta
    'rain_rate': float,
    'wind_gust': float
}
'purpleair/sensor': {
    'st_aqi': int                       # Short-term AQI
}
'purpleair/last_hour': {
    'st_aqi': int                       # Last hour AQI value
}
```

**Energy Topics:**
```python
'rainforest/load': {
    'instantaneous': float              # Current kW demand
}
'rainforest/hourly': {
    'avg_kw': float                     # 60-min average
}
'rainforest/24h_compare': {
    'diff_kw': float                    # vs 24h ago
}
'rainforest/daily': {
    'total_kwh': float                  # Daily total
}
'rainforest/peak': {
    'peak_kw': float                    # Peak today
}
```

## Development Workflow

### Git Workflow
- **Main branch**: Direct commits to default branch
- **Feature branches**: Use `claude/` prefix for AI assistant changes
- **Commit style**: Descriptive messages (e.g., "Remove old weather.py and rainbow-weather.service")
- **History**: Linear history, no merge commits in current state

### Testing
- **No automated tests** currently exist
- **Manual testing** on actual Raspberry Pi hardware required
- Must test with real Rainbow HAT hardware (GPIO, display, buttons)

### Deployment
1. Code runs directly from `/home/pi/rainbow` on Raspberry Pi
2. Managed as systemd service (`rainbow.service`)
3. Runs as `pi` user
4. Auto-restarts on failure
5. Starts automatically on boot when enabled

## Code Conventions

### Python Style
- **Shebang**: `#!/usr/bin/env python3`
- **Docstrings**: Triple-quoted strings for module and functions
- **Naming**:
  - Functions: `snake_case` (e.g., `display_weather`, `set_mode`)
  - Constants: `SCREAMING_SNAKE_CASE` (e.g., `MODE_WEATHER`)
  - Globals: `g_` prefix (e.g., `g_mqtt_data`, `g_current_mode`)
- **Imports**: Standard library first, then third-party (configparser, json, time, then paho.mqtt, rainbowhat)
- **Line length**: No strict limit, practical readability
- **Comments**: Inline comments for clarity, docstrings for functions

### Display Patterns
- **4-digit limit**: All text must fit in 4 characters or scroll
- **Label-then-value**: Show text label, then numeric value
- **Sleep timing**:
  - Title/label: 0.5s default
  - Numbers: 1-2s default
  - Return to main metric between sub-metrics
- **Decimal point**: Position 3 (rightmost) used for message indicator flash

### Hardware Interaction Patterns
- **RGB LED**: Shows which button was pressed (Red/Green/Blue), turns off on release
- **Display clear**: Always `clear()` before new content
- **Display update**: Must call `.show()` after changes
- **Non-blocking**: Use `client.loop_start()` for background MQTT, not `loop_forever()`

## Configuration

### Required Configuration File: `mqtt.conf`

```ini
[ALL]
mqtt_host: <mqtt server ip>
mqtt_host_port: 1883
```

**Important**: `mqtt.conf` is gitignored (contains server credentials)

### Service Configuration

Edit `etc/systemd/system/rainbow.service` to change:
- Working directory (default: `/home/pi/rainbow`)
- User (default: `pi`)
- Restart policy (default: `always`)

## Common Development Tasks

### Adding a New Display Mode

1. Define mode constant at top of file:
   ```python
   MODE_NEWMODE = 'newmode'
   ```

2. Create display function:
   ```python
   def display_newmode():
       """Display new mode data."""
       # Access data from g_mqtt_data
       # Use display_message() helper
   ```

3. Add button handler (use unused button or repurpose):
   ```python
   @rainbowhat.touch.X.press()
   def touch_x(channel):
       rainbowhat.lights.rgb(r, g, b)
       set_mode(MODE_NEWMODE)
   ```

4. Add to main loop:
   ```python
   elif g_current_mode == MODE_NEWMODE:
       display_newmode()
   ```

### Adding New MQTT Topics

1. Subscribe in `on_connect()`:
   ```python
   client.subscribe([
       # ... existing subscriptions
       ("new/topic", 0),
   ])
   ```

2. Access data in display function:
   ```python
   if 'new/topic' in g_mqtt_data:
       value = g_mqtt_data['new/topic']['field_name']
   ```

### Modifying Display Timing

- Edit sleep values in `display_message()` calls
- Default parameters: `number_sleep=1`, `title_sleep=.5`
- Override per call: `display_message(['TEMP'], [temp], number_sleep=2)`

### Changing Night Hours

Modify `is_night_hours()` function (currently 11 PM - 7 AM):
```python
def is_night_hours():
    current_hour = int(time.strftime("%H", time.localtime()))
    return current_hour < 7 or current_hour >= 23  # Change these numbers
```

## Hardware Constraints

### Display Limitations
- **4 characters max** (7-segment display)
- **Numbers only**: Use `print_number_str()` for values
- **Text**: Use `print_str()` for labels (limited character set)
- **Decimal points**: 4 positions (0-3), position 3 used for indicators

### Rainbow HAT Components Used
- **Touch buttons**: A, B, C (capacitive touch)
- **RGB LED**: Single 3-color LED (feedback for button presses)
- **7-segment display**: 4-digit alphanumeric
- **LED bar**: Not currently used
- **Rainbow LEDs**: Used only in night mode (all set to 0,0,0 = off)

### Rainbow HAT Components NOT Used
- **LED bar graph**: 7 LEDs available but unused
- **Rainbow LEDs**: APA102 addressable RGB LEDs (7 total), turned off except night mode
- **Buzzer**: Available but not used

## AI Assistant Guidelines

### When Making Changes

1. **Read before editing**: Always read `rainbow.py` before making any modifications
2. **Test is manual**: Remember this requires physical hardware - you cannot run automated tests
3. **Single-file simplicity**: Keep all logic in `rainbow.py` unless there's strong reason to split
4. **Preserve patterns**: Follow existing `display_message()` pattern for consistency
5. **Hardware awareness**: Changes must work with 4-digit display and 3-button limitation

### What to Avoid

- **Don't add complexity**: No need for classes, modules, or abstractions for this small project
- **Don't add automated tests**: Hardware testing requires physical Rainbow HAT
- **Don't add type hints**: Not used in this codebase (Python 3 compatible, but untyped)
- **Don't remove global state**: The callback architecture requires global state
- **Don't add async/await**: Current blocking + background MQTT works fine
- **Don't add logging framework**: Simple `print()` statements are sufficient

### Configuration Changes

- **Never commit `mqtt.conf`**: It's gitignored for security
- **Preserve .gitignore**: Keep `*.conf` pattern
- **Document in README**: Update MQTT topics section if adding new subscriptions

### Service/Deployment Changes

- **Test service file syntax**: Use `systemd-analyze verify` if modifying
- **Working directory**: Must match actual installation path on Pi
- **User permissions**: `pi` user needs GPIO access (handled by system groups)

### Responding to User Requests

**For feature additions**:
1. Confirm understanding of 4-character display constraint
2. Ask which button should trigger the mode (if adding display mode)
3. Clarify MQTT topic structure and data format
4. Implement following existing patterns

**For bug fixes**:
1. Check if issue is hardware-specific (may not be reproducible without Pi)
2. Look for off-by-one errors in display positions (0-3 indexing)
3. Check for missing `rainbowhat.display.show()` calls
4. Verify MQTT topic names match exactly (case-sensitive)

**For refactoring requests**:
1. Push back on unnecessary complexity
2. Preserve single-file structure unless strong justification
3. Keep global state pattern for hardware callbacks
4. Maintain backward compatibility with existing MQTT topics

### Understanding Context

- **Target audience**: Hobbyist maker with Raspberry Pi
- **Reliability**: Must run 24/7 unattended
- **Updates**: Deployed manually via git pull + systemd restart
- **Monitoring**: Via systemd logs (`journalctl -u rainbow`)

### Git Operations

- **Branch naming**: Use `claude/` prefix for AI-generated changes
- **Commit messages**: Descriptive, imperative mood ("Add feature" not "Added feature")
- **Push carefully**: This is a production system running on physical hardware
- **Tag releases**: Not currently used, but could be beneficial for rollbacks

## Troubleshooting Common Issues

### Display shows "WAIT"
- **Cause**: No data received on required MQTT topics
- **Fix**: Check MQTT broker connection, verify topic names, check `mqtt.conf`

### Buttons not responding
- **Cause**: GPIO permissions or hardware connection issue
- **Fix**: Ensure running as user with GPIO access, check Rainbow HAT seating

### Service fails to start
- **Cause**: Missing `mqtt.conf` or wrong working directory
- **Fix**: Verify file exists at `/home/pi/rainbow/mqtt.conf`, check service `WorkingDirectory`

### Display garbled or numbers cut off
- **Cause**: Value too large for 4-digit display
- **Fix**: Adjust `format_kw()` logic or display formatting

## File Change History

Based on git history, key evolution:
1. Initial commit: Basic project structure
2. Description updates and dependency refinements
3. Removed `smbus` from requirements (system package)
4. Migrated from single-purpose weather display to multi-mode system
5. Removed old `weather.py` and `rainbow-weather.service` in favor of unified `rainbow.py`

## Future Enhancement Considerations

If users request these, here's how to approach:

- **Add more modes**: Follow "Adding a New Display Mode" pattern
- **LED bar usage**: Use `rainbowhat.lights.pixel[0-6]` for indicators
- **Rainbow LED effects**: Control via `rainbowhat.rainbow.set_pixel()`
- **Logging to file**: Add file handler, but keep console output for systemd
- **Configuration reload**: Add signal handler (SIGHUP) to re-read mqtt.conf
- **Multiple MQTT brokers**: Extend config file format and client setup
- **Display animations**: Add smooth transitions between values
- **Button combinations**: Track multi-button state for advanced features

## Dependencies Update Policy

- **Pin major versions** with `~=` to allow minor/patch updates
- **Test on actual hardware** before updating rainbowhat library
- **paho-mqtt**: Stable, updates rarely needed
- **rainbowhat**: Hardware-specific, update cautiously

## Security Considerations

- **MQTT credentials**: Stored in gitignored `mqtt.conf`
- **Network exposure**: Assumes trusted local network
- **No authentication**: MQTT client uses anonymous connection (acceptable for home LAN)
- **Service user**: Runs as `pi` (not root), but has GPIO access
- **No web interface**: No attack surface from network services

## Related Documentation

- [Pimoroni Rainbow HAT Python library](https://github.com/pimoroni/rainbow-hat)
- [paho-mqtt documentation](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)
- [systemd service documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Last Updated**: 2026-01-02
**Target Python Version**: 3.x (tested on Raspberry Pi OS)
**Hardware Platform**: Raspberry Pi with Pimoroni Rainbow HAT
