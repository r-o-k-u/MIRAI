/**
 * Enhanced Motor control functions implementation with Hall Sensors
 */

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"
// Global variables initialization
// MotorState motorL = {0, 0, "STOPPED", false, 0, 0, PULSES_PER_ROTATION_L, 0, 0, 0};
// MotorState motorR = {0, 0, "STOPPED", false, 0, 0, PULSES_PER_ROTATION_R, 0, 0, 0};
// bool emergency_stop = false;
// bool soft_brake_active = false;
// bool hard_brake_active = false;

// Hall sensor interrupt handlers
void recordPulseL() {
  motorL.pulse_count++;
}

void recordPulseR() {
  motorR.pulse_count++;
}

// Motor control functions implementation
void setMotorForward(int motor_num) {
  if (!emergency_stop) {
    if (motor_num == 1) { // Left motor
      digitalWrite(LEFT_DIR_PIN, HIGH);
      motorL.direction = "FORWARD";
    } else { // Right motor
      digitalWrite(RIGHT_DIR_PIN, HIGH);
      motorR.direction = "FORWARD";
    }
  }
}

void setMotorReverse(int motor_num) {
  if (!emergency_stop) {
    if (motor_num == 1) { // Left motor
      digitalWrite(LEFT_DIR_PIN, LOW);
      motorL.direction = "REVERSE";
    } else { // Right motor
      digitalWrite(RIGHT_DIR_PIN, LOW);
      motorR.direction = "REVERSE";
    }
  }
}

void stopMotor(int motor_num) {
  if (motor_num == 1) { // Left motor
    digitalWrite(LEFT_BRAKE_PIN, HIGH); // Active low, so HIGH engages brake
    analogWrite(LEFT_PWM_PIN, 0);
    motorL.current_speed = 0;
    motorL.target_speed = 0;
    motorL.direction = "STOPPED";
  } else { // Right motor
    digitalWrite(RIGHT_BRAKE_PIN, HIGH); // Active low, so HIGH engages brake
    analogWrite(RIGHT_PWM_PIN, 0);
    motorR.current_speed = 0;
    motorR.target_speed = 0;
    motorR.direction = "STOPPED";
  }
}

void coastMotor(int motor_num) {
  if (motor_num == 1) { // Left motor
    digitalWrite(LEFT_BRAKE_PIN, LOW); // Release brake
    analogWrite(LEFT_PWM_PIN, 0);
    motorL.current_speed = 0;
    motorL.direction = "COASTING";
  } else { // Right motor
    digitalWrite(RIGHT_BRAKE_PIN, LOW); // Release brake
    analogWrite(RIGHT_PWM_PIN, 0);
    motorR.current_speed = 0;
    motorR.direction = "COASTING";
  }
}

void setMotorSpeed(int motor_num, int speed) {
  if (!emergency_stop) {
    speed = constrain(speed, 0, 255);
    
    if (motor_num == 1) { // Left motor
      digitalWrite(LEFT_BRAKE_PIN, LOW); // Release brake
      analogWrite(LEFT_PWM_PIN, speed);
      motorL.current_speed = speed;
      motorL.target_speed = speed;
      if (motorL.direction == "STOPPED" || motorL.direction == "COASTING") {
        motorL.direction = "FORWARD"; // Default to forward when setting speed
        digitalWrite(LEFT_DIR_PIN, HIGH);
      }
    } else { // Right motor
      digitalWrite(RIGHT_BRAKE_PIN, LOW); // Release brake
      analogWrite(RIGHT_PWM_PIN, speed);
      motorR.current_speed = speed;
      motorR.target_speed = speed;
      if (motorR.direction == "STOPPED" || motorR.direction == "COASTING") {
        motorR.direction = "FORWARD"; // Default to forward when setting speed
        digitalWrite(RIGHT_DIR_PIN, HIGH);
      }
    }
  }
}

void setBothMotorsSpeed(int speed) {
  if (!emergency_stop) {
    setMotorSpeed(1, speed);
    setMotorSpeed(2, speed);
  }
}

void emergencyStop() {
  // Immediate stop for both motors
  stopMotor(1);
  stopMotor(2);
  motorL.current_speed = 0;
  motorR.current_speed = 0;
  motorL.target_speed = 0;
  motorR.target_speed = 0;
  motorL.is_braking = false;
  motorR.is_braking = false;
  soft_brake_active = false;
  hard_brake_active = false;
  emergency_stop = true;
}

void activateSoftBrake() {
  soft_brake_active = true;
  hard_brake_active = false;
  motorL.is_braking = true;
  motorR.is_braking = true;
  motorL.brake_start_time = millis();
  motorR.brake_start_time = millis();
}

void activateHardBrake() {
  hard_brake_active = true;
  soft_brake_active = false;
  motorL.is_braking = true;
  motorR.is_braking = true;
  
  // For hard brake, reverse the motors briefly then stop
  setMotorReverse(1);
  setMotorReverse(2);
  delay(100);
  stopMotor(1);
  stopMotor(2);
  
  motorL.current_speed = 0;
  motorR.current_speed = 0;
  motorL.target_speed = 0;
  motorR.target_speed = 0;
  motorL.is_braking = false;
  motorR.is_braking = false;
  hard_brake_active = false;
}

void clearEmergency() {
  emergency_stop = false;
  coastMotor(1);
  coastMotor(2);
}

void updateBraking() {
  if (soft_brake_active) {
    motorL.current_speed = calculateBrakeSpeed(1);
    motorR.current_speed = calculateBrakeSpeed(2);
    
    analogWrite(LEFT_PWM_PIN, motorL.current_speed);
    analogWrite(RIGHT_PWM_PIN, motorR.current_speed);
    
    // Check if braking is complete
    if (motorL.current_speed == 0 && motorR.current_speed == 0) {
      soft_brake_active = false;
      motorL.is_braking = false;
      motorR.is_braking = false;
      Serial.println("✅ Soft brake complete");
    }
  }
}

int calculateBrakeSpeed(int motor_num) {
  MotorState* motor = (motor_num == 1) ? &motorL : &motorR;
  unsigned long brake_time = millis() - motor->brake_start_time;
  float brake_progress = min(1.0, (float)brake_time / SOFT_BRAKE_TIME);
  
  // Exponential decay for smoother braking
  int new_speed = motor->target_speed * (1.0 - brake_progress * brake_progress);
  return max(0, new_speed);
}

void blinkStatusLED(int times, int delay_ms) {
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(delay_ms);
    digitalWrite(STATUS_LED, LOW);
    delay(delay_ms);
  }
}

// Reads the speed from the input pin and calculates RPM and MPH
void readSpeed(int motor_num) {
  static bool lastStateL = false;
  static bool lastStateR = false;
  static unsigned long last_uSL;
  static unsigned long last_uSR;
  static unsigned long timeout_uSL;
  static unsigned long timeout_uSR;

  MotorState* motor = (motor_num == 1) ? &motorL : &motorR;
  bool* lastState = (motor_num == 1) ? &lastStateL : &lastStateR;
  unsigned long* last_uS = (motor_num == 1) ? &last_uSL : &last_uSR;
  unsigned long* timeout_uS = (motor_num == 1) ? &timeout_uSL : &timeout_uSR;
  int speed_pin = (motor_num == 1) ? LEFT_SPEED_PIN : RIGHT_SPEED_PIN;

  // Read the current state of the input pin
  bool state = digitalRead(speed_pin);

  // Check if the pin has changed state
  if (state != *lastState) {
    // Calculate how long has passed since last transition
    unsigned long current_uS = micros();
    unsigned long elapsed_uS = current_uS - *last_uS;

    // Calculate the frequency of the input signal
    double period_uS = elapsed_uS * 2.0;
    double freq = (1 / period_uS) * 1E6;

    // Calculate the RPM (assuming 45 pulses per revolution)
    motor->rpm = freq / 45 * 60;

    // If RPM is excessively high then ignore it
    if (motor->rpm > 5000) motor->rpm = 0;

    // Calculate the miles per hour (mph) based on the wheel circumference
    motor->mph = (WHEEL_CIRCUMFERENCE_IN * motor->rpm * 60) / 63360; 
  
    // Calculate the kilometers per hour (kph) based on the wheel circumference
    motor->kph = (WHEEL_CIRCUMFERENCE_CM * motor->rpm * 60) / 100000; 

    // Save the last state and next timeout time
    *last_uS = current_uS;
    *timeout_uS = *last_uS + SPEED_TIMEOUT;
    *lastState = state;
  }
  // If too long has passed then the wheel has probably stopped
  else if (micros() > *timeout_uS) {
    motor->rpm = 0;
    motor->mph = 0;
    motor->kph = 0;
    *last_uS = micros();
  }
}

// Writes the RPM and MPH to the serial port at a set interval
void writeToSerial() {
  static unsigned long updateTime;
  
  if (millis() > updateTime) {
    // Write data to the serial port
    Serial.print("Left - ");
    Serial.print("RPM:"); Serial.print(motorL.rpm); Serial.print(" ");
    Serial.print("MPH:"); Serial.print(motorL.mph); Serial.print(" ");
    Serial.print("KPH:"); Serial.print(motorL.kph); Serial.print(" | ");
    
    Serial.print("Right - ");
    Serial.print("RPM:"); Serial.print(motorR.rpm); Serial.print(" ");
    Serial.print("MPH:"); Serial.print(motorR.mph); Serial.print(" ");
    Serial.print("KPH:"); Serial.println(motorR.kph);

    // Calculate next update time
    updateTime = millis() + UPDATE_TIME;
  }
}