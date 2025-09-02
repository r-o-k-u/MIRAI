# serial_interface.py
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
                timeout=self.config['serial']['timeout']
            )
            time.sleep(2)  # Wait for connection to establish
            self.logger.info(f"Connected to {self.config['serial']['port']}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Serial connection failed: {e}")
            return False
    
    def start(self):
        if self.connect():
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
            self.read_thread.start()
            self.write_thread.start()
            self.logger.info("Serial interface started")
    
    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.logger.info("Serial interface stopped")
    
    def _read_loop(self):
        while self.running:
            try:
                if self.simulate:
                    # Generate simulated data
                    time.sleep(0.1)
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
                elif self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        self.data_queue.put(line)
            except serial.SerialException as e:
                self.logger.error(f"Read error: {e}")
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Unexpected read error: {e}")
                time.sleep(1)
    
    def _write_loop(self):
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    if self.simulate:
                        self.logger.debug(f"SIMULATION: Would send: {command}")
                    elif self.serial_conn and self.serial_conn.is_open:
                        self.serial_conn.write((command + '\n').encode('utf-8'))
                        self.logger.debug(f"Sent: {command}")
            except serial.SerialException as e:
                self.logger.error(f"Write error: {e}")
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Unexpected write error: {e}")
                time.sleep(1)
    
    def send_command(self, command):
        self.command_queue.put(command)
    
    def get_data(self):
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None
    
    def get_all_data(self):
        data = []
        while not self.data_queue.empty():
            data.append(self.data_queue.get())
        return data

    def is_connected(self):
        """Check if serial connection is active"""
        if self.simulate:
            return True
        return self.serial_conn is not None and self.serial_conn.is_open