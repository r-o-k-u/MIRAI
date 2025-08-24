#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <Arduino.h>

// Motor state tracking structure
struct MotorState {
  int current_speed;        // 0-255
  int target_speed;         // 0-255
  String direction;         // FORWARD, REVERSE, STOPPED
  bool is_braking;          // Braking in progress
  unsigned long brake_start_time;
  volatile int pulse_count; // Hall sensor pulse count
  float pulses_per_rotation;// Motor specific pulses per rotation
};

// Global variables
extern MotorState motorL;
extern MotorState motorR;
extern bool emergency_stop;
extern bool soft_brake_active;
extern bool hard_brake_active;

// Function declarations
void setMotorForward(int motor_num);
void setMotorReverse(int motor_num);
void stopMotor(int motor_num);
void coastMotor(int motor_num);
void setMotorSpeed(int motor_num, int speed);
void setBothMotorsSpeed(int speed);
void emergencyStop();
void activateSoftBrake();
void activateHardBrake();
void clearEmergency();
void updateBraking();
void updateMotorSpeeds();
int calculateBrakeSpeed(int motor_num);
void blinkStatusLED(int times, int delay_ms);

// Hall sensor interrupt handlers
void recordPulseL();
void recordPulseR();

#endif