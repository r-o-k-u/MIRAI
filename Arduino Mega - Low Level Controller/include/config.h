#ifndef CONFIG_H
#define CONFIG_H

// ======================
// Hardware Configuration
// ======================

// ======================
// Hardware Configuration for ZS-X11H
// ======================
// Left Motor Pins
#define LEFT_PWM_PIN     10   // P pin (Red) - PWM control
#define LEFT_SPEED_PIN   11   // S pin (Yellow) - Speed control (input)
#define LEFT_BRAKE_PIN   5    // BRK pin (Blue) - Brake control
#define LEFT_DIR_PIN     4    // DIR pin (Orange) - Direction control

// Right Motor Pins
#define RIGHT_PWM_PIN    9    // P pin (Red) - PWM control
#define RIGHT_SPEED_PIN  12   // S pin (Yellow) - Speed control (input)
#define RIGHT_BRAKE_PIN  3    // BRK pin (Blue) - Brake control
#define RIGHT_DIR_PIN    2    // DIR pin (Orange) - Direction control

#define STATUS_LED 13   // Built-in LED for status

// ======================
// Motor Specifications
// ======================
#define PULSES_PER_ROTATION_L 44.0  // Left motor pulses per rotation
#define PULSES_PER_ROTATION_R 45.0  // Right motor pulses per rotation
#define MAX_PWM 255                 // Maximum PWM value
#define MIN_PWM 0                   // Minimum PWM value

// ======================
// PID Control Settings
// ======================
#define KP 0.15         // Proportional gain
#define KI 0.7          // Integral gain
#define KD 0.001        // Derivative gain
#define MAX_I_SUM 50    // Maximum integral sum

// ======================
// Braking Settings
// ======================
#define BRAKE_DECAY_RATE 15        // Speed reduction per brake cycle
#define BRAKE_CYCLE_DELAY 30       // ms between brake steps
#define SOFT_BRAKE_TIME 1000       // Time for soft brake to complete (ms)

// ======================
// Communication Settings
// ======================
#define SERIAL_BAUDRATE 115200
#define ROS2_BAUDRATE 115200
#define HEARTBEAT_TIMEOUT 2000     // 2 second timeout

// ======================
// Speed Calculation Constants
// ======================
#define SPEED_TIMEOUT 500000       // Time used to determine wheel is not spinning (µs)
#define UPDATE_TIME 500            // Time used to output serial data (ms)
#define WHEEL_DIAMETER_IN 6.5      // Motor wheel diameter (inches)
#define WHEEL_CIRCUMFERENCE_IN 22.25 // Motor wheel circumference (inches)
#define WHEEL_DIAMETER_CM 16.5     // Motor wheel diameter (centimeters)
#define WHEEL_CIRCUMFERENCE_CM 56.5 // Motor wheel circumference (centimeters)

// ======================
// Communication Settings
// ======================
#define SERIAL_BAUDRATE 115200
#define ROS2_BAUDRATE 115200
#define HEARTBEAT_TIMEOUT 2000     // 2 second timeout

#endif