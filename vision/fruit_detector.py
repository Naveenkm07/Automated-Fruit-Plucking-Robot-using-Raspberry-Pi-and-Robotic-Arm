import cv2
import numpy as np
import time
import sys
import os

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import (
    HSV_LOWER_RED1, HSV_UPPER_RED1,
    HSV_LOWER_RED2, HSV_UPPER_RED2,
    MIN_FRUIT_AREA, DETECTION_CONFIDENCE
)

class Detection:
    def __init__(self, x, y, w, h, confidence, method='hsv', label='tomato'):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = x + w // 2
        self.cy = y + h // 2
        self.confidence = confidence
        self.method = method
        self.label = label
        self.area = w * h

class FruitDetector:
    def __init__(self, method='hsv'):
        self.method = method
        self.hsv_lower1 = np.array(HSV_LOWER_RED1)
        self.hsv_upper1 = np.array(HSV_UPPER_RED1)
        self.hsv_lower2 = np.array(HSV_LOWER_RED2)
        self.hsv_upper2 = np.array(HSV_UPPER_RED2)

    def detect(self, frame):
        if frame is None:
            return []
        return self._detect_hsv(frame)

    def _detect_hsv(self, frame):
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.hsv_lower1, self.hsv_upper1)
        mask2 = cv2.inRange(hsv, self.hsv_lower2, self.hsv_upper2)
        mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MIN_FRUIT_AREA:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * 3.14159 * area / (perimeter * perimeter)
            
            if circularity < 0.3:
                continue

            aspect_ratio = float(w) / h if h > 0 else 0
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                continue

            roi_hsv = hsv[y:y+h, x:x+w]
            avg_saturation = roi_hsv[:, :, 1].mean() / 255.0
            confidence = min(1.0, circularity * avg_saturation * 1.5)

            detections.append(Detection(x, y, w, h, confidence, method='hsv'))

        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections

    def draw_detections(self, frame, detections):
        annotated = frame.copy()
        for i, det in enumerate(detections):
            color = (0, 165, 255)
            cv2.rectangle(annotated, (det.x, det.y),
                         (det.x + det.w, det.y + det.h), color, 2)
            cv2.drawMarker(annotated, (det.cx, det.cy),
                          color, cv2.MARKER_CROSS, 15, 2)
            label = f"#{i+1} {det.label} {det.confidence:.0%}"
            label_y = det.y - 10 if det.y > 30 else det.y + det.h + 20
            cv2.putText(annotated, label, (det.x, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return annotated

    def get_best_detection(self, detections):
        if not detections:
            return None
        return max(detections, key=lambda d: d.confidence)
