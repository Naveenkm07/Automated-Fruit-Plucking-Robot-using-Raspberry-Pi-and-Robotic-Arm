import cv2
import time
import sys
import os

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import CAMERA_TYPE, CAMERA_USB_INDEX, CAMERA_RESOLUTION

class CameraManager:
    def __init__(self, camera_type=None, resolution=None):
        self.camera_type = camera_type or CAMERA_TYPE
        self.resolution = resolution or CAMERA_RESOLUTION
        self.camera = None
        self.is_running = False
        self.output_dir = '/home/fruit/fruit_robot/captured_images'
        os.makedirs(self.output_dir, exist_ok=True)

    def start(self):
        try:
            if self.camera_type == 'picamera':
                return self._start_picamera()
            else:
                return self._start_usb()
        except Exception as e:
            print(f"[CAMERA] Failed to start: {e}")
            return False

    def _start_picamera(self):
        try:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)
            self.is_running = True
            return True
        except ImportError:
            self.camera_type = 'usb'
            return self._start_usb()

    def _start_usb(self):
        self.camera = cv2.VideoCapture(CAMERA_USB_INDEX)
        if not self.camera.isOpened():
            return False
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        ret, frame = self.camera.read()
        if not ret:
            return False
        self.is_running = True
        return True

    def capture(self):
        if not self.is_running:
            return None
        try:
            if self.camera_type == 'picamera':
                frame = self.camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame
            else:
                ret, frame = self.camera.read()
                return frame if ret else None
        except Exception as e:
            return None

    def save_image(self, frame, filename=None):
        if frame is None:
            return None
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        cv2.imwrite(filepath, frame)
        return filepath

    def get_brightness(self, frame):
        if frame is None:
            return 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray.mean()

    def stop(self):
        if self.camera:
            if self.camera_type == 'picamera':
                try: self.camera.stop()
                except: pass
            else:
                self.camera.release()
            self.is_running = False

    def __del__(self):
        self.stop()
