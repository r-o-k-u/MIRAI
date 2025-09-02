#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <Arduino.h>

// Motor state tracking structure
struct MotorState {
  int current_speed;
  int target_speed;
  String direction;
  bool is_braking;
  unsigned long brake_start_time;
  volatile int pulse_count;
  float pulses_per_rotation;
  double rpm;
  double mph;
  double kph;
};

// Global variables (extern declarations - NO DEFINITIONS HERE)
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
int calculateBrakeSpeed(int motor_num);
void blinkStatusLED(int times, int delay_ms);

// Speed measurement functions
void readSpeed(int motor_num);
void writeToSerial();

// Hall sensor interrupt handlers
void recordPulseL();
void recordPulseR();

#endif