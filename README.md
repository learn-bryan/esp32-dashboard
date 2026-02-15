# ESP32 Dashboard

A real-time web-based monitoring dashboard for ESP32-WROOM-32 development boards running MicroPython. Control GPIO pins and monitor system metrics through a clean, responsive web interface.

## Features

- **LED Control** - Toggle GPIO pins via web interface with visual status indicator
- **Touch Sensor Monitoring** - Real-time capacitive touch sensor readings (GPIO4)
- **System Metrics**
  - Internal chip temperature
  - Free/total RAM usage
  - CPU frequency
  - System uptime
  - ADC readings (GPIO34)
- **Network Information** - IP address and MAC address display
- **Auto-refresh** - Dashboard updates every 3 seconds
- **Responsive Design** - Works on desktop and mobile browsers
- **No Client Software Required** - Just connect to the ESP32's WiFi AP

## Hardware Requirements

- ESP32-WROOM-32 development board
- USB cable (data-capable, not power-only)
- Computer with USB port

## Software Requirements

- Python 3.x
- `esptool` - For flashing firmware
- `mpremote` - For file transfer to ESP32
- MicroPython firmware for ESP32

## Installation

### 1. Install Required Tools

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install tools
pip install esptool mpremote
```

### 2. Flash MicroPython to ESP32

```bash
# Download MicroPython firmware
wget https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin

# Erase existing flash
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython (replace /dev/ttyUSB0 with your port)
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
```

**Windows users:** Replace `/dev/ttyUSB0` with your COM port (e.g., `COM3`)

### 3. Upload Files to ESP32

```bash
# Upload boot.py
mpremote connect /dev/ttyUSB0 fs cp boot.py :boot.py

# Upload main.py
mpremote connect /dev/ttyUSB0 fs cp main.py :main.py

# Reset the ESP32
mpremote connect /dev/ttyUSB0 reset
```

## Usage

### Connecting to the Dashboard

1. **Power on your ESP32** (via USB or external power)
2. **Connect to the ESP32's WiFi network:**
   - **SSID:** `ESP32-Dashboard`
   - **Password:** `12345678`
3. **Open your browser** and navigate to: `http://192.168.4.1`

The dashboard will load and begin displaying real-time data.

### Features Overview

- **LED Control:** Use the toggle switch to turn GPIO2 (built-in LED) on/off
- **Touch Sensor:** Touch GPIO4 pin to see the capacitive reading change
- **Temperature:** Internal chip temperature in Fahrenheit
- **Memory:** Current free RAM in kilobytes
- **Uptime:** Time since last reset
- **ADC:** Raw analog reading from GPIO34 (0-4095)

## Configuration

### Changing WiFi Credentials

Edit `main.py` and modify these lines:

```python
ap.config(essid='ESP32-Dashboard', password='12345678')
```

### Changing the LED Pin

To use a different GPIO pin for LED control, edit `main.py`:

```python
led = Pin(2, Pin.OUT)  # Change 2 to your desired GPIO number
```

### Adjusting Auto-Refresh Rate

In `main.py`, find the JavaScript section and modify:

```javascript
setInterval(() => {
    // ...
}, 3000);  // Change 3000 to desired milliseconds
```

## Pin Configuration

| Feature | GPIO Pin | Notes |
|---------|----------|-------|
| LED Control | GPIO2 | Built-in LED on most ESP32 boards |
| Touch Sensor | GPIO4 | Any touch-capable pin works |
| ADC Input | GPIO34 | Input-only pin, suitable for analog |

## Troubleshooting

### ESP32 not showing up as USB device

- **Check your cable** - Must be data-capable, not power-only
- **Install drivers** - Some ESP32 boards need CH340 or CP2102 drivers
- **Check permissions** (Linux):
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in
  ```

### Can't connect to WiFi

- Verify SSID and password in `main.py`
- Check that Access Point is enabled: `ap.active(True)`
- Try forgetting the network on your device and reconnecting

### Dashboard loads slowly

- Normal for first load or after changes
- Subsequent loads should be faster due to caching
- Reduce auto-refresh interval if needed

### ETIMEDOUT errors when using mpremote

- This is expected when the web server is running
- The ESP32 is busy serving web pages
- To access REPL: Press Ctrl-C multiple times or reset the board

### Temperature shows "N/A"

- Some ESP32 revisions have unreliable internal temperature sensors
- This is a known hardware limitation
- The sensor provides rough estimates only

## Development

### Project Structure

```
esp32-dashboard/
├── boot.py          # Minimal boot configuration
├── main.py          # Web server and dashboard code
└── README.md        # This file
```

### Adding New Sensors

To add a new sensor to the dashboard:

1. **Import and configure the sensor** in `main.py`
2. **Read sensor values** in the `web_page()` function
3. **Add a new card** to the HTML dashboard section

Example for adding a DHT22 temperature sensor:

```python
# At the top of main.py
from dht import DHT22
dht_sensor = DHT22(Pin(15))

# In web_page() function
dht_sensor.measure()
dht_temp = str(dht_sensor.temperature())
dht_humidity = str(dht_sensor.humidity())

# In HTML section, add a new card:
            <div class="card">
                <div class="card-title">DHT22 Sensor</div>
                <div class="card-value">""" + dht_temp + """&deg;C</div>
                <div class="card-label">Humidity: """ + dht_humidity + """%</div>
            </div>
```

### Debugging

To see serial output while the web server runs:

```bash
screen /dev/ttyUSB0 115200
# Press Ctrl-A then K then Y to exit
```

Or use minicom:
```bash
minicom -D /dev/ttyUSB0 -b 115200
```

## Technical Details

### Hardware Specifications

- **Chip:** ESP32-D0WD-V3 (revision v3.1)
- **CPU:** Dual-core Xtensa LX6, up to 240MHz
- **RAM:** 520KB SRAM
- **Flash:** 4MB
- **WiFi:** 802.11 b/g/n (2.4GHz)
- **Bluetooth:** V4.2 BR/EDR and BLE

### Network Configuration

- **Mode:** WiFi Access Point (AP)
- **Default IP:** 192.168.4.1
- **Subnet:** 255.255.255.0
- **DHCP Range:** 192.168.4.2 - 192.168.4.10

## Future Enhancements

- [ ] WebREPL support for wireless debugging
- [ ] Data logging to SD card
- [ ] MQTT publishing for IoT integration
- [ ] Charts/graphs for sensor history
- [ ] PWM control with sliders
- [ ] Multiple page support
- [ ] OTA (Over-The-Air) firmware updates
- [ ] Deep sleep mode with wake-on-demand

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- MicroPython project for the excellent embedded Python implementation
- ESP32 community for hardware documentation and examples
- Espressif for the ESP32 platform

## Resources

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [MicroPython Forum](https://forum.micropython.org/)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
