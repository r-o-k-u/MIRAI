# 🚀 MIRAI Phase: Dual Hoverboard Motor Control with PlatformIO

## 📋 Overview
Complete implementation for controlling two hoverboard motors with ZS-X11H controllers, including PID control, hall sensor feedback, smooth braking functionality, and ROS2 compatibility.

## 🛠 Hardware Setup

### Components Required
- Arduino Mega 2560 or Arduino Nano
- 2x ZS-X11H Motor Controllers
- 2x Recycled Hoverboard Motors (Brushless DC)
- External Power Supply (24-36V for hoverboard motors)

### ZS-X11H Motor Controller Pinout

**Left Motor Controller:**
```text
ZS-X11H Left Arduino
─────────────────────────────────
P (Red - PWM) → Digital Pin 10
S (Yellow - Speed) → Digital Pin 11 (Input)
BRK (Blue - Brake) → Digital Pin 5
DIR (Orange - Direction) → Digital Pin 4
GND (Black) → GND
```

**Right Motor Controller:**
```text
ZS-X11H Right Arduino
─────────────────────────────────
P (Red - PWM) → Digital Pin 9
S (Yellow - Speed) → Digital Pin 12 (Input)
BRK (Blue - Brake) → Digital Pin 3
DIR (Orange - Direction) → Digital Pin 2
GND (Black) → GND
```


### Power Connections:
```text
External Power Supply → Motor Controllers
─────────────────────────────────────────
24-36V (+) → VM on both controllers
GND (-) → GND on both controllers

```

### ⚠️ Critical Safety Notes:
- Hoverboard motors require 24-36V! Do not use lower voltages
- Connect all GND connections together - Arduino GND must connect to external power supply GND
- Use appropriate wire gauge - 14-16 AWG for motor power connections
- Add fuses - 20-30A fuses recommended on VM power lines

## 📁 PlatformIO Project Structure
mirai-hoverboard-motor-control/
├── include/
│ ├── config.h
│ ├── motor_control.h
│ ├── pid_control.h
│ └── communication.h
├── src/
│ ├── main.cpp
│ ├── motor_control.cpp
│ ├── pid_control.cpp
│ └── communication.cpp
├── platformio.ini
└── README.md



### ⚙️ PlatformIO Configuration

**platformio.ini**
```ini
; For Arduino Mega
[env:megaatmega2560]
platform = atmelavr
board = megaatmega2560
framework = arduino
monitor_speed = 115200
lib_deps = 
    frankjoshua/Rosserial Arduino Library@^0.9.1
build_flags = 
    -D ROS2_SERIAL_BAUDRATE=115200
    -D SERIAL_DEBUG

; For Arduino Nano
[env:nanoatmega328]
platform = atmelavr
board = nanoatmega328
framework = arduino
monitor_speed = 115200
build_flags = 
    -D ROS2_SERIAL_BAUDRATE=115200
    -D SERIAL_DEBUG
```
## 🧪 Testing Procedure
##### 1. Build and Upload
```bash
# Build the project
pio run

# Upload to Arduino
pio run --target upload

# Monitor serial output
pio device monitor
```
##### 2. Basic Functionality Test
Test these commands in sequence:

- **HELP** - Show available commands

- **F** - Move both motors forward

- **150** - Set speed to 150/255

- **SOFTBRAKE** - Test soft braking

- **R** - Move both motors reverse

- **HARDBRAKE** - Test hard braking

- **COAST** - Let motors free spin

- **E** - Emergency stop

- **C** - Clear emergency

- **D** - Show diagnostics

##### 3. Individual Motor Control Test
- **ML:100** - Motor L at speed 100

- **MR:200** - Motor R at speed 200

- **STATUS** - Check individual motor status

##### 4. PID Control Test
- **PID** - Show PID status

- **PIDL**:0.2,0.8,0.002,60 - Tune left PID

- **PIDR**:0.18,0.75,0.0015,55 - Tune right PID

- **PIDBOTH**:RESET - Reset both PIDs

##### 5. ROS2 Simulation Test
Test ROS2-like commands:

- **ROS:FORWARD**

- **ROS:SPEED:180**

- **ROS:SOFTBRAKE**

- **ROS:STATUS**

## 🔌 ROS2 Integration Setup
##### Orange Pi Side Setup

``` bash
# On Orange Pi Zero 2W
sudo apt update
sudo apt install ros-humble-rosserial-arduino ros-humble-rosserial

# Create ROS2 package
ros2 pkg create mirai_motor_control --build-type ament_cmake

```
## Serial Communication Setup
The code uses Serial1 (pins 18/19 on Mega) for ROS2 communication:

- Connect Orange Pi TX → Arduino RX1 (pin 19 on Mega)

- Connect Orange Pi RX → Arduino TX1 (pin 18 on Mega)

- Connect GND between both devices

## 📦 Production Deployment
1. Optimize Build Settings
``` ini
; platformio.ini optimization for production
build_flags = 
    -D ROS2_SERIAL_BAUDRATE=115200
    -Os
    -flto
2. Create Deployment Script
```
``` bash
#!/bin/bash
# deploy-hoverboard-motors.sh

echo "🔨 Building MIRAI Hoverboard Motor Controller..."
pio run

echo "📤 Uploading to Arduino..."
pio run --target upload

echo "✅ Deployment complete!"
echo "📋 Serial monitor: pio device monitor"
```
## 🚨 Troubleshooting Common Issues
##### Motors not moving?

- Check all GND connections are common

- Verify 24-36V power supply is working

- Test with multimeter for voltage at VM pins

##### Erratic motor behavior?

- Ensure all connections are secure

- Check for loose speed sensor connections

- Verify PWM pins are correctly configured

##### Controllers overheating?

- Add heatsinks to ZS-X11H controllers

- Ensure adequate airflow

- Reduce load or use higher current rating controllers

##### Serial communication issues?

- Verify baud rate matches (115200)

- Check TX/RX connections are not reversed

- Ensure common ground between all devices

##### PID tuning issues?

- Start with low gains: PIDBOTH:0.1,0.5,0.0005,30

- Gradually increase until you get stable response

- Use PIDSTATUS to monitor performance

## 📊 Expected Performance
- Speed Range: 0-255 PWM (approximately 0-300 RPM for hoverboard motors)

- Current Draw: 5-20A per motor under load

- Response Time: <100ms for speed changes

- Braking Distance: 0.5-2m depending on speed and braking mode

- PID Stability: <5% overshoot with proper tuning

## 🔧 PID Tuning Guide
1. **Start with basic P control**: PIDBOTH:0.15,0,0,0

2. **Add I term to eliminate steady-state error**: PIDBOTH:0.15,0.7,0,50

3. **Add D term to reduce overshoot: PIDBOTH**:0.15,0.7,0.001,50

4. **Fine-tune for your specific motors**: Adjust based on response

##### Recommended starting values:

- Kp: 0.15-0.25

- Ki: 0.5-1.0

- Kd: 0.001-0.005

- Max Integral: 30-70