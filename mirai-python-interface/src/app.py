from flask import Flask, render_template, jsonify, request
import threading
import time
import signal
import sys
from motor_controller import MotorController
import argparse

app = Flask(__name__)

# Global variables
motor_controller = None
running = True

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