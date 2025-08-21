<img width="1536" height="1024" alt="ChatGPT Image Aug 21, 2025, 12_14_34 PM" src="https://github.com/user-attachments/assets/1a98484c-021e-4820-97d3-992f220d8c4a" />

# MIRAI
🚀 Mirai: A Modular ROS2-Based Robotics Learning Platform
🔹 Introduction

Hi👋, this is Mirai—my personal robotics learning platform.

I come from an IT background (BBIT – Business & IT) and have spent years in software development (JavaScript, Python, cloud systems). I currently work in agricultural data analytics, helping companies use data for predictive maintenance and forecasting.

But I’ve always wanted to dive into robotics, electronics, and mechatronics. So I decided to build a modular open robotics platform that will let me:

Learn about sensors, actuators, and embedded systems.

Explore ROS2 as the standard robotics middleware.

Integrate various MCUs, SBCs, and communication protocols.

Control real hardware (motors, relays, LEDs) and stream sensor data (video, IMU, etc.).

Document the journey so others can learn along with me.

🔹 Hardware Inventory

So far, my hardware collection includes:

Orange Pi Zero 2W (1GB RAM) – running Ubuntu 22.04 + ROS2 Humble.

Raspberry Pi Zero 2W (512MB RAM) – for lightweight tasks / secondary robot.

Arduino Mega – motor + relay control via serial.

Arduino Uno – for smaller experiments.

ESP32 (x2) – future expansion nodes.

ESP32-CAM – low-cost video streaming module.

Microsoft Kinect v1 – RGB + depth camera.

2x ZS-X11H motor drivers – to control hoverboard motors.

Accelerometer (IMU) – for motion sensing.

Relays + LEDs – for signaling/control.

🔹 System Architecture

At the core, Mirai is built around ROS2 with a distributed setup:

Orange Pi Zero 2W

Runs ROS2 Humble.

Acts as a sensor + control gateway.

Connects Kinect v1 → publishes RGB/Depth feeds.

Handles communication with Arduino Mega via serial.

Arduino Mega

Low-level motor + actuator controller.

Controls hoverboard motors via ZS-X11H drivers.

Switches relays + LEDs.

Reads accelerometer.

Communicates with Orange Pi over serial.

PC (Workstation)

Heavy-duty ROS2 node.

Subscribes to Kinect & ESP32-CAM feeds.

Runs video processing + object detection.

Sends back motor/LED commands to Orange Pi.

Future Expansion (ESP32s, Pi Zero, Uno)

ESP32 #1: Extra sensors, wireless relays.

ESP32 #2: Motor driver for a mini robot.

ESP32-CAM: Extra video source (low-res stream).

Raspberry Pi Zero 2W: Secondary robot brain.

Arduino Uno: Simple actuator experiments.

🔹 ROS2 Node Layout

On Orange Pi

kinect_driver_node → Publishes Kinect RGB/Depth.

serial_bridge_node → Talks to Arduino Mega (motor, relay, sensor data).

cmd_relay_node → Forwards PC control commands to Arduino.

On PC

vision_node → Processes Kinect & ESP32-CAM feeds (object detection, tracking).

control_logic_node → Generates motor + LED commands.

teleop_node → Manual joystick/keyboard override.

On Arduino Mega

motor_loop → Controls ZS-X11H → hoverboard motors.

relay_loop → Toggles LEDs via relays.

imu_loop → Reads accelerometer → sends data back.

safety_loop → Emergency stop if serial connection lost.

🔹 Communication Plan

ROS2 over LAN between Orange Pi and PC.

Serial (UART/USB) between Orange Pi and Arduino Mega.

Wi-Fi for ESP32s and ESP32-CAM.

Future option: MQTT or micro-ROS to integrate ESP32 nodes into ROS2.

🔹 Development Roadmap
✅ Phase 1 (Current)

Install Ubuntu 22.04 + ROS2 Humble on Orange Pi.

Connect Kinect v1 → publish RGB/Depth topics.

Forward Kinect video to PC → verify streaming.

🔜 Phase 2

Arduino Mega integration:

Motor control via ZS-X11H.

Relay + LED switching.

Accelerometer feedback.

🔜 Phase 3

Control loop:

PC does image detection.

Sends /cmd_motor + /cmd_led commands.

Orange Pi → Arduino executes commands.

🔜 Phase 4

Add ESP32s + ESP32-CAM as ROS2 nodes (via micro-ROS or MQTT bridge).

Experiment with distributed robots (ESP32 + Pi Zero).

🔜 Phase 5

Build miniature robot swarm controlled via ROS2 network.

Explore multi-robot coordination.

Test ML-based navigation + reinforcement learning.

🔹 Why Mirai?

This project isn’t just about one robot. It’s about building a modular, scalable robotics platform that:

Starts with simple motor + sensor control.

Scales to distributed, multi-robot coordination.

Helps me (and others) learn ROS2, embedded electronics, and AI robotics step by step.

🔹 Open Source

All project files (code, wiring diagrams, firmware, ROS2 launch files) will be on:

🔗 GitHub Repository .

🔗 Hackaday Project Page.

Contributions, suggestions, and collaboration are welcome!

