import sys
sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import CAMERA_RESOLUTION

class TargetCalculator:
    def __init__(self, frame_width=None, frame_height=None):
        self.frame_width = frame_width or CAMERA_RESOLUTION[0]
        self.frame_height = frame_height or CAMERA_RESOLUTION[1]
        self.center_x = self.frame_width // 2
        self.center_y = self.frame_height // 2
        self.dead_zone_x = self.frame_width * 0.1
        self.dead_zone_y = self.frame_height * 0.1

    def detection_to_arm_coords(self, detection):
        x = int(((self.center_x - detection.cx) / self.center_x) * 100)
        x = max(-100, min(100, x))
        y = int(((self.frame_height - detection.cy) / self.frame_height) * 100)
        y = max(0, min(100, y))
        return x, y

    def get_reach_command(self, detection):
        x, y = self.detection_to_arm_coords(detection)
        return f"REACH:{x},{y}"

    def is_centered(self, detection):
        dx = abs(detection.cx - self.center_x)
        dy = abs(detection.cy - self.center_y)
        return dx < self.dead_zone_x and dy < self.dead_zone_y

    def get_rover_adjustment(self, detection):
        if self.is_centered(detection):
            return {'action': 'centered', 'amount': 0}

        dx = detection.cx - self.center_x
        dy = detection.cy - self.center_y

        if abs(dx) > abs(dy):
            if dx > self.dead_zone_x:
                return {'action': 'move_right', 'amount': abs(dx) / self.center_x}
            elif dx < -self.dead_zone_x:
                return {'action': 'move_left', 'amount': abs(dx) / self.center_x}
        else:
            if dy > self.dead_zone_y:
                return {'action': 'move_forward', 'amount': abs(dy) / self.center_y}
            elif dy < -self.dead_zone_y:
                return {'action': 'move_backward', 'amount': abs(dy) / self.center_y}

        return {'action': 'centered', 'amount': 0}

    def estimate_distance(self, detection, known_fruit_diameter_cm=7):
        focal_length_pixels = 500
        apparent_diameter = max(detection.w, detection.h)
        if apparent_diameter == 0:
            return float('inf')
        distance = (focal_length_pixels * known_fruit_diameter_cm) / apparent_diameter
        return round(distance, 1)

    def get_pick_readiness(self, detection):
        issues = []
        score = 1.0

        if not self.is_centered(detection):
            adjustment = self.get_rover_adjustment(detection)
            issues.append(f"Not centered: need to {adjustment['action']}")
            score -= 0.3

        if detection.confidence < 0.5:
            issues.append(f"Low confidence: {detection.confidence:.0%}")
            score -= 0.2

        fruit_size_ratio = detection.area / (self.frame_width * self.frame_height)
        if fruit_size_ratio < 0.01:
            issues.append("Fruit appears too far away")
            score -= 0.3
        elif fruit_size_ratio > 0.3:
            issues.append("Fruit appears too close")
            score -= 0.2

        arm_x, arm_y = self.detection_to_arm_coords(detection)
        distance = self.estimate_distance(detection)
        ready = score > 0.5 and len(issues) == 0

        return {
            'ready': ready,
            'score': max(0, score),
            'issues': issues,
            'arm_coords': (arm_x, arm_y),
            'estimated_distance_cm': distance
        }
