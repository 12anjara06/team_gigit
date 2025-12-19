import cv2
import numpy as np
import base64
import face_recognition
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import function to test - need to mock or just copy it here for isolated testing
# For simplicity, I'll copy the logic we just implemented to verify it works with face_recognition
def data_uri_to_cv2_img_simulated(img_bgr):
    # Simulate processing: BGR -> RGB -> Contiguous
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_rgb = np.ascontiguousarray(img_rgb)
    return img_rgb

def test_fix():
    print("Creating dummy BGR image...")
    # Create a dummy image (100x100, 3 channels, BGR)
    # Just a black square with a white rectangle (simulating a "face" roughly for image structure)
    img_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img_bgr, (20, 20), (80, 80), (255, 255, 255), -1)
    
    print("Simulating conversions...")
    # 1. Normal conversion
    img_rgb = data_uri_to_cv2_img_simulated(img_bgr)
    
    print(f"Image shape: {img_rgb.shape}, dtype: {img_rgb.dtype}")
    print(f"Flags: {img_rgb.flags}")
    print(f"Strides: {img_rgb.strides}")
    print(f"Itemsize: {img_rgb.itemsize}")
    
    # Try forcing uint8 again just in case
    img_rgb = img_rgb.astype('uint8')
    
    # Debug: Save and reload to compare
    cv2.imwrite('debug_face.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
    loaded_img = face_recognition.load_image_file('debug_face.jpg')
    
    print("\n--- COMPARISON ---")
    print(f"Constructed: shape={img_rgb.shape}, dtype={img_rgb.dtype}, flags={img_rgb.flags}")
    print(f"Loaded:      shape={loaded_img.shape}, dtype={loaded_img.dtype}, flags={loaded_img.flags}")
    
    try:
        print("\nAttempting loaded image...")
        face_recognition.face_encodings(loaded_img)
        print("Loaded image works!")
    except Exception as e:
        print(f"Loaded image FAILED: {e}")

    try:
        print("\nAttempting constructed image...")
        face_recognition.face_encodings(img_rgb)
        print("Constructed image works!")
    except Exception as e:
        print(f"Constructed image FAILED: {e}")

if __name__ == "__main__":
    test_fix()
