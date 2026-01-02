
import cv2
import time
import base64
import numpy as np
import mediapipe as mp


class ProctoringEngine:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.calibrated = False
        self.calibration_samples = []
        self.base_pitch = 0.0
        self.base_yaw = 0.0

    def get_head_pose(self, landmarks, img_shape):
        h, w = img_shape[:2]

        image_points = np.array([
            (landmarks[1].x * w, landmarks[1].y * h),
            (landmarks[152].x * w, landmarks[152].y * h),
            (landmarks[33].x * w, landmarks[33].y * h),
            (landmarks[263].x * w, landmarks[263].y * h),
            (landmarks[61].x * w, landmarks[61].y * h),
            (landmarks[291].x * w, landmarks[291].y * h),
        ], dtype="double")

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -63.6, -12.5),
            (-43.3, 32.7, -26.0),
            (43.3, 32.7, -26.0),
            (-28.9, -28.9, -24.1),
            (28.9, -28.9, -24.1),
        ])

        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ])

        dist_coeffs = np.zeros((4, 1))
        _, rot_vec, _ = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        return angles  # pitch, yaw, roll

    def process_frame(self, frame_data):
        if "," in frame_data:
            frame_data = frame_data.split(",")[1]

        try:
            img = cv2.imdecode(np.frombuffer(base64.b64decode(frame_data), np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return {"status": "Error", "message": "Invalid image"}

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return {"status": "Flagged", "violations": ["No Face Detected"]}

            pitch, yaw, roll = self.get_head_pose(results.multi_face_landmarks[0].landmark, img.shape)

            if not self.calibrated:
                self.calibration_samples.append((pitch, yaw))
                if len(self.calibration_samples) >= 30:
                    self.base_pitch = sum(p for p, _ in self.calibration_samples) / 30
                    self.base_yaw = sum(y for _, y in self.calibration_samples) / 30
                    self.calibrated = True
                    return {"status": "Calibrated"}
                return {"status": "Calibrating", "progress": len(self.calibration_samples)}

            delta_pitch = pitch - self.base_pitch
            delta_yaw = yaw - self.base_yaw

            violations = []
            if abs(delta_yaw) > 25:
                violations.append("Looking Away")
            if abs(delta_pitch) > 20:
                violations.append("Looking Down")

            return {
                "status": "Flagged" if violations else "Clean",
                "violations": violations,
                "angles": {
                    "pitch": round(delta_pitch, 2),
                    "yaw": round(delta_yaw, 2)
                }
            }
        except Exception as e:
            return {"status": "Error", "message": str(e)}


class ProctoringService:
    _instance = None

    @staticmethod
    def get_instance():
        if ProctoringService._instance is None:
            ProctoringService._instance = ProctoringEngine()
        return ProctoringService._instance
