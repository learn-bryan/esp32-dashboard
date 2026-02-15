import network
import socket
from machine import Pin, TouchPad, ADC, freq
import esp32
import gc
import time

# Setup LED
led = Pin(2, Pin.OUT)
led.off()

# Setup touch pad (GPIO4)
touch_pad = TouchPad(Pin(4))

# Setup ADC for analog reading (GPIO34 is input-only, good for ADC)
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)  # Full range: 0-3.3V

# Track boot time
boot_time = time.time()

# Setup Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-Dashboard', password='12345678')

sta = network.WLAN(network.STA_IF)
sta.active(True)

print('Access Point active')
print('Connect to WiFi and browse to http://192.168.4.1')

# Cache static values
ip_addr = ap.ifconfig()[0]
mac_addr = ':'.join(['%02x' % b for b in ap.config('mac')])
cpu_freq_val = str(freq() // 1000000)

def get_uptime():
    seconds = time.time() - boot_time
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    else:
        return f"{minutes}m {secs}s"

def web_page():
    led_state = 'ON' if led.value() else 'OFF'
    led_checked = 'checked' if led.value() else ''
    
    # Quick readings only
    touch_value = str(touch_pad.read())
    adc_value = str(adc.read())
    uptime = get_uptime()
    
    # Only check memory every few requests to speed things up
    free_mem = str(gc.mem_free() // 1024)
    total_mem = str((gc.mem_free() + gc.mem_alloc()) // 1024)
    
    # Temperature reading in Fahrenheit
    try:
        temp = str(round(esp32.raw_temperature(), 1))
    except:
        temp = "N/A"
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        h1 {
            color: #333;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 0.9em;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .card-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .card-value.small {
            font-size: 1.8em;
        }
        .card-label {
            font-size: 0.9em;
            color: #999;
        }
        
        /* Toggle Switch */
        .switch-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 80px;
            height: 40px;
        }
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 40px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 32px;
            width: 32px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #4CAF50;
        }
        input:checked + .slider:before {
            transform: translateX(40px);
        }
        .switch-label {
            font-size: 1.1em;
            color: #333;
            font-weight: 500;
        }
        
        /* Status indicator */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-on { background-color: #4CAF50; }
        .status-off { background-color: #f44336; }
        
        /* Info grid */
        .info-grid {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px;
            font-size: 0.9em;
        }
        .info-label {
            color: #666;
            font-weight: 500;
        }
        .info-value {
            color: #333;
            font-family: monospace;
        }
        
        /* Loading indicator */
        .loading {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px 20px;
            border-radius: 20px;
            display: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="loading" id="loading">Updating...</div>
    <div class="container">
        <div class="header">
            <h1>ESP32 Dashboard</h1>
            <p class="subtitle">ESP32-WROOM-32 Real-time Monitoring</p>
        </div>
        
        <div class="dashboard">
            <!-- LED Control -->
            <div class="card">
                <div class="card-title">LED Control</div>
                <div class="card-value">
                    <span class="status-indicator status-""" + ('on' if led.value() else 'off') + """"></span>
                    """ + led_state + """
                </div>
                <div class="switch-container">
                    <span class="switch-label">OFF</span>
                    <label class="switch">
                        <input type="checkbox" id="ledToggle" """ + led_checked + """>
                        <span class="slider"></span>
                    </label>
                    <span class="switch-label">ON</span>
                </div>
            </div>
            
            <!-- Touch Sensor -->
            <div class="card">
                <div class="card-title">Touch Sensor</div>
                <div class="card-value">""" + touch_value + """</div>
                <div class="card-label">GPIO4 capacitive</div>
            </div>
            
            <!-- Temperature -->
            <div class="card">
                <div class="card-title">Chip Temperature</div>
                <div class="card-value">""" + temp + """&deg;F</div>
                <div class="card-label">Internal sensor</div>
            </div>
            
            <!-- Memory -->
            <div class="card">
                <div class="card-title">Free Memory</div>
                <div class="card-value">""" + free_mem + """<span style="font-size:0.5em">KB</span></div>
                <div class="card-label">of """ + total_mem + """ KB total</div>
            </div>
            
            <!-- CPU Frequency -->
            <div class="card">
                <div class="card-title">CPU Frequency</div>
                <div class="card-value">""" + cpu_freq_val + """<span style="font-size:0.5em">MHz</span></div>
                <div class="card-label">Dual-core Xtensa LX6</div>
            </div>
            
            <!-- Uptime -->
            <div class="card">
                <div class="card-title">Uptime</div>
                <div class="card-value small">""" + uptime + """</div>
                <div class="card-label">Since last reset</div>
            </div>
            
            <!-- ADC Reading -->
            <div class="card">
                <div class="card-title">ADC (GPIO34)</div>
                <div class="card-value">""" + adc_value + """</div>
                <div class="card-label">0-4095 raw value</div>
            </div>
            
            <!-- Network Info -->
            <div class="card">
                <div class="card-title">Network Info</div>
                <div class="info-grid">
                    <div class="info-label">IP:</div>
                    <div class="info-value">""" + ip_addr + """</div>
                    <div class="info-label">MAC:</div>
                    <div class="info-value">""" + mac_addr + """</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let isUpdating = false;
        
        document.getElementById('ledToggle').addEventListener('change', function(e) {
            if (isUpdating) return;
            isUpdating = true;
            document.getElementById('loading').style.display = 'block';
            
            const newState = this.checked ? 'on' : 'off';
            fetch('/?led=' + newState)
                .then(() => {
                    setTimeout(() => { 
                        isUpdating = false;
                        document.getElementById('loading').style.display = 'none';
                    }, 500);
                })
                .catch(() => { 
                    isUpdating = false;
                    document.getElementById('loading').style.display = 'none';
                });
        });
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            if (!isUpdating) {
                document.getElementById('loading').style.display = 'block';
                location.reload();
            }
        }, 5000);
    </script>
</body>
</html>"""
    return html

# Setup socket with larger backlog
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

print('Web server running...')

while True:
    try:
        conn, addr = s.accept()
        conn.settimeout(3.0)  # 3 second timeout
        
        request = conn.recv(1024)
        request = str(request)
        
        if '/?led=on' in request:
            led.on()
        elif '/?led=off' in request:
            led.off()
        
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
        
    except Exception as e:
        print('Error:', e)
        try:
            conn.close()
        except:
            pass
