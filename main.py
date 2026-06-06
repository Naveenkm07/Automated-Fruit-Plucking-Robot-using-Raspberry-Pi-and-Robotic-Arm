import time
import sys

sys.path.insert(0, '/home/fruit/fruit_robot')

from rover.rover_movement import RoverController
from arm.serial_comm import ArduinoComm
from vision.camera_test import CameraManager
from vision.fruit_detector import FruitDetector
from vision.target_calculator import TargetCalculator

class HarvestingRobot:
    def __init__(self, detection_method='hsv'):
        print('Initializing Harvesting Robot...')
        self.rover = RoverController()
        
        self.arm = ArduinoComm()
        if not self.arm.connect():
            self.arm.find_arduino_port()
            
        self.camera = CameraManager()
        self.camera.start()
        
        self.detector = FruitDetector(method=detection_method)
        self.calculator = TargetCalculator()
        
        self.fruits_picked = 0

    def run(self):
        print('Starting autonomous harvesting loop...')
        try:
            while True:
                frame = self.camera.capture()
                if frame is None:
                    continue
                    
                detections = self.detector.detect(frame)
                
                if detections:
                    best = self.detector.get_best_detection(detections)
                    readiness = self.calculator.get_pick_readiness(best)
                    
                    if readiness['ready']:
                        print('Fruit ready to pick! Stopping rover.')
                        self.rover.stop()
                        
                        print('Picking fruit...')
                        self.arm.pick()
                        time.sleep(5)
                        self.arm.go_home()
                        self.fruits_picked += 1
                        print(f'Fruits picked: {self.fruits_picked}')
                    else:
                        print('Adjusting position...')
                        adj = self.calculator.get_rover_adjustment(best)
                        if adj['action'] == 'move_left':
                            self.rover.turn_left(40)
                        elif adj['action'] == 'move_right':
                            self.rover.turn_right(40)
                        elif adj['action'] == 'move_forward':
                            self.rover.forward(40)
                        time.sleep(0.5)
                        self.rover.stop()
                else:
                    self.rover.spin_right(40)
                    time.sleep(0.5)
                    self.rover.stop()
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print('Stopping...')
        finally:
            self.cleanup()

    def cleanup(self):
        self.rover.cleanup()
        if self.arm:
            self.arm.go_home()
            self.arm.disconnect()
        if self.camera:
            self.camera.stop()

if __name__ == '__main__':
    method = 'hsv'
    if '--method' in sys.argv:
        method = sys.argv[sys.argv.index('--method') + 1]
    robot = HarvestingRobot(detection_method=method)
    robot.run()
