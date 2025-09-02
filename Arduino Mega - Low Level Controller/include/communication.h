
#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>
#include "pid_control.h"

// Forward declarations (extern - NO DEFINITIONS HERE)
extern PIDController pidL;
extern PIDController pidR;
extern bool ros2_connected;
extern unsigned long last_heartbeat;
extern String inputString;
extern boolean stringComplete;

// Function declarations
void processSerialCommand(String command);
void processROSCommand(String command);
void processPIDCommand(String command);
void processPIDTuning(String params, PIDController &pid, const String &name);
bool isNumeric(String str);
void printDiagnostics();
void printHelp();
void printPIDHelp();


#endif