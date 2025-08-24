import serial.tools.list_ports

def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'Arduino' in port.description or 'USB Serial' in port.description:
            return port.device
    return None

arduino_port = find_arduino_port()
if arduino_port:
    print(f"Arduino found at: {arduino_port}")
else:
    print("No Arduino found. Check connections.")