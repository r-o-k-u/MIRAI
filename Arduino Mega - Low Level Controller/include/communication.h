#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>

// Global variables
extern bool ros2_connected;
extern unsigned long last_heartbeat;
extern String inputString;
extern boolean stringComplete;

// Function declarations
void processSerialCommand(String command);
void processROSCommand(String command);
bool isNumeric(String str);
void printDiagnostics();
void printHelp();
void serialEvent();

#endif