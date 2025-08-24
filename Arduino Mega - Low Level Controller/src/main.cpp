/**
 * MIRAI Dual Hoverboard Motor Controller - ROS2 Compatible
 * PlatformIO Implementation for Arduino Mega with PID Control
 * 
 * Main application file
 */

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"
#include "pid_control.h"
#include "communication.h"

// Initialize global variables
MotorState motorL = {0, 0, "STOPPED", false, 0, 0, PULSES_PER_ROTATION_L};
MotorState motorR = {0, 0, "STOPPED", false, 0, 0, PULSES_PER_ROTATION_R};
bool emergency_stop = false;
bool soft_brake_active = false;
bool hard_brake_active = false;
bool ros2_connected = false;
unsigned long last_heartbeat = 0;
String inputString = "";
boolean stringComplete = false;

// PID controllers
PIDController pidL, pidR;

// Timing variables
unsigned long lastBrakeUpdate = 0;
unsigned long lastSpeedUpdate = 0;
unsigned long lastPIDUpdate = 0;

void setup() {
  // Initialize motor control pins
  pinMode(ENA_L_PIN, OUTPUT);
  pinMode(IN1_L_PIN, OUTPUT);
  pinMode(IN2_L_PIN, OUTPUT);
  
  pinMode(ENA_R_PIN, OUTPUT);
  pinMode(IN1_R_PIN, OUTPUT);
  pinMode(IN2_R_PIN, OUTPUT);
  
  pinMode(STATUS_LED, OUTPUT);
  
  // Initialize hall sensor interrupts
  pinMode(HALL_L_PIN, INPUT);
  pinMode(HALL_R_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(HALL_L_PIN), recordPulseL, RISING);
  attachInterrupt(digitalPinToInterrupt(HALL_R_PIN), recordPulseR, RISING);
  
  // Initialize serial communication
  Serial.begin(SERIAL_BAUDRATE);
  Serial1.begin(ROS2_BAUDRATE);
  
  while (!Serial) {
    delay(10);
  }
  
  // Initialize PID controllers
  initPID(pidL, KP, KI, KD, MAX_I_SUM);
  initPID(pidR, KP, KI, KD, MAX_I_SUM);
  
  // Startup sequence
  blinkStatusLED(3, 200);
  coastMotor(1);
  coastMotor(2);
  
  Serial.println("==================================================");
  Serial.println("🤖 MIRAI Enhanced Dual Hoverboard Motor Controller");
  Serial.println("==================================================");
  Serial.println("Board: Arduino Mega 2560");
  Serial.println("Motors: 2x Recycled Hoverboard Motors with PID");
  Serial.println("Pulses/Rev - L: " + String(PULSES_PER_ROTATION_L) + " R: " + String(PULSES_PER_ROTATION_R));
  Serial.println("==================================================");
  Serial.println("Type 'HELP' for command list");
  Serial.println("==================================================");
}

void loop() {
  // Check for commands from primary serial
  if (stringComplete) {
    processSerialCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Check for ROS2 commands on Serial1
  if (Serial1.available() > 0) {
    String rosCommand = Serial1.readStringUntil('\n');
    rosCommand.trim();
    processROSCommand(rosCommand);
  }
  
  // Handle ROS2 connection timeout
  if (ros2_connected && millis() - last_heartbeat > HEARTBEAT_TIMEOUT) {
    Serial.println("⚠️  ROS2 connection timeout - safety stop activated");
    emergencyStop();
    ros2_connected = false;
    blinkStatusLED(5, 100);
  }
  
  // Update motor speeds with PID control (every 20ms)
  if (millis() - lastPIDUpdate >= 20) {
    float dt = (millis() - lastPIDUpdate) / 1000.0;
    
    // Calculate RPM from pulse counts
    float rpmL = (motorL.pulse_count / motorL.pulses_per_rotation) * (60000.0 / dt);
    float rpmR = (motorR.pulse_count / motorR.pulses_per_rotation) * (60000.0 / dt);
    
    // Reset pulse counts
    motorL.pulse_count = 0;
    motorR.pulse_count = 0;
    
    // Compute PID outputs
    float pidOutputL = computePID(pidL, motorL.target_speed, rpmL, dt);
    float pidOutputR = computePID(pidR, motorR.target_speed, rpmR, dt);
    
    // Apply PID outputs to motors
    analogWrite(ENA_L_PIN, constrain(pidOutputL, MIN_PWM, MAX_PWM));
    analogWrite(ENA_R_PIN, constrain(pidOutputR, MIN_PWM, MAX_PWM));
    
    lastPIDUpdate = millis();
  }
  
  // Handle braking (every 30ms)
  if (millis() - lastBrakeUpdate >= 30) {
    if (soft_brake_active || hard_brake_active) {
      updateBraking();
    }
    lastBrakeUpdate = millis();
  }
  
  // Status LED
  static unsigned long lastBlink = 0;
  if (ros2_connected) {
    digitalWrite(STATUS_LED, HIGH);
  } else if (emergency_stop) {
    // Rapid blink for emergency stop
    if (millis() - lastBlink > 200) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      lastBlink = millis();
    }
  } else {
    // Slow blink in standalone mode
    if (millis() - lastBlink > 1000) {
      digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
      lastBlink = millis();
    }
  }
}