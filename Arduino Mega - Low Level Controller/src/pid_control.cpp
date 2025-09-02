/**
 * PID Control functions implementation
 * Updated for ZS-X11H Motor Controllers with RPM-based control
 * Added serial monitoring and control capabilities
 */

#include <Arduino.h>
#include "pid_control.h"

void initPID(PIDController& pid, float kp, float ki, float kd, float max_i, const String& name) {
  pid.kp = kp;
  pid.ki = ki;
  pid.kd = kd;
  pid.max_integral = max_i;
  pid.error = 0;
  pid.prev_error = 0;
  pid.integral = 0;
  pid.derivative = 0;
  pid.output = 0;
  pid.setpoint = 0;
  pid.input = 0;
  pid.name = name;
}

float computePID(PIDController& pid, float setpoint, float input, float dt) {
  // Update setpoint and input
  pid.setpoint = setpoint;
  pid.input = input;
  
  // Calculate error - convert RPM error to PWM correction
  // Scale factor: 255 PWM / ~300 RPM (typical max RPM for hoverboard motors)
  const float rpm_to_pwm_scale = 255.0 / 300.0;
  pid.error = (setpoint - input) * rpm_to_pwm_scale;
  
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
  
  // Constrain output to valid PWM range
  pid.output = constrain(pid.output, 0, 255);
  
  return pid.output;
}

void resetPID(PIDController& pid) {
  pid.error = 0;
  pid.prev_error = 0;
  pid.integral = 0;
  pid.derivative = 0;
  pid.output = 0;
  pid.setpoint = 0;
  pid.input = 0;
}

// Get PID status for diagnostics
String getPIDStatus(const PIDController& pid) {
  String status = "🔧 " + pid.name + " PID: ";
  status += "Kp=" + String(pid.kp, 3);
  status += " Ki=" + String(pid.ki, 3);
  status += " Kd=" + String(pid.kd, 3);
  status += " | SP=" + String(pid.setpoint, 1);
  status += " RPM=" + String(pid.input, 1);
  status += " PWM=" + String(pid.output, 1);
  status += " Err=" + String(pid.error, 1);
  status += " I=" + String(pid.integral, 1);
  status += " D=" + String(pid.derivative, 1);
  return status;
}

// Tune PID parameters dynamically
void tunePID(PIDController& pid, float kp, float ki, float kd, float max_i) {
  pid.kp = kp;
  pid.ki = ki;
  pid.kd = kd;
  pid.max_integral = max_i;
  // Reset integral to prevent windup with new parameters
  pid.integral = 0;
}

// Adaptive PID for varying load conditions
float computeAdaptivePID(PIDController& pid, float setpoint, float input, float dt, float load_factor) {
  // Adjust PID gains based on load factor (0.5-2.0)
  float adaptive_kp = pid.kp * load_factor;
  float adaptive_ki = pid.ki * load_factor;
  float adaptive_kd = pid.kd / load_factor; // Reduce derivative gain under heavy load
  
  // Calculate error
  pid.error = setpoint - input;
  
  // Proportional term
  float proportional = adaptive_kp * pid.error;
  
  // Integral term with anti-windup
  pid.integral += pid.error * dt;
  pid.integral = constrain(pid.integral, -pid.max_integral, pid.max_integral);
  float integral = adaptive_ki * pid.integral;
  
  // Derivative term
  pid.derivative = (pid.error - pid.prev_error) / dt;
  float derivative = adaptive_kd * pid.derivative;
  
  // Store error for next iteration
  pid.prev_error = pid.error;
  
  // Compute total output
  pid.output = proportional + integral + derivative;
  
  // Constrain output to valid PWM range
  pid.output = constrain(pid.output, 0, 255);
  
  return pid.output;
}