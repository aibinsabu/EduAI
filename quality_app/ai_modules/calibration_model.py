import os
os.environ["GLOG_minloglevel"] = "3"
os.environ["GLOG_stderrthreshold"] = "3"
os.environ["GLOG_logtostderr"] = "0"
os.environ["GLOG_v"] = "0"
os.environ["ABSL_MIN_LOG_LEVEL"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import logging
logging.getLogger("mediapipe").setLevel(logging.ERROR)

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)
absl.logging.set_stderrthreshold('error')


import threading

_local = threading.local()

class CalibrationEngine:
    """
    Dedicated AI Engine for the Calibration / Preview Phase.
    Stateless, safe, and stable.
    """

    def __init__(self):
        print("DEBUG: CalibrationEngine Initialized")

    @property
    def face_mesh(self):
        if not hasattr(_local, 'face_mesh'):
            _local.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
        return _local.face_mesh

    def analyze_frame(self, frame_data, strict=True):
        if "," in frame_data:
            frame_data = frame_data.split(",")[1]

        try:
            # Decode image
            img_bytes = base64.b64decode(frame_data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                return {"status": "Error", "message": "Cannot decode image"}

            # Lighting check
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = float(np.mean(gray))

            if strict:
                if brightness < 40:
                    return {"status": "Flagged", "message": "Too Dark. Please increase lighting."}
                if brightness > 220:
                    return {"status": "Flagged", "message": "Too Bright. Avoid backlighting."}

            # Face detection
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return {"status": "Flagged", "message": "No Face Detected"}

            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = img.shape

            # Centering check (nose tip = 1)
            nose = landmarks[1]
            if strict:
                if nose.x < 0.30 or nose.x > 0.70 or nose.y < 0.30 or nose.y > 0.80:
                    return {"status": "Flagged", "message": "Center your face in the frame"}

            # Blur check
            laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            if strict and laplacian_var < 20:
                return {"status": "Flagged", "message": "Image too blurry. Clean lens?"}

            # Head pose
            pitch, yaw, roll = self.get_head_pose(landmarks, (h, w))

            if strict:
                if abs(yaw) > 25:
                    return {"status": "Flagged", "message": "Look straight at the screen (Yaw)"}
                if abs(pitch) > 20:
                    return {"status": "Flagged", "message": "Look straight at the screen (Pitch)"}

            return {
                "status": "OK",
                "pitch": float(pitch),
                "yaw": float(yaw),
                "brightness": brightness,
                "blur_score": laplacian_var
            }

        except Exception as e:
            print(f"Calibration Error: {e}")
            err_str = str(e)
            if len(err_str) > 50:
                 # Mediapipe protobuf errors are huge and break the UI
                 err_str = "AI Engine is warming up or frame tracking failed. Retrying..."
            return {"status": "Error", "message": err_str}

    def get_head_pose(self, landmarks, img_shape):
        h, w = img_shape

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

        success, rot_vec, trans_vec = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0.0, 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        return angles[0], angles[1], angles[2]


# Singleton
_calibration_instance = None

def get_calibration_engine():
    global _calibration_instance
    if _calibration_instance is None:
        _calibration_instance = CalibrationEngine()
    return _calibration_instance
