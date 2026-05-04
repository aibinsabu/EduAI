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

import cv2
import time
import base64
import sys
import os

# --- CLEAN AI REDIRECTION (Bypass Space/Paren Bug) ---
CLEAN_AI_PATH = r"D:\EducationalAI"
if CLEAN_AI_PATH not in sys.path:
    sys.path.insert(0, CLEAN_AI_PATH)
# ----------------------------------------------------

import mediapipe as mp
import numpy as np
import threading
import sys
import os

# --- MEDIAPIPE WINDOWS PATH PATCH (IMPORTANT) ---
# Fixes "libprotobuf ERROR... Expected identifier, got: \" when spaces/parens are in path.
try:
    if os.name == 'nt':
        import mediapipe.python.solution_base as pb
        _orig_init = pb.SolutionBase.__init__
        def _patched_init(self, *args, **kwargs):
            # Force the internal path to use the virtual Z: drive (mapped earlier)
            if 'binary_graph_path' in kwargs and kwargs['binary_graph_path']:
                kwargs['binary_graph_path'] = kwargs['binary_graph_path'].replace(
                    'D:\\New folder (2)\\project', 'Z:'
                ).replace('D:/New folder (2)/project', 'Z:')
            
            # Also ensure the AI engine initializes in a space-free environment
            old_cwd = os.getcwd()
            try:
                if os.path.exists('Z:\\'):
                    os.chdir('Z:\\edu')
                else:
                    os.chdir(os.path.dirname(pb.__file__))
                return _orig_init(self, *args, **kwargs)
            finally:
                os.chdir(old_cwd)
        pb.SolutionBase.__init__ = _patched_init
        print("DEBUG: MediaPipe Z-Drive Redirection Applied (Proctoring)")
except Exception as e:
    print(f"Warning: MediaPipe Path Patch Failed: {e}")
# ------------------------------------------------

_local = threading.local()

class ProctoringEngine:
    def __init__(self):
        print("DEBUG: ProctoringEngine Initialized")

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

        success, rot_vec, _ = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0.0, 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        return angles[0], angles[1], angles[2]

    def process_frame(self, frame_data, calibration_state=None):
        if calibration_state is None:
            calibration_state = {
                "calibrated": False,
                "base_pitch": 0.0,
                "base_yaw": 0.0,
                "violation_streak": 0
            }

        if "," in frame_data:
            frame_data = frame_data.split(",")[1]

        try:
            img_bytes = base64.b64decode(frame_data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if img is None or img.size == 0:
                return {"status": "Error", "message": "Video stream corrupted or empty"}, calibration_state

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            results = self.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return {"status": "Flagged", "violations": ["Face Not Visible"]}, calibration_state

            pitch, yaw, roll = self.get_head_pose(
                results.multi_face_landmarks[0].landmark, img.shape
            )

            pitch = float(pitch)
            yaw = float(yaw)

            if not calibration_state["calibrated"]:
                if calibration_state.get("trigger_calibration"):
                    calibration_state["base_pitch"] = pitch
                    calibration_state["base_yaw"] = yaw
                    calibration_state["calibrated"] = True
                    calibration_state["violation_streak"] = 0
                    calibration_state["trigger_calibration"] = False
                    return {"status": "Calibrated", "message": "Baseline Set"}, calibration_state

                return {"status": "preview", "message": "Position yourself and click Calibrate"}, calibration_state

            base_pitch = calibration_state["base_pitch"]
            base_yaw = calibration_state["base_yaw"]

            delta_pitch = pitch - base_pitch
            delta_yaw = yaw - base_yaw

            violations = []
            if abs(delta_yaw) > 35:
                violations.append("Looking Away")
            if abs(delta_pitch) > 20:
                violations.append("Looking Down")

            if violations:
                calibration_state["violation_streak"] += 1
            else:
                calibration_state["violation_streak"] = 0

            status = "Clean"
            final_violations = []

            if calibration_state["violation_streak"] >= 3:
                status = "Flagged"
                final_violations = violations

            return {
                "status": status,
                "violations": final_violations,
                "angles": {
                    "pitch": round(delta_pitch, 2),
                    "yaw": round(delta_yaw, 2)
                }
            }, calibration_state

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Proctoring Error: {e}")
            return {"status": "Error", "message": "Proctoring model busy or tracking lost"}, calibration_state


class ProctoringService:
    _instance = None

    @staticmethod
    def get_instance():
        if ProctoringService._instance is None:
            ProctoringService._instance = ProctoringEngine()
        return ProctoringService._instance

    @staticmethod
    def reset_instance():
        ProctoringService._instance = None
        print("DEBUG: ProctoringService instance reset.")
