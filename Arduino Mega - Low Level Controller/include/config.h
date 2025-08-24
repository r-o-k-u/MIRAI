#ifndef CONFIG_H
#define CONFIG_H

// ======================
// Hardware Configuration
// ======================
// Left Motor Pins
#define ENA_L_PIN 5     // PWM speed control left motor
#define IN1_L_PIN 6     // Direction control 1 left motor
#define IN2_L_PIN 7     // Direction control 2 left motor
#define HALL_L_PIN 2    // Hall sensor left motor (Interrupt)

// Right Motor Pins
#define ENA_R_PIN 9     // PWM speed control right motor
#define IN1_R_PIN 10    // Direction control 1 right motor
#define IN2_R_PIN 11    // Direction control 2 right motor
#define HALL_R_PIN 3    // Hall sensor right motor (Interrupt)

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

#endif