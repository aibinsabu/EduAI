
import os
import django
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_quality.settings')
django.setup()

print("[OK] Django Environment Setup Complete")

try:
    print("\n--- Testing Proctoring Service ---")
    from quality_app.ai_modules.proctoring_model import ProctoringService
    # Reset first to be clean
    ProctoringService.reset_instance()
    
    # Lazy load check
    print("Initializing Proctoring Service...")
    ps = ProctoringService.get_instance()
    print("Proctoring Service Initialized.")
    
    # Dummy Frame Check (White image)
    import base64
    import numpy as np
    import cv2
    
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', dummy_img)
    b64 = base64.b64encode(buf).decode('utf-8')
    
    print("Testing process_frame...")
    try:
        ps.process_frame(b64, {"calibrated": True, "base_pitch":0, "base_yaw":0})
        print("[OK] Proctoring Service: process_frame OK")
    except Exception as e:
        print(f"[FAIL] Proctoring Service Failed: {e}")

except Exception as e:
    print(f"[FAIL] Proctoring Import/Init Failed: {e}")


try:
    print("\n--- Testing Grading Service ---")
    from quality_app.ai_modules.grading_model import GradingService
    print("Initializing Grading Service...")
    gs = GradingService.get_instance()
    
    print("Testing grade_submission...")
    res = gs.grade_submission("The capital of France is Paris", "Paris", "Paris")
    print(f"Grading Result: {res}")
    
    if res['score'] > 0:
        print("[OK] Grading Service: Logic OK")
    else:
        print("[WARN] Grading Service: Low Score (Check Model)")

except Exception as e:
    print(f"[FAIL] Grading Service Failed: {e}")

try:
    print("\n--- Testing Question Generation ---")
    from quality_app.ai_modules import generate_questions
    print("Testing QG...")
    
    # Mock QG logic if it's too heavy to run full T5, but let's try
    # It might be slow.
    q = generate_questions("Deep learning is a subset of machine learning.", max_questions=1)
    print(f"Generated: {q}")
    print("[OK] Question Generation: OK")

except Exception as e:
    print(f"[FAIL] QG Failed: {e}")

print("\n--- Verification Complete ---")
