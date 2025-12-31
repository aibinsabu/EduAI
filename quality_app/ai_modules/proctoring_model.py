import cv2
import time
import json
import mediapipe as mp
import numpy as np
import base64

class ProctoringEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        print("Initializing Proctoring Engine (Real MediaPipe Loaded)")

    def process_frame(self, frame_data):
        """
        Process a video frame (or image data) to detect anomalies.
        Input: frame_data (base64 string)
        Output: { "status": "Clean" | "Flagged", "violations": [...] }
        """
        violations = []
        status = "Clean"
        
        try:
            # Decode base64 frame
            # frame_data expected format: "data:image/jpeg;base64,..."
            if ',' in frame_data:
                header, encoded = frame_data.split(",", 1)
            else:
                encoded = frame_data
                
            data = base64.b64decode(encoded)
            np_arr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"status": "Error", "violations": ["Invalid Image Data"], "timestamp": time.time()}

            # Process with MediaPipe
            results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            if not results.multi_face_landmarks:
                violations.append("No Face Detected")
                status = "Flagged"
            elif len(results.multi_face_landmarks) > 1:
                violations.append("Multiple Faces Detected")
                status = "Flagged"      
            else:
                # Gaze tracking (Approximation via Iris/Eye landmarks)
                # This is complex, but for demo check head pose or just presence
                pass

        except Exception as e:
            print(f"Proctoring Error: {e}")
            # violations.append("Processing Error")

        return {
            "status": status,
            "violations": violations,
            "timestamp": time.time()
        }

    def analyze_session(self, session_id):
        """
        Aggregate logs for a session
        """
        pass

class ProctoringService:
    _instance = None
    
    @staticmethod
    def get_instance():
        if ProctoringService._instance is None:
            ProctoringService._instance = ProctoringEngine()
        return ProctoringService._instance
