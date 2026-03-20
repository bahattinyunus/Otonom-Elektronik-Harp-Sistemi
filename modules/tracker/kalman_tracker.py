import math
import numpy as np
from core.config import (KALMAN_PROCESS_NOISE_FREQ, KALMAN_PROCESS_NOISE_AOA,
                          KALMAN_MEAS_NOISE_FREQ, KALMAN_MEAS_NOISE_AOA,
                          TRACKER_DISTANCE_THRESHOLD, TRACKER_MAX_AGE)


class KalmanFilter1D:
    """Constant-velocity Kalman filter for a single scalar dimension."""

    def __init__(self, initial_pos, process_noise=1.0, meas_noise=5.0):
        self.x = np.array([initial_pos, 0.0], dtype=float)
        self.P = np.eye(2) * 100.0
        self.F = np.array([[1.0, 1.0], [0.0, 1.0]])
        self.H = np.array([[1.0, 0.0]])
        self.Q = np.diag([process_noise, process_noise * 0.1])
        self.R = np.array([[meas_noise]])

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[0]

    def update(self, measurement, is_angle=False):
        if is_angle:
            y_val = (measurement - self.H @ self.x + 180) % 360 - 180
            y = np.array([y_val])
        else:
            y = measurement - self.H @ self.x
            
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T / S[0, 0]
        self.x = self.x + (K * y[0]).flatten()
        
        if is_angle:
            self.x[0] = self.x[0] % 360
            
        self.P = (np.eye(2) - np.outer(K, self.H)) @ self.P
        return self.x[0]

    @property
    def velocity(self):
        return float(self.x[1])


class KalmanTracker:
    """Track-While-Scan using per-target 1D Kalman filters for frequency and AoA."""

    def __init__(self,
                 distance_threshold=TRACKER_DISTANCE_THRESHOLD,
                 max_age=TRACKER_MAX_AGE):
        self.tracks = {}
        self.next_id = 1
        self.distance_threshold = distance_threshold
        self.max_age = max_age

    def _predict_state(self, track):
        track['kf_freq'].predict()
        track['kf_aoa'].predict()

    def _distance(self, det, track):
        freq_pred = track['kf_freq'].x[0]
        aoa_pred  = track['kf_aoa'].x[0]
        freq_diff = abs(det['freq_idx'] - freq_pred) * 0.5
        aoa_diff  = min(abs(det['aoa'] - aoa_pred), 360.0 - abs(det['aoa'] - aoa_pred))
        return math.sqrt(freq_diff ** 2 + aoa_diff ** 2)

    def update(self, detections):
        for track in self.tracks.values():
            self._predict_state(track)

        updated_ids = set()
        results = []

        for det in detections:
            best_id   = None
            min_dist  = float('inf')
            for tid, tdata in self.tracks.items():
                if tid in updated_ids:
                    continue
                d = self._distance(det, tdata)
                if d < min_dist and d < self.distance_threshold:
                    min_dist = d
                    best_id  = tid

            if best_id is not None:
                t = self.tracks[best_id]
                t['kf_freq'].update(float(det['freq_idx']))
                filtered_aoa = t['kf_aoa'].update(float(det['aoa']), is_angle=True)
                t['age'] = 0
                t['hit_count'] = t.get('hit_count', 0) + 1
                updated_ids.add(best_id)
                det['track_id']      = f"TRK-{best_id:04d}"
                det['track_hits']    = t['hit_count']
                det['aoa']           = round(filtered_aoa, 1)
                det['freq_velocity'] = round(t['kf_freq'].velocity, 3)
            else:
                nid = self.next_id
                self.next_id += 1
                self.tracks[nid] = {
                    'age': 0,
                    'hit_count': 1,
                    'kf_freq': KalmanFilter1D(
                        float(det['freq_idx']),
                        process_noise=KALMAN_PROCESS_NOISE_FREQ,
                        meas_noise=KALMAN_MEAS_NOISE_FREQ,
                    ),
                    'kf_aoa': KalmanFilter1D(
                        float(det['aoa']),
                        process_noise=KALMAN_PROCESS_NOISE_AOA,
                        meas_noise=KALMAN_MEAS_NOISE_AOA,
                    ),
                }
                updated_ids.add(nid)
                det['track_id']      = f"TRK-{nid:04d}"
                det['track_hits']    = 1
                det['freq_velocity'] = 0.0

            results.append(det)

        for tid in list(self.tracks.keys()):
            if tid not in updated_ids:
                self.tracks[tid]['age'] += 1
                if self.tracks[tid]['age'] > self.max_age:
                    del self.tracks[tid]

        return results
