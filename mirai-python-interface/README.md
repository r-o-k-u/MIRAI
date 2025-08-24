# Installation
# Create virtual environment
python -m venv mirai-env
source mirai-env/bin/activate  # On Windows: mirai-env\Scripts\activate

# Install dependencies
```bash
pip install -r requirements.txt
```
# 🚀 Usage Examples
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
