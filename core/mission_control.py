import time
from enum import Enum

class MissionState(Enum):
    SCAN = "SCAN"           # Searching for new threats
    TRACK = "TRACK"         # Focusing on identified targets
    ENGAGE = "ENGAGE"       # Active EA/Jamming countermeasures
    EVALUATE = "EVALUATE"   # Battle Damage Assessment (BDA)

class MissionStateMachine:
    """Manages high-level strategic states of the autonomous mission.
    
    Implements transition logic between discovery, tracking, and engagement phases.
    """
    def __init__(self):
        self.current_state = MissionState.SCAN
        self.target_track_id = None
        self.target_track_ids = []  # Multi-target support (V1.0)
        self.state_start_time = time.time()
        self.engagement_count = 0
        self.bda_cycles = 0

    def get_state_info(self):
        return {
            "state": self.current_state.value,
            "target": self.target_track_id,
            "targets_count": len(self.target_track_ids),
            "duration": round(time.time() - self.state_start_time, 1)
        }

    def update(self, detected_tracks):
        """Processes the latest detections and decides on state transitions."""
        num_targets = len(detected_tracks)
        
        # Update multi-target list (top 3 by threat)
        sorted_tracks = sorted(detected_tracks, key=lambda x: self._threat_to_score(x.get("threat_level", "LOW")), reverse=True)
        self.target_track_ids = [t.get("track_id") for t in sorted_tracks[:3]]
        
        if self.current_state == MissionState.SCAN:
            if num_targets > 0:
                highest_threat = sorted_tracks[0]
                self.target_track_id = highest_threat.get("track_id")
                self._transition_to(MissionState.TRACK)

        elif self.current_state == MissionState.TRACK:
            if num_targets == 0:
                self._transition_to(MissionState.SCAN)
            elif self.target_track_id not in [t.get("track_id") for t in detected_tracks]:
                self._transition_to(MissionState.SCAN)
            else:
                self._transition_to(MissionState.ENGAGE)

        elif self.current_state == MissionState.ENGAGE:
            engagement_duration = time.time() - self.state_start_time
            if engagement_duration > 5.0:  # Stay longer for multi-target cycles
                self._transition_to(MissionState.EVALUATE)

        elif self.current_state == MissionState.EVALUATE:
            self.bda_cycles += 1
            if self.bda_cycles >= 2:
                self.bda_cycles = 0
                target_present = any(t.get("track_id") == self.target_track_id for t in detected_tracks)
                if target_present:
                    self._transition_to(MissionState.ENGAGE)
                else:
                    self._transition_to(MissionState.SCAN)

        return self.current_state

    def _transition_to(self, new_state):
        if self.current_state != new_state:
            # print(f"[MissionSM] Transition: {self.current_state.value} -> {new_state.value}")
            self.current_state = new_state
            self.state_start_time = time.time()
            if new_state == MissionState.SCAN:
                self.target_track_id = None

    def _threat_to_score(self, level):
        return {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(level, 0)
