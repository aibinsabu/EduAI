import sys
import os
import cv2
import numpy as np
import base64
import json

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "water_quality.settings")
import django
django.setup()

def generate_dummy_frame():
    # Create a 640x480 gray image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a white circle to represent a "face" area (though MediaPipe needs real landmarks)
    cv2.circle(img, (320, 240), 100, (255, 255, 255), -1)
    
    _, buffer = cv2.imencode('.jpg', img)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return "data:image/jpeg;base64," + jpg_as_text

try:
    from quality_app.ai_modules.calibration_model import get_calibration_engine
    
    print("--- FULL AI CYCLE TEST ---")
    engine = get_calibration_engine()
    
    dummy_frame = generate_dummy_frame()
    
    print("Testing analyze_frame with dummy data...")
    # This will trigger face_mesh.process()
    result = engine.analyze_frame(dummy_frame, strict=False)
    
    print(f"Result Status: {result.get('status')}")
    print(f"Result Message: {result.get('message')}")
    
    if result.get('status') == "Error":
         print("\nFAILED: The AI Engine returned an Error during processing.")
         sys.exit(1)
    else:
         print("\nSUCCESS: The AI Engine processed the frame without crashing.")

except Exception as e:
    print(f"\nCRITICAL FAILURE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
