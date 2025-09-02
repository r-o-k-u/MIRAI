# main.py
import argparse
import signal
import sys
import threading
import time
from motor_controller import MotorController
from data_visualizer import DataVisualizer

def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT"""
    print("\nShutting down gracefully...")
    if 'motor_controller' in globals():
        motor_controller.stop()
    if 'visualizer' in globals() and visualizer.running:
        visualizer.stop()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='MIRAI Motor Control Interface')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    parser.add_argument('--config', default='config/settings.yaml', help='Config file path')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode (no serial)')
    args = parser.parse_args()
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize motor controller
    global motor_controller
    motor_controller = MotorController(args.config, simulate=args.simulate)
    
    try:
        motor_controller.start()
        
        if not args.no_gui:
            # Initialize and start visualizer in a separate thread
            global visualizer
            visualizer = DataVisualizer(motor_controller)
            visualizer_thread = threading.Thread(target=visualizer.start, daemon=True)
            visualizer_thread.start()
            
            # Keep main thread alive while visualizer is running
            try:
                while visualizer.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                
        else:
            # Command line interface mode
            print("MIRAI Motor Control - CLI Mode")
            print("Commands: forward, reverse, stop, emergency, clear, speed <left> <right>, coast, softbrake, hardbrake, status, exit")
            
            while True:
                try:
                    command = input("> ").strip().lower()
                    
                    if command == 'exit':
                        break
                    elif command == 'forward':
                        motor_controller.set_direction('both', 'FORWARD')
                    elif command == 'reverse':
                        motor_controller.set_direction('both', 'REVERSE')
                    elif command == 'stop':
                        motor_controller.stop_motors()
                    elif command == 'coast':
                        motor_controller.coast_motors()
                    elif command == 'emergency':
                        motor_controller.emergency_stop()
                    elif command == 'clear':
                        motor_controller.clear_emergency()
                    elif command == 'softbrake':
                        motor_controller.activate_soft_brake()
                    elif command == 'hardbrake':
                        motor_controller.activate_hard_brake()
                    elif command.startswith('speed'):
                        parts = command.split()
                        if len(parts) == 3:
                            try:
                                left_speed = int(parts[1])
                                right_speed = int(parts[2])
                                motor_controller.set_speed('left', left_speed)
                                motor_controller.set_speed('right', right_speed)
                            except ValueError:
                                print("Invalid speed values")
                        else:
                            print("Usage: speed <left> <right>")
                    elif command == 'status':
                        status = motor_controller.get_status()
                        print(f"Left: {status['motors']['left']['speed']}/255, Target: {status['motors']['left']['target']}")
                        print(f"Right: {status['motors']['right']['speed']}/255, Target: {status['motors']['right']['target']}")
                        print(f"Emergency: {status['system']['emergency_stop']}")
                        print(f"Serial Connected: {status['system']['serial_connected']}")
                    elif command == 'pid':
                        # Show PID status
                        print("PID status would be displayed here")
                    else:
                        print("Unknown command")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
    
    except Exception as e:
        print(f"Fatal error: {e}")
    
    finally:
        motor_controller.stop()
        if not args.no_gui and 'visualizer' in globals() and visualizer.running:
            visualizer.stop()

if __name__ == "__main__":
    main()