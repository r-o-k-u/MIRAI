/**
 * Communication functions implementation - FIXED VERSION
 * Updated for ZS-X11H Motor Controllers with PID control
 */

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"
#include "communication.h"
#include "pid_control.h"

// Global variables
extern MotorState motorL;
extern MotorState motorR;
extern bool emergency_stop;
extern bool soft_brake_active;
extern bool hard_brake_active;
extern bool ros2_connected;
extern unsigned long last_heartbeat;
extern String inputString;
extern boolean stringComplete;

// PID controllers (declared in main.cpp)
// extern PIDController pidL;
// extern PIDController pidR;

void processSerialCommand(String command)
{
  command.trim();
  command.toUpperCase();

  if (command.length() == 0)
  {
    return;
  }

  if (emergency_stop && command != "C" && command != "CLEAR")
  {
    Serial.println("🚨 EMERGENCY STOP ACTIVE - Use 'C' to clear");
    return;
  }

  if (command == "F" || command == "FORWARD")
  {
    setMotorForward(1);
    setMotorForward(2);
    motorL.direction = "FORWARD";
    motorR.direction = "FORWARD";
    motorL.target_speed = motorL.current_speed > 0 ? motorL.current_speed : 150;
    motorR.target_speed = motorR.current_speed > 0 ? motorR.current_speed : 150;
    Serial.println("✅ Both motors FORWARD | Speed: " + String(motorL.target_speed));
  }
  else if (command == "R" || command == "REVERSE")
  {
    setMotorReverse(1);
    setMotorReverse(2);
    motorL.direction = "REVERSE";
    motorR.direction = "REVERSE";
    motorL.target_speed = motorL.current_speed > 0 ? motorL.current_speed : 150;
    motorR.target_speed = motorR.current_speed > 0 ? motorR.current_speed : 150;
    Serial.println("✅ Both motors REVERSE | Speed: " + String(motorL.target_speed));
  }
  else if (command == "S" || command == "STOP")
  {
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    Serial.println("✅ Stopping both motors");
  }
  else if (command == "COAST")
  {
    coastMotor(1);
    coastMotor(2);
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    motorL.current_speed = 0;
    motorR.current_speed = 0;
    Serial.println("✅ Motors coasting (free spin)");
  }
  else if (command == "SOFTBRAKE" || command == "SB")
  {
    activateSoftBrake();
    Serial.println("✅ Soft brake activated");
  }
  else if (command == "HARDBRAKE" || command == "HB")
  {
    activateHardBrake();
    Serial.println("✅ Hard brake activated");
  }
  else if (command == "E" || command == "EMERGENCY")
  {
    emergencyStop();
    Serial.println("🚨 EMERGENCY STOP ACTIVATED");
  }
  else if (command == "C" || command == "CLEAR")
  {
    clearEmergency();
    Serial.println("✅ Emergency cleared");
  }
  else if (command == "D" || command == "DIAG")
  {
    printDiagnostics();
  }
  else if (command == "HELP" || command == "?")
  {
    printHelp();
  }
  else if (command == "STATUS")
  {
    Serial.println("📊 Motor L: " + motorL.direction + " at " + String(motorL.current_speed) + "/255");
    Serial.println("📊 Motor R: " + motorR.direction + " at " + String(motorR.current_speed) + "/255");
    Serial.println("📊 Motor L RPM: " + String(motorL.rpm) + " | MPH: " + String(motorL.mph) + " | KPH: " + String(motorL.kph));
    Serial.println("📊 Motor R RPM: " + String(motorR.rpm) + " | MPH: " + String(motorR.mph) + " | KPH: " + String(motorR.kph));
    
    // Show PID status
    Serial.println(getPIDStatus(pidL));
    Serial.println(getPIDStatus(pidR));
  }
  else if (command.startsWith("ML:"))
  {
    String speedStr = command.substring(3);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorL.target_speed = speed;
        Serial.println("✅ Motor L speed set to: " + String(speed));
      }
    }
  }
  else if (command.startsWith("MR:"))
  {
    String speedStr = command.substring(3);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorR.target_speed = speed;
        Serial.println("✅ Motor R speed set to: " + String(speed));
      }
    }
  }
  else if (command.startsWith("BOTH:"))
  {
    String speedStr = command.substring(5);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorL.target_speed = speed;
        motorR.target_speed = speed;
        Serial.println("✅ Both motors speed set to: " + String(speed));
      }
    }
  }
  else if (isNumeric(command))
  {
    int speed = command.toInt();
    if (speed >= 0 && speed <= 255)
    {
      motorL.target_speed = speed;
      motorR.target_speed = speed;
      Serial.println("✅ Both motors speed set to: " + String(speed));
    }
    else
    {
      Serial.println("❌ Speed must be 0-255");
    }
  }
  else if (command.startsWith("ROS:"))
  {
    processROSCommand(command);
  }
  else if (command.startsWith("PID"))
  {
    processPIDCommand(command);
  }
  else
  {
    Serial.println("❌ Unknown command: '" + command + "'");
    Serial.println("💡 Type 'HELP' for available commands");
  }
}

void processROSCommand(String command)
{
  Serial.print("📡 ROS2 Command: ");
  Serial.println(command);

  // Update connection status
  last_heartbeat = millis();
  if (!ros2_connected)
  {
    ros2_connected = true;
    Serial.println("✅ ROS2 connected");
  }

  // Parse ROS2 commands
  if (command.startsWith("ROS:SPEED:"))
  {
    String speedStr = command.substring(10);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorL.target_speed = speed;
        motorR.target_speed = speed;
        Serial1.println("ACK:SPEED:" + String(speed));
      }
    }
  }
  else if (command.startsWith("ROS:ML:"))
  {
    String speedStr = command.substring(7);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorL.target_speed = speed;
        Serial1.println("ACK:ML:" + String(speed));
      }
    }
  }
  else if (command.startsWith("ROS:MR:"))
  {
    String speedStr = command.substring(7);
    if (isNumeric(speedStr))
    {
      int speed = speedStr.toInt();
      if (speed >= 0 && speed <= 255)
      {
        motorR.target_speed = speed;
        Serial1.println("ACK:MR:" + String(speed));
      }
    }
  }
  else if (command == "ROS:FORWARD")
  {
    setMotorForward(1);
    setMotorForward(2);
    motorL.direction = "FORWARD";
    motorR.direction = "FORWARD";
    Serial1.println("ACK:FORWARD");
  }
  else if (command == "ROS:REVERSE")
  {
    setMotorReverse(1);
    setMotorReverse(2);
    motorL.direction = "REVERSE";
    motorR.direction = "REVERSE";
    Serial1.println("ACK:REVERSE");
  }
  else if (command == "ROS:STOP")
  {
    motorL.target_speed = 0;
    motorR.target_speed = 0;
    Serial1.println("ACK:STOP");
  }
  else if (command == "ROS:SOFTBRAKE")
  {
    activateSoftBrake();
    Serial1.println("ACK:SOFTBRAKE");
  }
  else if (command == "ROS:HARDBRAKE")
  {
    activateHardBrake();
    Serial1.println("ACK:HARDBRAKE");
  }
  else if (command == "ROS:STATUS")
  {
    Serial1.println("STATUS:ML:" + motorL.direction + ":" + String(motorL.current_speed) + ":" + String(motorL.rpm));
    Serial1.println("STATUS:MR:" + motorR.direction + ":" + String(motorR.current_speed) + ":" + String(motorR.rpm));
  }
  else if (command == "ROS:HEARTBEAT")
  {
    Serial1.println("ACK:HEARTBEAT");
  }
  else if (command.startsWith("ROS:PID:"))
  {
    // ROS2 PID control commands
    String pidCmd = command.substring(8);
    if (pidCmd == "STATUS")
    {
      Serial1.println("PID_STATUS:" + getPIDStatus(pidL));
      Serial1.println("PID_STATUS:" + getPIDStatus(pidR));
    }
  }
}

// Process PID-specific commands
void processPIDCommand(String command)
{
  command.trim();
  command.toUpperCase();

  if (command == "PID" || command == "PIDSTATUS")
  {
    Serial.println(getPIDStatus(pidL));
    Serial.println(getPIDStatus(pidR));
  }
  else if (command.startsWith("PIDL:"))
  {
    String params = command.substring(5);
    if (params == "RESET")
    {
      resetPID(pidL);
      Serial.println("✅ Left PID reset");
    }
    else
    {
      processPIDTuning(params, pidL, "Left");
    }
  }
  else if (command.startsWith("PIDR:"))
  {
    String params = command.substring(5);
    if (params == "RESET")
    {
      resetPID(pidR);
      Serial.println("✅ Right PID reset");
    }
    else
    {
      processPIDTuning(params, pidR, "Right");
    }
  }
  else if (command.startsWith("PIDBOTH:"))
  {
    String params = command.substring(8);
    if (params == "RESET")
    {
      resetPID(pidL);
      resetPID(pidR);
      Serial.println("✅ Both PIDs reset");
    }
    else
    {
      processPIDTuning(params, pidL, "Left");
      processPIDTuning(params, pidR, "Right");
      Serial.println("✅ Both PIDs tuned with: " + params);
    }
  }
  else
  {
    Serial.println("❌ Unknown PID command: '" + command + "'");
    printPIDHelp();
  }
}

// Process PID tuning parameters
void processPIDTuning(String params, PIDController &pid, const String &name)
{
  int firstComma = params.indexOf(',');
  int secondComma = params.indexOf(',', firstComma + 1);
  int thirdComma = params.indexOf(',', secondComma + 1);

  if (firstComma != -1 && secondComma != -1 && thirdComma != -1)
  {
    String kpStr = params.substring(0, firstComma);
    String kiStr = params.substring(firstComma + 1, secondComma);
    String kdStr = params.substring(secondComma + 1, thirdComma);
    String maxiStr = params.substring(thirdComma + 1);

    if (isNumeric(kpStr) && isNumeric(kiStr) && isNumeric(kdStr) && isNumeric(maxiStr))
    {
      float kp = kpStr.toFloat();
      float ki = kiStr.toFloat();
      float kd = kdStr.toFloat();
      float maxi = maxiStr.toFloat();

      tunePID(pid, kp, ki, kd, maxi);
      Serial.println("✅ " + name + " PID tuned: Kp=" + String(kp, 3) +
                     ", Ki=" + String(ki, 3) + ", Kd=" + String(kd, 3) +
                     ", MaxI=" + String(maxi, 1));
    }
    else
    {
      Serial.println("❌ Invalid PID parameters. Use: Kp,Ki,Kd,MaxI");
    }
  }
  else
  {
    Serial.println("❌ Invalid PID format. Use: Kp,Ki,Kd,MaxI");
  }
}

bool isNumeric(String str)
{
  if (str.length() == 0)
    return false;
  for (byte i = 0; i < str.length(); i++)
  {
    if (!isDigit(str.charAt(i)))
    {
      return false;
    }
  }
  return true;
}

// Print PID-specific help
void printPIDHelp()
{
  Serial.println("\n🎛️  PID Control Commands:");
  Serial.println("  PID, PIDSTATUS       - Show current PID status");
  Serial.println("  PIDL:RESET           - Reset Left PID controller");
  Serial.println("  PIDR:RESET           - Reset Right PID controller");
  Serial.println("  PIDBOTH:RESET        - Reset both PID controllers");
  Serial.println("  PIDL:Kp,Ki,Kd,MaxI   - Tune Left PID parameters");
  Serial.println("  PIDR:Kp,Ki,Kd,MaxI   - Tune Right PID parameters");
  Serial.println("  PIDBOTH:Kp,Ki,Kd,MaxI - Tune both PID parameters");
  Serial.println("  Example: PIDL:0.15,0.7,0.001,50");
  Serial.println();
}

void printDiagnostics()
{
  Serial.println("\n===== 🤖 MIRAI HOVERBOARD MOTOR DIAGNOSTICS =====");
  Serial.println("Board: Arduino Mega/Nano with ZS-X11H Controllers");
  Serial.println("Motors: 2x Hoverboard Brushless DC with PID");
  Serial.println("----------------------------------------");
  Serial.println("Motor L Status:");
  Serial.println("  Direction: " + motorL.direction);
  Serial.println("  Speed: " + String(motorL.current_speed) + "/255");
  Serial.println("  Target: " + String(motorL.target_speed) + "/255");
  Serial.println("  RPM: " + String(motorL.rpm));
  Serial.println("  MPH: " + String(motorL.mph));
  Serial.println("  KPH: " + String(motorL.kph));
  Serial.println("  Pulses: " + String(motorL.pulse_count));
  Serial.println("  Braking: " + String(motorL.is_braking ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("Motor R Status:");
  Serial.println("  Direction: " + motorR.direction);
  Serial.println("  Speed: " + String(motorR.current_speed) + "/255");
  Serial.println("  Target: " + String(motorR.target_speed) + "/255");
  Serial.println("  RPM: " + String(motorR.rpm));
  Serial.println("  MPH: " + String(motorR.mph));
  Serial.println("  KPH: " + String(motorR.kph));
  Serial.println("  Pulses: " + String(motorR.pulse_count));
  Serial.println("  Braking: " + String(motorR.is_braking ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("System Status:");
  Serial.println("  Emergency Stop: " + String(emergency_stop ? "ACTIVE" : "INACTIVE"));
  Serial.println("  Soft Brake: " + String(soft_brake_active ? "ACTIVE" : "INACTIVE"));
  Serial.println("  Hard Brake: " + String(hard_brake_active ? "ACTIVE" : "INACTIVE"));
  Serial.println("  ROS2 Connected: " + String(ros2_connected ? "YES" : "NO"));
  Serial.println("----------------------------------------");
  Serial.println("PID Status:");
  Serial.println("  " + getPIDStatus(pidL));
  Serial.println("  " + getPIDStatus(pidR));
  Serial.println("----------------------------------------");
  Serial.println("Pin States:");
  Serial.println("  LEFT_PWM (Pin " + String(LEFT_PWM_PIN) + "): " + String(analogRead(LEFT_PWM_PIN)));
  Serial.println("  LEFT_BRAKE (Pin " + String(LEFT_BRAKE_PIN) + "): " + String(digitalRead(LEFT_BRAKE_PIN)));
  Serial.println("  LEFT_DIR (Pin " + String(LEFT_DIR_PIN) + "): " + String(digitalRead(LEFT_DIR_PIN)));
  Serial.println("  RIGHT_PWM (Pin " + String(RIGHT_PWM_PIN) + "): " + String(analogRead(RIGHT_PWM_PIN)));
  Serial.println("  RIGHT_BRAKE (Pin " + String(RIGHT_BRAKE_PIN) + "): " + String(digitalRead(RIGHT_BRAKE_PIN)));
  Serial.println("  RIGHT_DIR (Pin " + String(RIGHT_DIR_PIN) + "): " + String(digitalRead(RIGHT_DIR_PIN)));
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
  Serial.println("  PID           - PID control commands (type 'PID' for help)");
  Serial.println("  HELP, ?       - Show this help");
  Serial.println("  ROS:COMMAND   - Simulate ROS2 command");
  Serial.println();
}

// void serialEvent()
// {
//   while (Serial.available())
//   {
//     char inChar = (char)Serial.read();
//     if (inChar == '\n')
//     {
//       stringComplete = true;
//     }
//     else
//     {
//       inputString += inChar;
//     }
//   }
// }