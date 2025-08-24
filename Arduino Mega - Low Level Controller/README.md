# 🚀 MIRAI Phase 2: Dual Hoverboard Motor Control with PlatformIO

## 📋 Overview
Complete implementation for controlling two hoverboard motors with ZS-X11H controllers, including PID control, hall sensor feedback, smooth braking functionality, and ROS2 compatibility.

## 🛠 Hardware Setup

### Components Required
- Arduino Mega 2560
- 2x ZS-X11H Motor Controllers
- 2x Recycled Hoverboard Motors (Brushless DC)
- External Power Supply (24-36V for hoverboard motors)

### ZS-X11H Motor Controller Pinout
https://github.com/user-attachments/assets/controller-pinout-example *Note: Add actual photo of your ZS-X11H controller*


The ZS-X11H typically has these connections:

ENA: PWM Speed Control (connect to Arduino PWM pins)

IN1 & IN2: Direction Control (HIGH/LOW combinations determine direction)

VM: Motor Power Input (12-36V)

VCC: Logic Voltage (5V - often optional)

GND: Ground

Motor Outputs: A+ and A- (to motor phases)\

### Wiring Configuration
Motor Controller 1 (Left Motor) ↔ Arduino Mega
ZS-X11H Right       Arduino Mega
─────────────────────────────────
ENA_L (PWM)    → Digital Pin 5 (PWM capable)
IN1_L          → Digital Pin 6  
IN2_L          → Digital Pin 7 
HALL_L         → Digital Pin 2 (Interrupt 0)
GND            → GND (common ground)
Motor Connections:
A+ → Hoverboard Motor Phase U
A- → Hoverboard Motor Phase V

Motor Controller 2 (Right Motor) ↔ Arduino Mega
ZS-X11H Right       Arduino Mega
─────────────────────────────────
ENA_R (PWM)    → Digital Pin 9 (PWM capable)
IN1_R          → Digital Pin 10  
IN2_R          → Digital Pin 11
HALL_R         → Digital Pin 3 (Interrupt 1)
GND            → GND (common ground)

### Motor Connections:
A+ → Hoverboard Motor Phase U
A- → Hoverboard Motor Phase V
Power Connections:

text
External Power Supply → Motor Controllers
─────────────────────────────────────────
24-36V (+)           → VM on both controllers
GND (-)              → GND on both controllers

### ⚠️ Critical Safety Notes:

Hoverboard motors require 24-36V! Do not use lower voltages

Connect all GND connections together - Arduino GND must connect to external power supply GND

Use appropriate wire gauge - 14-16 AWG for motor power connections

Add fuses - 20-30A fuses recommended on VM power lines


### 🔧 Connection Photos & Diagrams
Add photos of your actual setup here:

ZS-X11H controller close-up showing pin labels

Arduino Mega with all connections

Complete wiring overview

Power supply connections

### 📁 PlatformIO Project Structure
text
mirai-hoverboard-motor-control/
├── include/
│   ├── config.h
│   ├── motor_control.h
│   ├── pid_control.h
│   └── communication.h
├── lib/
│   └── README  
├── src/
│   ├── main.cpp
│   ├── motor_control.cpp
│   ├── pid_control.cpp
│   └── communication.cpp
├── test/
│   └── test_connections.py
├── platformio.ini
└── README.md


#### ⚙️ PlatformIO Configuration
platformio.ini
ini
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

## 🧪 Testing Procedure

### 1. Build and Upload
```bash
# Build the project
pio run

# Upload to Arduino Mega
pio run --target upload

# Monitor serial output
pio device monitor
2. Connection Verification Test
Before powering motors, test with this simple sketch:
```
```cpp
void setup() {
  Serial.begin(115200);
  pinMode(5, OUTPUT); pinMode(6, OUTPUT); pinMode(7, OUTPUT);
  pinMode(9, OUTPUT); pinMode(10, OUTPUT); pinMode(11, OUTPUT);
  Serial.println("Connection test: All pins set to OUTPUT");
}

void loop() {
  // Test each pin sequentially
  for (int pin = 5; pin <= 11; pin++) {
    if (pin != 8) { // Skip pin 8
      digitalWrite(pin, HIGH);
      Serial.print("Pin "); Serial.print(pin); Serial.println(" HIGH");
      delay(500);
      digitalWrite(pin, LOW);
    }
  }
}
```
### 2. Basic Functionality Test
#### Test these commands in sequence:

HELP - Show available commands

F - Move both motors forward

150 - Set speed to 150/255

SOFTBRAKE - Test soft braking

R - Move both motors reverse

HARDBRAKE - Test hard braking

COAST - Let motors free spin

E - Emergency stop

C - Clear emergency

D - Show diagnostics

### 3. Individual Motor Control Test
ML:100 - Motor L at speed 100

MR:200 - Motor R at speed 200

STATUS - Check individual motor status

### 4. ROS2 Simulation Test
Test ROS2-like commands:

ROS:FORWARD

ROS:SPEED:180

ROS:SOFTBRAKE

ROS:STATUS

# 🔌 ROS2 Integration Setup
Orange Pi Side Setup
```bash
# On Orange Pi Zero 2W
sudo apt update
sudo apt install ros-humble-rosserial-arduino ros-humble-rosserial

# Create ROS2 package
ros2 pkg create mirai_motor_control --build-type ament_cmake
```
# Serial Communication Setup
The code uses Serial1 (pins 18/19) for ROS2 communication:

Connect Orange Pi TX → Arduino Mega RX1 (pin 19)

Connect Orange Pi RX → Arduino Mega TX1 (pin 18)

Connect GND between both devices

# 📦 Production Deployment
### 1. Optimize Build Settings
ini
; platformio.ini optimization for production
build_flags = 
    -D ROS2_SERIAL_BAUDRATE=115200
    -Os
    -flto
### 2. Create Deployment Script
bash
#!/bin/bash
# deploy-hoverboard-motors.sh

echo "🔨 Building MIRAI Hoverboard Motor Controller..."
pio run

echo "📤 Uploading to Arduino Mega..."
pio run --target upload

echo "✅ Deployment complete!"
echo "📋 Serial monitor: pio device monitor"

## 🚨 Troubleshooting Common Issues
- Motors not moving?

Check all GND connections are common

Verify 24-36V power supply is working

Test with multimeter for voltage at VM pins

- Erratic motor behavior?

Ensure all connections are secure

Check for loose hall sensor connections

Verify PWM pins are correctly configured

- Controllers overheating?

Add heatsinks to ZS-X11H controllers

Ensure adequate airflow

Reduce load or use higher current rating controllers

- Serial communication issues?

Verify baud rate matches (115200)

Check TX/RX connections are not reversed

Ensure common ground between all devices

# 📊 Expected Performance
Speed Range: 0-255 PWM (approximately 0-300 RPM for hoverboard motors)

Current Draw: 5-20A per motor under load

Response Time: <100ms for speed changes

Braking Distance: 0.5-2m depending on speed and braking mode

Remember to add actual photos of your setup to this documentation for future reference!