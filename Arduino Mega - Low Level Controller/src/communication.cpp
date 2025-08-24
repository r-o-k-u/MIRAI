/**
 * Communication functions implementation - FIXED VERSION
 */

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"
#include "communication.h"

void processSerialCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command.length() == 0) {
    return;
  }
  
  if (emergency_stop && command != "C" && command != "CLEAR") {
    Serial.println("🚨 EMERGENCY STOP ACTIVE - Use 'C' to clear");
    return;
  }
  
  if (command == "F" || command == "FORWARD") {
    setMotorForward(1);
    setMotorForward(2);
    motorL.direction = "FORWARD";
    motorR.direction = "FORWARD";
    motorL.target_speed = motorL.current_speed > 0 ? motorL.current_speed : 150;
    motorR.target_speed = motorR.current_speed > 0 ? motorR.current_speed : 150;
    Serial.println("✅ Both motors FORWARD | Speed: " + String(motorL.target_speed));
  } 
  else if (command == "R" || command == "REVERSE") {
    setMotorReverse(1);
    setMotorReverse(2);
    motorL.direction = "REVERSE";
    motorR.direction = "REVERSE";
    motorL.target_speed = motorL.current_speed > 0 ? motorL.current_speed : 150;
    motorR.target_speed = motorR.current_speed > 0 ? motorR.current_speed : 150;
    Serial.println("✅ Both motors REVERSE | Speed: " + String(motorL.target_speed));
  } 
  else if (command == "S" || command == "STOP") {
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    Serial.println("✅ Stopping both motors");
  }
  else if (command == "COAST") {
    coastMotor(1);
    coastMotor(2);
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    motorL.current_speed = 0;
    motorR.current_speed = 0;
    Serial.println("✅ Motors coasting (free spin)");
  }
  else if (command == "SOFTBRAKE" || command == "SB") {
    activateSoftBrake();
    Serial.println("✅ Soft brake activated");
  }
  else if (command == "HARDBRAKE" || command == "HB") {
    activateHardBrake();
    Serial.println("✅ Hard brake activated");
  }
  else if (command == "E" || command == "EMERGENCY") {
    emergencyStop();
    Serial.println("🚨 EMERGENCY STOP ACTIVATED");
  }
  else if (command == "C" || command == "CLEAR") {
    clearEmergency();
    Serial.println("✅ Emergency cleared");
  }
  else if (command == "D" || command == "DIAG") {
    printDiagnostics();
  }
  else if (command == "HELP" || command == "?") {
    printHelp();
  }
  else if (command == "STATUS") {
    Serial.println("📊 Motor L: " + motorL.direction + " at " + String(motorL.current_speed) + "/255");
    Serial.println("📊 Motor R: " + motorR.direction + " at " + String(motorR.current_speed) + "/255");
  }
  else if (command.startsWith("ML:")) {
    String speedStr = command.substring(3);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorL.target_speed = speed;
        Serial.println("✅ Motor L speed set to: " + String(speed));
      }
    }
  }
  else if (command.startsWith("MR:")) {
    String speedStr = command.substring(3);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorR.target_speed = speed;
        Serial.println("✅ Motor R speed set to: " + String(speed));
      }
    }
  }
  else if (command.startsWith("BOTH:")) {
    String speedStr = command.substring(5);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorL.target_speed = speed;
        motorR.target_speed = speed;
        Serial.println("✅ Both motors speed set to: " + String(speed));
      }
    }
  }
  else if (isNumeric(command)) {
    int speed = command.toInt();
    if (speed >= 0 && speed <= 255) {
      motorL.target_speed = speed;
      motorR.target_speed = speed;
      Serial.println("✅ Both motors speed set to: " + String(speed));
    } else {
      Serial.println("❌ Speed must be 0-255");
    }
  }
  else if (command.startsWith("ROS:")) {
    processROSCommand(command);
  }
  else {
    Serial.println("❌ Unknown command: '" + command + "'");
    Serial.println("💡 Type 'HELP' for available commands");
  }
}

void processROSCommand(String command) {
  Serial.print("📡 ROS2 Command: ");
  Serial.println(command);
  
  // Update connection status
  last_heartbeat = millis();
  if (!ros2_connected) {
    ros2_connected = true;
    Serial.println("✅ ROS2 connected");
  }
  
  // Parse ROS2 commands
  if (command.startsWith("ROS:SPEED:")) {
    String speedStr = command.substring(10);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorL.target_speed = speed;
        motorR.target_speed = speed;
        Serial1.println("ACK:SPEED:" + String(speed));
      }
    }
  }
  else if (command.startsWith("ROS:ML:")) {
    String speedStr = command.substring(7);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorL.target_speed = speed;
        Serial1.println("ACK:ML:" + String(speed));
      }
    }
  }
  else if (command.startsWith("ROS:MR:")) {
    String speedStr = command.substring(7);
    if (isNumeric(speedStr)) {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255) {
        motorR.target_speed = speed;
        Serial1.println("ACK:MR:" + String(speed));
      }
    }
  }
  else if (command == "ROS:FORWARD") {
    setMotorForward(1);
    setMotorForward(2);
    motorL.direction = "FORWARD";
    motorR.direction = "FORWARD";
    Serial1.println("ACK:FORWARD");
  }
  else if (command == "ROS:REVERSE") {
    setMotorReverse(1);
    setMotorReverse(2);
    motorL.direction = "REVERSE";
    motorR.direction = "REVERSE";
    Serial1.println("ACK:REVERSE");
  }
  else if (command == "ROS:STOP") {
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    Serial1.println("ACK:STOP");
  }
  else if (command == "ROS:SOFTBRAKE") {
    activateSoftBrake();
    Serial1.println("ACK:SOFTBRAKE");
  }
  else if (command == "ROS:HARDBRAKE") {
    activateHardBrake();
    Serial1.println("ACK:HARDBRAKE");
  }
  else if (command == "ROS:STATUS") {
    Serial1.println("STATUS:ML:" + motorL.direction + ":" + String(motorL.current_speed));
    Serial1.println("STATUS:MR:" + motorR.direction + ":" + String(motorR.current_speed));
  }
  else if (command == "ROS:HEARTBEAT") {
    Serial1.println("ACK:HEARTBEAT");
  }
}

bool isNumeric(String str) {
  if (str.length() == 0) return false;
  for (byte i = 0; i < str.length(); i++) {
    if (!isDigit(str.charAt(i))) {
      return false;
    }
  }
  return true;
}

void printDiagnostics() {
  Serial.println("\n===== 🤖 MIRAI HOVERBOARD MOTOR DIAGNOSTICS =====");
  Serial.println("Board: Arduino Mega 2560");
  Serial.println("Motors: 2x Hoverboard Brushless DC with PID");
  Serial.println("----------------------------------------");
  Serial.println("Motor L Status:");
  Serial.println("  Direction: " + motorL.direction);
  Serial.println("  Speed: " + String(motorL.current_speed) + "/255");
  Serial.println("  Target: " + String(motorL.target_speed) + "/255");
  Serial.println("  Pulses: " + String(motorL.pulse_count));
  Serial.println("  Braking: " + String(motorL.is_braking ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("Motor R Status:");
  Serial.println("  Direction: " + motorR.direction);
  Serial.println("  Speed: " + String(motorR.current_speed) + "/255");
  Serial.println("  Target: " + String(motorR.target_speed) + "/255");
  Serial.println("  Pulses: " + String(motorR.pulse_count));
  Serial.println("  Braking: " + String(motorR.is_braking ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("System Status:");
  Serial.println("  Emergency Stop: " + String(emergency_stop ? "ACTIVE" : "INACTIVE"));
  Serial.println("  Soft Brake: " + String(soft_brake_active ? "ACTIVE" : "INACTIVE"));
  Serial.println("  Hard Brake: " + String(hard_brake_active ? "ACTIVE" : "INACTIVE"));
  Serial.println("  ROS2 Connected: " + String(ros2_connected ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("Pin States:");
  Serial.println("  ENA_L (Pin 5): " + String(analogRead(ENA_L_PIN)));
  Serial.println("  IN1_L (Pin 6): " + String(digitalRead(IN1_L_PIN)));
  Serial.println("  IN2_L (Pin 7): " + String(digitalRead(IN2_L_PIN)));
  Serial.println("  ENA_R (Pin 9): " + String(analogRead(ENA_R_PIN)));
  Serial.println("  IN1_R (Pin 10): " + String(digitalRead(IN1_R_PIN)));
  Serial.println("  IN2_R (Pin 11): " + String(digitalRead(IN2_R_PIN)));
  Serial.println("========================================\n");
}

void printHelp() {
  Serial.println("\n📋 Available Commands:");
  Serial.println("  F, FORWARD    - Both motors forward");
  Serial.println("  R, REVERSE    - Both motors reverse");
  Serial.println("  S, STOP       - Stop both motors (coast)");
  Serial.println("  COAST         - Let motors free spin");
  Serial.println("  SOFTBRAKE, SB - Gradual soft braking");
  Serial.println("  HARDBRAKE, HB - Immediate hard braking");
  Serial.println("  0-255         - Set speed for both motors");
  Serial.println("  ML:0-255      - Set speed for motor L only");
  Serial.println("  MR:0-255      - Set speed for motor R only");
  Serial.println("  BOTH:0-255    - Set speed for both motors");
  Serial.println("  E, EMERGENCY  - Emergency stop");
  Serial.println("  C, CLEAR      - Clear emergency stop");
  Serial.println("  D, DIAG       - Show diagnostics");
  Serial.println("  STATUS        - Show current status");
  Serial.println("  HELP, ?       - Show this help");
  Serial.println("  ROS:COMMAND   - Simulate ROS2 command");
  Serial.println();
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}