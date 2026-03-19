import time
import math

class KalmanTracker:
    """ Tracks detected emitters over time using a simple distance-based correlation mechanism
        (simplified alpha-beta tracker for AoA and Frequency). """
    def __init__(self, distance_threshold=20.0, max_age=5):
        self.tracks = {}  # key: track_id, value: track_data
        self.next_id = 1
        self.distance_threshold = distance_threshold
        self.max_age = max_age

    def _distance(self, sig1, sig2):
        # Normalize diffs to get a comparable distance metric
        freq_diff = abs(sig1['freq_idx'] - sig2['freq_idx']) * 0.5
        # Shortest angular distance for AoA
        aoa_diff = min(abs(sig1['aoa'] - sig2['aoa']), 360 - abs(sig1['aoa'] - sig2['aoa']))
        return math.sqrt(freq_diff**2 + aoa_diff**2)

    def update(self, detections):
        """ Correlates new detections with existing tracks. """
        updated_tracks = set()
        results = []

        for det in detections:
            best_match_id = None
            min_dist = float('inf')

            for tid, tdata in self.tracks.items():
                if tid in updated_tracks:
                    continue
                dist = self._distance(det, tdata['last_state'])
                if dist < min_dist and dist < self.distance_threshold:
                    min_dist = dist
                    best_match_id = tid

            if best_match_id is not None:
                # Update existing track
                self.tracks[best_match_id]['age'] = 0
                self.tracks[best_match_id]['last_state'] = det
                updated_tracks.add(best_match_id)
                det['track_id'] = f"TRK-{best_match_id:04d}"
            else:
                # Create new track
                new_id = self.next_id
                self.next_id += 1
                self.tracks[new_id] = {
                    'age': 0,
                    'last_state': det
                }
                updated_tracks.add(new_id)
                det['track_id'] = f"TRK-{new_id:04d}"
                
            results.append(det)

        # Age missing tracks
        for tid in list(self.tracks.keys()):
            if tid not in updated_tracks:
                self.tracks[tid]['age'] += 1
                if self.tracks[tid]['age'] > self.max_age:
                    del self.tracks[tid]
                    
        return results
