/**
 * PID Control functions implementation
 */

#include <Arduino.h>
#include "pid_control.h"

void initPID(PIDController& pid, float kp, float ki, float kd, float max_i) {
  pid.kp = kp;
  pid.ki = ki;
  pid.kd = kd;
  pid.max_integral = max_i;
  pid.error = 0;
  pid.prev_error = 0;
  pid.integral = 0;
  pid.derivative = 0;
  pid.output = 0;
}

float computePID(PIDController& pid, float setpoint, float input, float dt) {
  // Calculate error
  pid.error = setpoint - input;
  
  // Proportional term
  float proportional = pid.kp * pid.error;
  
  // Integral term with anti-windup
  pid.integral += pid.error * dt;
  pid.integral = constrain(pid.integral, -pid.max_integral, pid.max_integral);
  float integral = pid.ki * pid.integral;
  
  // Derivative term
  pid.derivative = (pid.error - pid.prev_error) / dt;
  float derivative = pid.kd * pid.derivative;
  
  // Store error for next iteration
  pid.prev_error = pid.error;
  
  // Compute total output
  pid.output = proportional + integral + derivative;
  
  return pid.output;
}

void resetPID(PIDController& pid) {
  pid.error = 0;
  pid.prev_error = 0;
  pid.integral = 0;
  pid.derivative = 0;
  pid.output = 0;
}