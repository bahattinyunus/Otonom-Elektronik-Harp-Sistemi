import numpy as np

class WaterfallDetector:
    """Detects signals that exceed the noise floor in the waterfall data."""
    def __init__(self, threshold_db=15):
        self.threshold = threshold_db
        
    def detect(self, psd_frame, noise_floor):
        detections = []
        # Simple threshold crossing detection
        # In a real system, this would be a CV model on the spectrogram
        peaks = np.where(np.array(psd_frame) > (noise_floor + self.threshold))[0]
        
        if len(peaks) > 0:
            # Group contiguous peaks into signal blocks
            blocks = np.split(peaks, np.where(np.diff(peaks) > 5)[0] + 1)
            for b in blocks:
                center_idx = int(np.mean(b))
                detections.append({
                    "center_idx": center_idx,
                    "bandwidth_idx": len(b),
                    "snr": np.max(np.array(psd_frame)[b]) - noise_floor
                })
        return detections
