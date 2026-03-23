import numpy as np
import cv2

class WaterfallDetector:
    """Detects signals using a hybrid approach: Fast 1D Peak Detection + 2D Contour Verification."""
    def __init__(self, threshold_db=15, history_len=3):
        self.threshold = threshold_db
        self.history_len = history_len # Reduced from 12 to 3 for low latency
        self.history = []
        
    def detect(self, psd_frame, noise_floor):
        detections = []
        
        # 1. Maintain 2D history buffer (Minimal for CV requirements)
        self.history.append(psd_frame)
        if len(self.history) > self.history_len:
            self.history.pop(0)
            
        # 2. Fast 1D Detection (Zero Latency Path)
        # Use only the latest frame for immediate discovery
        latest_psd = np.array(psd_frame)
        snr_1d = latest_psd - noise_floor
        mask_1d = snr_1d > self.threshold
        
        # 3. Computer Vision Processing (Verification Path)
        if len(self.history) >= self.history_len:
            mat = np.array(self.history)
            mat_snr = np.maximum(mat - noise_floor, 0)
            img = np.clip(mat_snr * (255.0 / 60.0), 0, 255).astype(np.uint8)
            
            thresh_img = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY, 11, -self.threshold * (255.0 / 60.0)
            )
            
            kernel = np.ones((3, 3), np.uint8)
            thresh_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                # If it's in the latest frame and has some width
                if (y + h) >= len(self.history) - 1 and w > 1:
                    box_snr = np.max(mat_snr[y:y+h, x:x+w])
                    detections.append({
                        "center_idx": x + w // 2,
                        "bandwidth_idx": w,
                        "snr": float(box_snr)
                    })
        
        # If CV failed or was too slow, use 1D thresholding as fallback (simple clustering)
        if not detections and np.any(mask_1d):
            # Simple grouping of adjacent triggered bins
            indices = np.where(mask_1d)[0]
            if len(indices) > 0:
                groups = np.split(indices, np.where(np.diff(indices) > 2)[0] + 1)
                for g in groups:
                    if len(g) > 2:
                        detections.append({
                            "center_idx": int(np.mean(g)),
                            "bandwidth_idx": len(g),
                            "snr": float(np.max(snr_1d[g]))
                        })
                        
        return detections
