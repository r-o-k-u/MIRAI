#ifndef PID_CONTROL_H
#define PID_CONTROL_H

#include <Arduino.h>

// PID control structure
struct PIDController {
  float kp, ki, kd;
  float error;
  float prev_error;
  float integral;
  float derivative;
  float output;
  float max_integral;
};

// Function declarations
void initPID(PIDController& pid, float kp, float ki, float kd, float max_i);
float computePID(PIDController& pid, float setpoint, float input, float dt);
void resetPID(PIDController& pid);

#endif