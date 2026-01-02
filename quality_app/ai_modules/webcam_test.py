import cv2
import base64
from proctoring_model import ProctoringService

# Initialize webcam
cap = cv2.VideoCapture(0)

# Get Proctoring Engine instance
engine = ProctoringService.get_instance()

print("Press 'q' to quit...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Encode frame to base64
    _, buffer = cv2.imencode(".jpg", frame)
    frame_base64 = base64.b64encode(buffer).decode("utf-8")

    frame_data = f"data:image/jpeg;base64,{frame_base64}"

    # Process frame
    result = engine.process_frame(frame_data)

    # Print result
    print(result)

    # Show webcam preview
    cv2.imshow("Live Proctoring Feed", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
