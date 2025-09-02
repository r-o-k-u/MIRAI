# Installation
# Create virtual environment
python -m venv venv
source venv/Scripts/activate # On Windows: venv\Scripts\activate

# Install dependencies
```bash
pip install -r requirements.txt
```
# 🚀 Usage Examples

# 0. Run with simulation mode (no Arduino needed):

``` bash
python src/main.py --simulate
```
## 1. Start with GUI
```bash
python src/main.py
```
## 2. Start without GUI (CLI mode)
``` bash
python src/main.py --no-gui
```
## 3. With custom config
```bash
python src/main.py --config my_config.yaml
```
## 4. Programmatic Usage
``` python
from motor_controller import MotorController

# Initialize controller
controller = MotorController('config/settings.yaml')
controller.start()

# Control motors
controller.set_both_speeds(150)  # Set both motors to speed 150
controller.set_direction('left', 'FORWARD')

# Get status
status = controller.get_status()
print(f"Left motor speed: {status['motors']['left']['speed']}")

# Save data
controller.save_data('motor_data.json')

controller.stop()
```
# 📊 Features
# Real-time Monitoring
- Live motor speed visualization

- Target vs actual speed comparison

- Hall sensor pulse counting

- System status monitoring

## Control Interface
- Graphical control buttons

- Keyboard shortcuts

- Emergency stop functionality

- Braking control (soft/hard)

## Data Logging
- Automatic data recording

- Export to JSON format

- Configurable history length

- Timestamped data points

## Advanced Features
- PID control visualization

- ROS2 integration status

- Serial communication monitoring

- Customizable themes and layout

# 🔧 Configuration
## Customizing Settings
Edit config/settings.yaml to modify:

- Serial port settings

- Motor parameters

- PID constants

- Visualization preferences

- Logging configuration

## Adding New Plots
Extend the DataVisualizer class to add additional plots or dashboard elements.

## Custom Commands
Add new motor control commands by extending the MotorController class.



# Finding Arduino COM Port in WSL

## Method 1: Check Windows Device Manager
Open Windows Device Manager (press Win + X, then select Device Manager)

Look under "Ports (COM & LPT)"

You should see something like "Arduino Mega 2560 (COM3)" or "USB Serial Device (COM4)"

## Method 2: Use WSL Command
```bash
# List all serial devices
ls /dev/ttyS* /dev/ttyUSB* /dev/ttyACM*

# Typically Arduino shows up as:
# /dev/ttyACM0  (most common in WSL)
# /dev/ttyUSB0
# /dev/ttyS0    (rare for Arduino)
```
# Method 3: Check Windows from WSL
``` bash
# PowerShell command from WSL to check Windows COM ports
powershell.exe -Command "[System.IO.Ports.SerialPort]::getportnames()"

# Or using wmic
cmd.exe /c "wmic path Win32_SerialPort get DeviceID, Description"
```
# Method 4: Arduino IDE Method
Open Arduino IDE

Go to Tools > Port

It will show the connected Arduino port (like COM3 or COM4)

# Common WSL Arduino Port Mappings
Windows COM3 → WSL: /dev/ttyS3

Windows COM4 → WSL: /dev/ttyS4

Some WSL distributions: /dev/ttyACM0
