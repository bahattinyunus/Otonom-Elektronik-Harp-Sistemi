import time

class SmartOptimizer:
    """Optimizes Electronic Attack (EA) strategy using Look-Through logic."""
    
    def __init__(self):
        self.jamming_active = False
        self.look_through_interval = 2.0  # Seconds
        self.jam_duration = 5.0  # Seconds
        self.last_switch_time = time.time()
        self.status = "Passive"
        self.total_reward = 0
        self.episode_count = 0
        self.last_target_count = 0

    def update_strategy(self, current_detections):
        """Decides whether to jam or look-through based on time and detections."""
        now = time.time()
        current_target_count = len(current_detections)
        reward_delta = 0
        
        if self.jamming_active:
            if now - self.last_switch_time > self.jam_duration:
                # Switch to Look-Through
                self.jamming_active = False
                self.last_switch_time = now
                self.status = "Looking-Through (Scanning)"
                
                # Check reward: If we jammed and targets disappeared or dropped, positive reward
                if current_target_count < self.last_target_count:
                    reward_delta = 10 * (self.last_target_count - current_target_count)  # Good
                elif current_target_count == self.last_target_count and self.last_target_count > 0:
                    reward_delta = -2  # Wasted energy, target still there
                else:
                    reward_delta = -5  # Target increased or we jammed nothing
                    
                self.total_reward += reward_delta
                self.episode_count += 1
        else:
            self.last_target_count = current_target_count
            if now - self.last_switch_time > self.look_through_interval:
                # Switch back to Jamming if signals exist
                if current_target_count > 0:
                    self.jamming_active = True
                    self.status = f"Jamming {current_target_count} Targets"
                else:
                    self.status = "Standby (No Targets)"
                self.last_switch_time = now
                
        return {
            "is_jamming": self.jamming_active,
            "status": self.status,
            "target_count": current_target_count,
            "reward": self.total_reward,
            "latest_reward_delta": reward_delta
        }
