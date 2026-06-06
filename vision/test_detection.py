import cv2
import time
import sys
import os

sys.path.insert(0, '/home/fruit/fruit_robot')
from vision.camera_test import CameraManager
from vision.fruit_detector import FruitDetector
from vision.target_calculator import TargetCalculator

def main():
    print("Starting detection test...")
    cam = CameraManager()
    detector = FruitDetector()
    calc = TargetCalculator()

    if not cam.start():
        print("Camera failed to start")
        return

    try:
        frame = cam.capture()
        if frame is not None:
            detections = detector.detect(frame)
            if detections:
                best = detector.get_best_detection(detections)
                readiness = calc.get_pick_readiness(best)
                print(f"Found fruit! Center: ({best.cx}, {best.cy})")
                print(f"Ready: {readiness['ready']}")
                if readiness['issues']:
                    print("Issues:")
                    for i in readiness['issues']:
                        print(f"- {i}")
            else:
                print("No fruit detected in frame")
    finally:
        cam.stop()

if __name__ == "__main__":
    main()
