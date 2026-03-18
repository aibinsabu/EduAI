import sys
import os
sys.path.insert(0, r"d:\New folder (2)\project\edu")
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu.settings")
django.setup()

from quality_app.ai_modules.calibration_model import get_calibration_engine

try:
    print("Initializing...")
    engine = get_calibration_engine()
    print("Initialized.")
    
    # Try a fake frame
    import base64
    import numpy as np
    import cv2
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', img)
    b64_str = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
    
    print("Analyzing...")
    res = engine.analyze_frame(b64_str)
    print("Result:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
