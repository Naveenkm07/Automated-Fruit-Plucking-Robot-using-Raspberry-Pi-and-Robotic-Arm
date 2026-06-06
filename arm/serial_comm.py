import serial
import time
import sys
import glob

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import ARM_SERIAL_PORT, ARM_BAUD_RATE

class ArduinoComm:
    def __init__(self, port=ARM_SERIAL_PORT, baudrate=ARM_BAUD_RATE):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.is_connected = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            self.is_connected = True
            return True
        except Exception as e:
            print(f'Serial error: {e}')
            return False

    def find_arduino_port(self):
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        for port in ports:
            self.port = port
            if self.connect():
                print(f'Found Arduino on {port}')
                return port
        return None

    def send_command(self, cmd):
        if not self.is_connected: return None
        try:
            self.ser.write((cmd + '\n').encode('utf-8'))
            resp = self.ser.readline().decode('utf-8').strip()
            return resp
        except:
            return None

    def move_servo(self, channel, angle):
        return self.send_command(f'MOVE:{channel},{angle}')

    def pick(self):
        return self.send_command('PICK')

    def drop(self):
        return self.send_command('DROP')

    def go_home(self):
        return self.send_command('HOME')

    def open_gripper(self):
        return self.move_servo(4, 30)

    def close_gripper(self):
        return self.move_servo(4, 110)

    def get_status(self):
        resp = self.send_command('STATUS')
        if resp and resp.startswith('ANGLES:'):
            return [int(x) for x in resp.split(':')[1].split(',')]
        return None

    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.is_connected = False
