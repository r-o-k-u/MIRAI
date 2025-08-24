import serial
import time
import logging
import threading
from queue import Queue
import yaml

class SerialInterface:
    def __init__(self, config_path='config/settings.yaml'):
        self.load_config(config_path)
        self.serial_conn = None
        self.running = False
        self.data_queue = Queue()
        self.command_queue = Queue()
        self.logger = self.setup_logger()
        
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
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
            self.read_thread = threading.Thread(target=self._read_loop)
            self.write_thread = threading.Thread(target=self._write_loop)
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
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        self.data_queue.put(line)
            except serial.SerialException as e:
                self.logger.error(f"Read error: {e}")
                time.sleep(0.1)
    
    def _write_loop(self):
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    if self.serial_conn and self.serial_conn.is_open:
                        self.serial_conn.write((command + '\n').encode('utf-8'))
                        self.logger.debug(f"Sent: {command}")
            except serial.SerialException as e:
                self.logger.error(f"Write error: {e}")
                time.sleep(0.1)
    
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