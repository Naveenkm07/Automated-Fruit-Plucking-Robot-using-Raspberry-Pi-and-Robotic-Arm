import time
import sys

sys.path.insert(0, '/home/fruit/fruit_robot')

from rover.rover_movement import RoverController
from arm.serial_comm import ArduinoComm
from vision.camera_test import CameraManager
from vision.fruit_detector import FruitDetector
from vision.target_calculator import TargetCalculator
from sensors.obstacle_sensors import ObstacleSensorArray

class HarvestingRobot:
    def __init__(self, detection_method='hsv'):
        print('='*50)
        print('🍎 Initializing Harvesting Robot...')
        print('='*50)
        
        self.rover = RoverController()
        
        self.arm = ArduinoComm()
        if not self.arm.connect():
            self.arm.find_arduino_port()
            
        self.camera = CameraManager()
        self.camera.start()
        
        self.detector = FruitDetector(method=detection_method)
        self.calculator = TargetCalculator()
        
        # Initialize the 6 obstacle sensors
        self.sensors = ObstacleSensorArray()
        
        self.fruits_picked = 0

    def run(self):
        print('\n🚀 Starting autonomous harvesting loop...')
        try:
            while True:
                # 1. Read obstacle sensors to ensure safety
                sensor_data = self.sensors.read_all()
                safe_action = sensor_data['action']
                
                # If we are completely blocked, stop and wait
                if safe_action == 'stop':
                    print('🚨 BLOCKED ON ALL SIDES! Stopping.')
                    self.rover.stop()
                    time.sleep(1)
                    continue

                # 2. Look for fruits
                frame = self.camera.capture()
                if frame is None:
                    continue
                    
                detections = self.detector.detect(frame)
                
                if detections:
                    best = self.detector.get_best_detection(detections)
                    readiness = self.calculator.get_pick_readiness(best)
                    
                    if readiness['ready']:
                        print('🎯 Fruit ready to pick! Stopping rover.')
                        self.rover.stop()
                        
                        print('🦾 Picking fruit...')
                        self.arm.pick()
                        time.sleep(5)
                        self.arm.go_home()
                        self.fruits_picked += 1
                        print(f'✅ Fruits picked: {self.fruits_picked}')
                    else:
                        print('🔄 Adjusting position towards fruit...')
                        adj = self.calculator.get_rover_adjustment(best)
                        
                        # Only move if the obstacle sensors say it is safe!
                        if adj['action'] == 'move_forward' and sensor_data['front_ok']:
                            self.rover.forward(40)
                        elif adj['action'] == 'move_left' and sensor_data['left_ok']:
                            self.rover.turn_left(40)
                        elif adj['action'] == 'move_right' and sensor_data['right_ok']:
                            self.rover.turn_right(40)
                        else:
                            print('⚠️ Cannot move towards fruit (obstacle in the way!)')
                            self.rover.stop()
                            
                        time.sleep(0.5)
                        self.rover.stop()
                else:
                    # No fruit seen, explore the environment using the safe action
                    print(f'🔍 Exploring... (Safe action: {safe_action})')
                    if safe_action == 'forward':
                        self.rover.forward(40)
                    elif safe_action == 'spin_left':
                        self.rover.spin_left(40)
                    elif safe_action == 'spin_right':
                        self.rover.spin_right(40)
                    elif safe_action == 'backward':
                        self.rover.backward(40)
                        
                    time.sleep(0.5)
                    self.rover.stop()
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print('\n🛑 Stopping Harvesting Robot...')
        finally:
            self.cleanup()

    def cleanup(self):
        self.rover.cleanup()
        if self.arm:
            self.arm.go_home()
            self.arm.disconnect()
        if self.camera:
            self.camera.stop()
        if hasattr(self, 'sensors'):
            self.sensors.cleanup()

if __name__ == '__main__':
    method = 'hsv'
    if '--method' in sys.argv:
        method = sys.argv[sys.argv.index('--method') + 1]
    robot = HarvestingRobot(detection_method=method)
    robot.run()
