/**
 * Enhanced Motor control functions implementation with Hall Sensors
 */

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"

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
      digitalWrite(IN1_L_PIN, HIGH);
      digitalWrite(IN2_L_PIN, LOW);
      motorL.direction = "FORWARD";
    } else { // Right motor
      digitalWrite(IN1_R_PIN, HIGH);
      digitalWrite(IN2_R_PIN, LOW);
      motorR.direction = "FORWARD";
    }
  }
}

void setMotorReverse(int motor_num) {
  if (!emergency_stop) {
    if (motor_num == 1) { // Left motor
      digitalWrite(IN1_L_PIN, LOW);
      digitalWrite(IN2_L_PIN, HIGH);
      motorL.direction = "REVERSE";
    } else { // Right motor
      digitalWrite(IN1_R_PIN, LOW);
      digitalWrite(IN2_R_PIN, HIGH);
      motorR.direction = "REVERSE";
    }
  }
}

void stopMotor(int motor_num) {
  if (motor_num == 1) { // Left motor
    digitalWrite(IN1_L_PIN, LOW);
    digitalWrite(IN2_L_PIN, LOW);
    analogWrite(ENA_L_PIN, 0);
    motorL.current_speed = 0;
  } else { // Right motor
    digitalWrite(IN1_R_PIN, LOW);
    digitalWrite(IN2_R_PIN, LOW);
    analogWrite(ENA_R_PIN, 0);
    motorR.current_speed = 0;
  }
}

void coastMotor(int motor_num) {
  if (motor_num == 1) { // Left motor
    analogWrite(ENA_L_PIN, 0);
    motorL.current_speed = 0;
  } else { // Right motor
    analogWrite(ENA_R_PIN, 0);
    motorR.current_speed = 0;
  }
}

void setMotorSpeed(int motor_num, int speed) {
  if (!emergency_stop) {
    if (motor_num == 1) { // Left motor
      motorL.target_speed = speed;
    } else { // Right motor
      motorR.target_speed = speed;
    }
  }
}

void setBothMotorsSpeed(int speed) {
  if (!emergency_stop) {
    motorL.target_speed = speed;
    motorR.target_speed = speed;
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
  stopMotor(1);
  stopMotor(2);
}

void updateBraking() {
  if (soft_brake_active) {
    motorL.current_speed = calculateBrakeSpeed(1);
    motorR.current_speed = calculateBrakeSpeed(2);
    
    analogWrite(ENA_L_PIN, motorL.current_speed);
    analogWrite(ENA_R_PIN, motorR.current_speed);
    
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