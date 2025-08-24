import time
import json
import threading
from datetime import datetime
from serial_interface import SerialInterface

class MotorController:
    def __init__(self, config_path='config/settings.yaml'):
        self.serial_interface = SerialInterface(config_path)
        self.motor_data = {
            'left': {'speed': 0, 'target': 0, 'direction': 'STOPPED', 'pulses': 0},
            'right': {'speed': 0, 'target': 0, 'direction': 'STOPPED', 'pulses': 0}
        }
        self.system_status = {
            'emergency_stop': False,
            'braking': False,
            'ros_connected': False,
            'last_heartbeat': None,
            'serial_connected': False
        }
        self.data_history = {
            'timestamp': [],
            'left_speed': [],
            'right_speed': [],
            'left_target': [],
            'right_target': [],
            'left_pulses': [],
            'right_pulses': []
        }
        self.update_thread = None
        self.running = False
    
    def start(self):
        self.serial_interface.start()
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.start()
        print("Motor controller started")
    
    def stop(self):
        self.running = False
        self.serial_interface.stop()
        if self.update_thread:
            self.update_thread.join()
        print("Motor controller stopped")
    
    def _update_loop(self):
        while self.running:
            data = self.serial_interface.get_all_data()
            for line in data:
                self._process_data(line)
            
            # Update serial connection status
            self.system_status['serial_connected'] = self.serial_interface.is_connected()
            
            time.sleep(0.01)
    
    def _process_data(self, data):
        try:
            # Process different data formats
            if data.startswith('STATUS:'):
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
            
            # Keep history within limits
            max_history = 1000
            for key in self.data_history:
                if len(self.data_history[key]) > max_history:
                    self.data_history[key] = self.data_history[key][-max_history:]
                    
        except Exception as e:
            print(f"Error processing data: {e}")
    
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
        if direction.upper() == 'FORWARD':
            self.serial_interface.send_command('F')
        elif direction.upper() == 'REVERSE':
            self.serial_interface.send_command('R')
    
    def stop_motors(self):
        self.serial_interface.send_command('S')
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
        print(f"ROS Connected: {status['system']['ros_connected']}")
        print(f"Emergency Stop: {status['system']['emergency_stop']}")
        print(f"Braking: {status['system']['braking']}")
        print(f"Left Motor - Speed: {status['motors']['left']['speed']}, Target: {status['motors']['left']['target']}")
        print(f"Right Motor - Speed: {status['motors']['right']['speed']}, Target: {status['motors']['right']['target']}")
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
                'data_points': len(self.data_history['timestamp'])
            },
            'data': self.data_history
        }
        
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
        
        return filename