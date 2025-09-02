# getport.py
import serial.tools.list_ports

def find_arduino_port():
    """Find Arduino port automatically"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if ('Arduino' in port.description or 
            'USB Serial' in port.description or 
            'CH340' in port.description or  # Common Arduino clone chip
            'FT232' in port.description):   # Another common chip
            return port.device
    return None

# Also provide a function to list all available ports
def list_all_ports():
    """List all available serial ports"""
    ports = list(serial.tools.list_ports.comports())
    return [{"device": port.device, "description": port.description} for port in ports]

if __name__ == "__main__":
    arduino_port = find_arduino_port()
    if arduino_port:
        print(f"Arduino found at: {arduino_port}")
    else:
        print("No Arduino found. Available ports:")
        for port in list_all_ports():
            print(f"  {port['device']} - {port['description']}")