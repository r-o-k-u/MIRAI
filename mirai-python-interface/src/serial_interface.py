import serial
import time
import logging
import threading
from queue import Queue
import yaml
import random

class SerialInterface:
    def __init__(self, config_path='config/settings.yaml', simulate=False):
        self.simulate = simulate
        self.load_config(config_path)
        self.serial_conn = None
        self.running = False
        self.data_queue = Queue()
        self.command_queue = Queue()
        self.logger = self.setup_logger()
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default config if file doesn't exist
            self.config = {
                'serial': {
                    'port': 'COM3',
                    'baudrate': 115200,
                    'timeout': 0.1
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'motor_control.log'
                }
            }
    
    def setup_logger(self):
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def connect(self):
        if self.simulate:
            self.logger.warning("SIMULATION MODE: Serial connection disabled")
            return True
            
        try:
            self.serial_conn = serial.Serial(
                port=self.config['serial']['port'],
                baudrate=self.config['serial']['baudrate'],
                timeout=self.config['serial']['timeout'],
                write_timeout=1.0  # Add write timeout
            )
            time.sleep(2)  # Wait for connection to establish
            self.logger.info(f"Connected to {self.config['serial']['port']}")
            self.connection_attempts = 0
            return True
        except serial.SerialException as e:
            self.connection_attempts += 1
            if self.connection_attempts <= self.max_connection_attempts:
                self.logger.warning(f"Serial connection attempt {self.connection_attempts} failed: {e}")
            else:
                self.logger.error(f"Serial connection failed after {self.max_connection_attempts} attempts: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected connection error: {e}")
            return False
    
    def start(self):
        if self.connect():
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
            self.read_thread.start()
            self.write_thread.start()
            self.logger.info("Serial interface started")
        else:
            self.logger.error("Failed to start serial interface")
    
    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception as e:
                self.logger.error(f"Error closing serial connection: {e}")
        self.logger.info("Serial interface stopped")
    
    def _read_loop(self):
        while self.running:
            try:
                if self.simulate:
                    # Generate simulated data
                    time.sleep(0.5)  # Slower simulation to reduce CPU usage
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
                        if self.serial_conn.in_waiting > 0:
                            line = self.serial_conn.readline().decode('utf-8').strip()
                            if line:
                                self.data_queue.put(line)
                        else:
                            time.sleep(0.01)  # Small sleep to prevent busy waiting
                    except serial.SerialException as e:
                        self.logger.error(f"Serial read error: {e}")
                        # Try to reconnect
                        self._handle_serial_error()
                        time.sleep(1)
            except Exception as e:
                self.logger.error(f"Unexpected read loop error: {e}")
                time.sleep(1)
    
    def _write_loop(self):
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    if self.simulate:
                        self.logger.debug(f"SIMULATION: Would send: {command}")
                        # Simulate command processing delay
                        time.sleep(0.1)
                    elif self.serial_conn and self.serial_conn.is_open:
                        try:
                            self.serial_conn.write((command + '\n').encode('utf-8'))
                            self.logger.debug(f"Sent: {command}")
                        except serial.SerialException as e:
                            self.logger.error(f"Serial write error: {e}")
                            # Try to reconnect
                            self._handle_serial_error()
                else:
                    time.sleep(0.01)  # Small sleep to prevent busy waiting
            except Exception as e:
                self.logger.error(f"Unexpected write loop error: {e}")
                time.sleep(1)
    
    def _handle_serial_error(self):
        """Handle serial communication errors by attempting to reconnect"""
        if not self.simulate:
            self.logger.warning("Attempting to reconnect to serial port...")
            self.stop()
            time.sleep(2)
            self.start()
    
    def send_command(self, command):
        """Send a command to the serial device"""
        try:
            self.command_queue.put(command)
            return True
        except Exception as e:
            self.logger.error(f"Error queueing command: {e}")
            return False
    
    def get_data(self):
        """Get a single data item from the queue"""
        try:
            if not self.data_queue.empty():
                return self.data_queue.get_nowait()
            return None
        except Exception as e:
            self.logger.error(f"Error getting data: {e}")
            return None
    
    def get_all_data(self):
        """Get all available data from the queue"""
        data = []
        try:
            while not self.data_queue.empty():
                data.append(self.data_queue.get_nowait())
        except Exception as e:
            self.logger.error(f"Error getting all data: {e}")
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