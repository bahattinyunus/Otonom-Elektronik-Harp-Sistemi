import numpy as np
import cv2

class WaterfallDetector:
    """Detects signals using OpenCV contour analysis on the 2D waterfall map."""
    def __init__(self, threshold_db=15, history_len=12):
        self.threshold = threshold_db
        self.history_len = history_len
        self.history = []
        
    def detect(self, psd_frame, noise_floor):
        detections = []
        
        # 1. Maintain 2D history buffer
        self.history.append(psd_frame)
        if len(self.history) > self.history_len:
            self.history.pop(0)
            
        if len(self.history) < 3:
            return detections # Need a few frames to run 2D CV reliably
            
        # 2. Convert to 2D numpy array and normalize to uint8 grayscale image
        mat = np.array(self.history)
        
        # Subtract noise floor to get pure SNR
        mat_snr = np.maximum(mat - noise_floor, 0)
        
        # Scale SNR (0 to 60dB) to Pixel intensity (0 to 255)
        img = np.clip(mat_snr * (255.0 / 60.0), 0, 255).astype(np.uint8)
        
        # 3. Apply OpenCV thresholding
        thresh_val = self.threshold * (255.0 / 60.0)
        _, thresh_img = cv2.threshold(img, thresh_val, 255, cv2.THRESH_BINARY)
        
        # Optional: Morphological operations could go here to bridge gaps
        # thresh_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
        
        # 4. Find Contours (Signal Blobs)
        contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Only consider contours that hit the latest time frame (bottom edge of image)
            # y + h == length of history
            if (y + h) >= len(self.history) - 1 and w > 2:
                # Calculate max SNR within the signal bounding box
                box_snr = np.max(mat_snr[y:y+h, x:x+w])
                
                detections.append({
                    "center_idx": x + w // 2,
                    "bandwidth_idx": w,
                    "snr": float(box_snr) # Cast float32 to python float for JSON serialization
                })
                
        return detections
