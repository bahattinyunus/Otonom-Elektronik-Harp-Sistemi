import time

class SmartOptimizer:
    """Optimizes Electronic Attack (EA) strategy using Look-Through logic."""
    
    def __init__(self):
        self.jamming_active = False
        self.look_through_interval = 2.0  # Seconds
        self.jam_duration = 5.0  # Seconds
        self.last_switch_time = time.time()
        self.status = "Passive"

    def update_strategy(self, current_detections):
        """Decides whether to jam or look-through based on time and detections."""
        now = time.time()
        
        if self.jamming_active:
            if now - self.last_switch_time > self.jam_duration:
                # Switch to Look-Through
                self.jamming_active = False
                self.last_switch_time = now
                self.status = "Looking-Through (Scanning)"
        else:
            if now - self.last_switch_time > self.look_through_interval:
                # Switch back to Jamming if signals exist
                if len(current_detections) > 0:
                    self.jamming_active = True
                    self.status = f"Jamming {len(current_detections)} Targets"
                else:
                    self.status = "Standby (No Targets)"
                self.last_switch_time = now
                
        return {
            "is_jamming": self.jamming_active,
            "status": self.status,
            "target_count": len(current_detections)
        }
