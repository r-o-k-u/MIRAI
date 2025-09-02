#ifndef PID_CONTROL_H
#define PID_CONTROL_H

#include <Arduino.h>

// PID Controller structure
struct PIDController {
  float kp;           // Proportional gain
  float ki;           // Integral gain
  float kd;           // Derivative gain
  float max_integral; // Maximum integral windup
  float error;        // Current error
  float prev_error;   // Previous error
  float integral;     // Integral accumulator
  float derivative;   // Derivative term
  float output;       // Controller output
  float setpoint;     // Current setpoint (for diagnostics)
  float input;        // Current input (for diagnostics)
  String name;        // Controller name for identification
};

// Function declarations
void initPID(PIDController& pid, float kp, float ki, float kd, float max_i, const String& name);
float computePID(PIDController& pid, float setpoint, float input, float dt);
void resetPID(PIDController& pid);
String getPIDStatus(const PIDController& pid);
void tunePID(PIDController& pid, float kp, float ki, float kd, float max_i);
float computeAdaptivePID(PIDController& pid, float setpoint, float input, float dt, float load_factor);

#endif