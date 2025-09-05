from flask import Flask, render_template, jsonify, request
import threading
import time
import signal
import sys
import json
from datetime import datetime
import serial
import serial.tools.list_ports
import yaml
import logging
from queue import Queue
import platform
import os

app = Flask(__name__)

# Global variables
motor_controller = None
running = True

# Detect operating system
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('motor_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SerialInterface:
    def __init__(self, config_path='config/settings.yaml', simulate=False):
        self.simulate = simulate
        self.load_config(config_path)
        self.serial_conn = None
        self.running = False
        self.data_queue = Queue()
        self.command_queue = Queue()
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default config if file doesn't exist
            default_port = 'COM3' if IS_WINDOWS else '/dev/ttyUSB0'
            self.config = {
                'serial': {
                    'port': default_port,
                    'baudrate': 115200,
                    'timeout': 0.1
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'motor_control.log'
                }
            }
    
    def connect(self):
        if self.simulate:
            logger.warning("SIMULATION MODE: Serial connection disabled")
            return True
            
        try:
            self.serial_conn = serial.Serial(
                port=self.config['serial']['port'],
                baudrate=self.config['serial']['baudrate'],
                timeout=self.config['serial']['timeout'],
                write_timeout=1.0  # Add write timeout
            )
            time.sleep(2)  # Wait for connection to establish
            logger.info(f"Connected to {self.config['serial']['port']}")
            self.connection_attempts = 0
            return True
        except serial.SerialException as e:
            self.connection_attempts += 1
            if self.connection_attempts <= self.max_connection_attempts:
                logger.warning(f"Serial connection attempt {self.connection_attempts} failed: {e}")
            else:
                logger.error(f"Serial connection failed after {self.max_connection_attempts} attempts: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}")
            return False
    
    def start(self):
        if self.connect():
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
            self.read_thread.start()
            self.write_thread.start()
            logger.info("Serial interface started")
        else:
            logger.error("Failed to start serial interface")
    
    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
        logger.info("Serial interface stopped")
    
    def _read_loop(self):
        while self.running:
            try:
                if self.simulate:
                    # Generate simulated data
                    time.sleep(0.5)  # Slower simulation to reduce CPU usage
                    import random
                    left_speed = random.randint(0, 255)
                    right_speed = random.randint(0, 255)
                    left_rpm = left_speed * 300 / 255
                    right_rpm = right_speed * 300 / 255
                    simulated_data = [
                        f"Left - RPM:{left_rpm:.1f} MPH:{left_rpm*0.1:.1f} KPH:{left_rpm*0.16:.1f}",
                        f"Right - RPM:{right_rpm:.1f} MPH:{right_rpm*0.1:.1f} KPH:{right_rpm*0.16:.1f}",
                        f"PULSES:{random.randint(1000, 2000)}:{random.randint(1000, 2000)}"
                    ]
                    for data in simulated_data:
                        self.data_queue.put(data)
                elif self.serial_conn and self.serial_conn.is_open:
                    try:
                        # Cross-platform compatible way to check for available data
                        if hasattr(self.serial_conn, 'in_waiting') and self.serial_conn.in_waiting > 0:
                            line = self.serial_conn.readline().decode('utf-8').strip()
                            if line:
                                self.data_queue.put(line)
                        else:
                            time.sleep(0.01)  # Small sleep to prevent busy waiting
                    except serial.SerialException as e:
                        logger.error(f"Serial read error: {e}")
                        # Try to reconnect
                        self._handle_serial_error()
                        time.sleep(1)
            except Exception as e:
                logger.error(f"Unexpected read loop error: {e}")
                time.sleep(1)
    
    def _write_loop(self):
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    if self.simulate:
                        logger.debug(f"SIMULATION: Would send: {command}")
                        # Simulate command processing delay
                        time.sleep(0.1)
                    elif self.serial_conn and self.serial_conn.is_open:
                        try:
                            self.serial_conn.write((command + '\n').encode('utf-8'))
                            logger.debug(f"Sent: {command}")
                        except serial.SerialException as e:
                            logger.error(f"Serial write error: {e}")
                            # Try to reconnect
                            self._handle_serial_error()
                else:
                    time.sleep(0.01)  # Small sleep to prevent busy waiting
            except Exception as e:
                logger.error(f"Unexpected write loop error: {e}")
                time.sleep(1)
    
    def _handle_serial_error(self):
        """Handle serial communication errors by attempting to reconnect"""
        if not self.simulate:
            logger.warning("Attempting to reconnect to serial port...")
            self.stop()
            time.sleep(2)
            self.start()
    
    def send_command(self, command):
        """Send a command to the serial device"""
        try:
            self.command_queue.put(command)
            return True
        except Exception as e:
            logger.error(f"Error queueing command: {e}")
            return False
    
    def get_data(self):
        """Get a single data item from the queue"""
        try:
            if not self.data_queue.empty():
                return self.data_queue.get_nowait()
            return None
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return None
    
    def get_all_data(self):
        """Get all available data from the queue"""
        data = []
        try:
            while not self.data_queue.empty():
                data.append(self.data_queue.get_nowait())
        except Exception as e:
            logger.error(f"Error getting all data: {e}")
        return data

    def is_connected(self):
        """Check if serial connection is active"""
        if self.simulate:
            return True
        return self.serial_conn is not None and self.serial_conn.is_open

    def get_port_status(self):
        """Get detailed port status information"""
        if self.simulate:
            return "Simulation Mode - No physical connection"
        elif self.serial_conn and self.serial_conn.is_open:
            return f"Connected to {self.config['serial']['port']}"
        else:
            return "Disconnected"

class MotorController:
    def __init__(self, config_path='config/settings.yaml', simulate=False):
        self.simulate = simulate
        self.serial_interface = SerialInterface(config_path, simulate=simulate)
        self.motor_data = {
            'left': {'speed': 0, 'target': 0, 'direction': 'STOPPED', 'pulses': 0, 'rpm': 0, 'mph': 0, 'kph': 0},
            'right': {'speed': 0, 'target': 0, 'direction': 'STOPPED', 'pulses': 0, 'rpm': 0, 'mph': 0, 'kph': 0}
        }
        self.system_status = {
            'emergency_stop': False,
            'braking': False,
            'ros_connected': False,
            'last_heartbeat': None,
            'serial_connected': False,
            'simulation_mode': simulate
        }
        self.data_history = {
            'timestamp': [],
            'left_speed': [],
            'right_speed': [],
            'left_target': [],
            'right_target': [],
            'left_pulses': [],
            'right_pulses': [],
            'left_rpm': [],
            'right_rpm': []
        }
        self.update_thread = None
        self.running = False
        self.max_history = 1000
    
    def start(self):
        self.serial_interface.start()
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Motor controller started" + (" in simulation mode" if self.simulate else ""))
    
    def stop(self):
        self.running = False
        self.serial_interface.stop()
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        logger.info("Motor controller stopped")
    
    def _update_loop(self):
        while self.running:
            try:
                # Only try to get data if serial is connected
                if self.serial_interface.is_connected():
                    data = self.serial_interface.get_all_data()
                    for line in data:
                        self._process_data(line)
                else:
                    # If not connected, try to reconnect every 5 seconds
                    time.sleep(5)
                    if not self.simulate:
                        self.serial_interface.start()  # Try to restart
                
                # Update serial connection status
                self.system_status['serial_connected'] = self.serial_interface.is_connected()
                
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(1)
    
    def _process_data(self, data):
        try:
            # Process different data formats
            if data.startswith('Left - ') or data.startswith('Right - '):
                # New speed format with RPM data
                if 'Left -' in data:
                    parts = data.split('Left - ')[1].split()
                    for part in parts:
                        if 'RPM:' in part:
                            self.motor_data['left']['rpm'] = float(part.split(':')[1])
                        elif 'MPH:' in part:
                            self.motor_data['left']['mph'] = float(part.split(':')[1])
                        elif 'KPH:' in part:
                            self.motor_data['left']['kph'] = float(part.split(':')[1])
                
                if 'Right -' in data:
                    parts = data.split('Right - ')[1].split()
                    for part in parts:
                        if 'RPM:' in part:
                            self.motor_data['right']['rpm'] = float(part.split(':')[1])
                        elif 'MPH:' in part:
                            self.motor_data['right']['mph'] = float(part.split(':')[1])
                        elif 'KPH:' in part:
                            self.motor_data['right']['kph'] = float(part.split(':')[1])
            
            elif data.startswith('STATUS:'):
                parts = data.split(':')
                if len(parts) >= 4:
                    motor = 'left' if parts[1] == 'ML' else 'right'
                    self.motor_data[motor]['direction'] = parts[2]
                    self.motor_data[motor]['speed'] = int(parts[3])
            
            elif data.startswith('PULSES:'):
                parts = data.split(':')
                if len(parts) >= 3:
                    self.motor_data['left']['pulses'] = int(parts[1])
                    self.motor_data['right']['pulses'] = int(parts[2])
            
            elif data.startswith('ACK:'):
                # Process acknowledgments
                pass
            
            elif data.startswith('DIAG:'):
                # Process diagnostic data
                pass
            
            # Update data history
            timestamp = datetime.now()
            self.data_history['timestamp'].append(timestamp)
            self.data_history['left_speed'].append(self.motor_data['left']['speed'])
            self.data_history['right_speed'].append(self.motor_data['right']['speed'])
            self.data_history['left_target'].append(self.motor_data['left']['target'])
            self.data_history['right_target'].append(self.motor_data['right']['target'])
            self.data_history['left_pulses'].append(self.motor_data['left']['pulses'])
            self.data_history['right_pulses'].append(self.motor_data['right']['pulses'])
            self.data_history['left_rpm'].append(self.motor_data['left']['rpm'])
            self.data_history['right_rpm'].append(self.motor_data['right']['rpm'])
            
            # Keep history within limits
            for key in self.data_history:
                if len(self.data_history[key]) > self.max_history:
                    self.data_history[key] = self.data_history[key][-self.max_history:]
                    
        except Exception as e:
            logger.error(f"Error processing data: {e}")
    
    # Motor control commands
    def set_speed(self, motor, speed):
        if motor in ['left', 'right']:
            motor_code = 'ML' if motor == 'left' else 'MR'
            self.serial_interface.send_command(f"{motor_code}:{speed}")
            self.motor_data[motor]['target'] = speed
    
    def set_both_speeds(self, speed):
        self.serial_interface.send_command(f"BOTH:{speed}")
        self.motor_data['left']['target'] = speed
        self.motor_data['right']['target'] = speed
    
    def set_direction(self, motor, direction):
        if motor == 'both':
            if direction.upper() == 'FORWARD':
                self.serial_interface.send_command('F')
            elif direction.upper() == 'REVERSE':
                self.serial_interface.send_command('R')
        elif motor in ['left', 'right']:
            # Individual motor direction control
            pass
    
    def stop_motors(self):
        self.serial_interface.send_command('S')
        self.motor_data['left']['target'] = 0
        self.motor_data['right']['target'] = 0
    
    def coast_motors(self):
        self.serial_interface.send_command('COAST')
        self.motor_data['left']['target'] = 0
        self.motor_data['right']['target'] = 0
    
    def emergency_stop(self):
        self.serial_interface.send_command('E')
        self.system_status['emergency_stop'] = True
    
    def clear_emergency(self):
        self.serial_interface.send_command('C')
        self.system_status['emergency_stop'] = False
    
    def activate_soft_brake(self):
        self.serial_interface.send_command('SOFTBRAKE')
        self.system_status['braking'] = True
    
    def activate_hard_brake(self):
        self.serial_interface.send_command('HARDBRAKE')
        self.system_status['braking'] = True
    
    def print_diagnostics(self):
        """Print diagnostic information to console"""
        status = self.get_status()
        print("\n=== MIRAI Motor Controller Diagnostics ===")
        print(f"Serial Connected: {status['system']['serial_connected']}")
        print(f"Simulation Mode: {status['system']['simulation_mode']}")
        print(f"ROS Connected: {status['system']['ros_connected']}")
        print(f"Emergency Stop: {status['system']['emergency_stop']}")
        print(f"Braking: {status['system']['braking']}")
        print(f"Left Motor - Speed: {status['motors']['left']['speed']}, Target: {status['motors']['left']['target']}, RPM: {status['motors']['left']['rpm']}")
        print(f"Right Motor - Speed: {status['motors']['right']['speed']}, Target: {status['motors']['right']['target']}, RPM: {status['motors']['right']['rpm']}")
        print("==========================================\n")
    
    def get_status(self):
        return {
            'motors': self.motor_data,
            'system': self.system_status,
            'timestamp': datetime.now()
        }
    
    def get_history(self):
        return self.data_history
    
    def save_data(self, filename=None):
        if filename is None:
            filename = f"motor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data_to_save = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'data_points': len(self.data_history['timestamp']),
                'simulation_mode': self.simulate
            },
            'data': self.data_history
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
            return filename
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def get_status():
    if motor_controller:
        return jsonify(motor_controller.get_status())
    return jsonify({'error': 'Motor controller not initialized'})

@app.route('/command', methods=['POST'])
def send_command():
    if not motor_controller:
        return jsonify({'error': 'Motor controller not initialized'})
    
    command = request.json.get('command')
    params = request.json.get('params', {})
    
    try:
        if command == 'forward':
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
        elif command == 'speed':
            left_speed = params.get('left', 0)
            right_speed = params.get('right', 0)
            motor_controller.set_speed('left', left_speed)
            motor_controller.set_speed('right', right_speed)
        elif command == 'both_speed':
            speed = params.get('speed', 0)
            motor_controller.set_both_speeds(speed)
        else:
            return jsonify({'error': 'Unknown command'})
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/history')
def get_history():
    if motor_controller:
        return jsonify(motor_controller.get_history())
    return jsonify({'error': 'Motor controller not initialized'})

@app.route('/diagnostics')
def get_diagnostics():
    if motor_controller:
        motor_controller.print_diagnostics()
        return jsonify({'success': True})
    return jsonify({'error': 'Motor controller not initialized'})

@app.route('/save_data')
def save_data():
    if motor_controller:
        filename = motor_controller.save_data()
        if filename:
            return jsonify({'success': True, 'filename': filename})
        return jsonify({'error': 'Failed to save data'})
    return jsonify({'error': 'Motor controller not initialized'})

@app.route('/ports')
def list_ports():
    """List all available serial ports"""
    ports = list(serial.tools.list_ports.comports())
    return jsonify([{"device": port.device, "description": port.description} for port in ports])

@app.route('/platform')
def get_platform():
    """Get information about the current platform"""
    return jsonify({
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX
    })

def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT"""
    print("\nShutting down gracefully...")
    global running, motor_controller
    running = False
    if motor_controller:
        motor_controller.stop()
    sys.exit(0)

def start_motor_controller(config_path, simulate=False, port=None):
    """Initialize and start the motor controller"""
    global motor_controller
    motor_controller = MotorController(config_path, simulate=simulate)
    motor_controller.start()
    print("Motor controller started" + (" in simulation mode" if simulate else ""))

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MIRAI Motor Control Web Interface')
    parser.add_argument('--config', default='config/settings.yaml', help='Config file path')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode (no serial)')
    parser.add_argument('--port', help='Specify serial port (e.g., COM5)')
    parser.add_argument('--host', default='127.0.0.1', help='Flask host address')
    parser.add_argument('--flask-port', default=5000, type=int, help='Flask port number')
    args = parser.parse_args()
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start motor controller
    start_motor_controller(args.config, args.simulate, args.port)
    
    # Start Flask app
    try:
        app.run(host=args.host, port=args.flask_port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if motor_controller:
            motor_controller.stop()