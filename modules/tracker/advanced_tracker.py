import numpy as np
from core.config import (KALMAN_PROCESS_NOISE_FREQ, KALMAN_PROCESS_NOISE_AOA,
                          KALMAN_MEAS_NOISE_FREQ, KALMAN_MEAS_NOISE_AOA,
                          TRACKER_DISTANCE_THRESHOLD, TRACKER_MAX_AGE)

class UKF1D:
    """1D Unscented Kalman Filter for non-linear state estimation."""
    def __init__(self, initial_pos, q=1.0, r=5.0):
        self.dim = 2 # pos, vel
        self.x = np.array([initial_pos, 0.0])
        self.P = np.eye(self.dim) * 10.0
        self.Q = np.diag([q, q * 0.1])
        self.R = np.array([[r]])
        
        # UKF Parameters
        self.alpha = 0.001
        self.beta = 2.0
        self.kappa = 0.0
        self.lambd = self.alpha**2 * (self.dim + self.kappa) - self.dim
        
        # Weights
        self.Wm = np.zeros(2 * self.dim + 1)
        self.Wc = np.zeros(2 * self.dim + 1)
        self.Wm[0] = self.lambd / (self.dim + self.lambd)
        self.Wc[0] = self.lambd / (self.dim + self.lambd) + (1 - self.alpha**2 + self.beta)
        for i in range(1, 2 * self.dim + 1):
            self.Wm[i] = 1 / (2 * (self.dim + self.lambd))
            self.Wc[i] = 1 / (2 * (self.dim + self.lambd))

    def _generate_sigma_points(self, x, P):
        n = len(x)
        points = np.zeros((2 * n + 1, n))
        points[0] = x
        U = np.linalg.cholesky((n + self.lambd) * P)
        for i in range(n):
            points[i+1] = x + U[i]
            points[i+n+1] = x - U[i]
        return points

    def predict(self):
        # State transition function (Constant Velocity)
        def f(x):
            return np.array([x[0] + x[1], x[1]])

        sigmas = self._generate_sigma_points(self.x, self.P)
        sigmas_f = np.array([f(s) for s in sigmas])
        
        # Predicted state mean
        self.x = np.sum(self.Wm[:, None] * sigmas_f, axis=0)
        
        # Predicted state covariance
        self.P = self.Q.copy()
        for i in range(2 * self.dim + 1):
            y = sigmas_f[i] - self.x
            self.P += self.Wc[i] * np.outer(y, y)
            
        return self.x[0]

    def update(self, measurement):
        # Measurement function (Identity for position)
        def h(x):
            return np.array([x[0]])

        sigmas_f = self._generate_sigma_points(self.x, self.P)
        sigmas_h = np.array([h(s) for s in sigmas_f])
        
        # Mean of predicted measurement
        z_pred = np.sum(self.Wm[:, None] * sigmas_h, axis=0)
        
        # Covariance of predicted measurement
        P_zz = self.R.copy()
        for i in range(2 * self.dim + 1):
            y = sigmas_h[i] - z_pred
            P_zz += self.Wc[i] * np.outer(y, y)
            
        # Cross-covariance
        P_xz = np.zeros((self.dim, 1))
        for i in range(2 * self.dim + 1):
            P_xz += self.Wc[i] * np.outer(sigmas_f[i] - self.x, sigmas_h[i] - z_pred)
            
        # Kalman gain
        K = P_xz @ np.linalg.inv(P_zz)
        
        # State update
        y = measurement - z_pred
        self.x = self.x + (K @ y).flatten()
        self.P = self.P - K @ P_zz @ K.T
        
        return self.x[0]

class AdvancedTracker:
    """Enterprise Tracker using Unscented Kalman Filters."""
    def __init__(self, dist_thresh=TRACKER_DISTANCE_THRESHOLD, max_age=TRACKER_MAX_AGE):
        self.tracks = {}
        self.next_id = 1
        self.dist_thresh = dist_thresh
        self.max_age = max_age

    def update(self, detections):
        for t in self.tracks.values():
            t['kf_freq'].predict()
            t['kf_aoa'].predict()

        updated_ids = set()
        results = []

        for det in detections:
            best_id, min_dist = None, float('inf')
            for tid, tdata in self.tracks.items():
                if tid in updated_ids: continue
                fd = abs(det['freq_idx'] - tdata['kf_freq'].x[0]) * 0.5
                ad = min(abs(det['aoa'] - tdata['kf_aoa'].x[0]), 360 - abs(det['aoa'] - tdata['kf_aoa'].x[0]))
                d = np.sqrt(fd**2 + ad**2)
                if d < min_dist and d < self.dist_thresh:
                    min_dist, best_id = d, tid

            if best_id is not None:
                t = self.tracks[best_id]
                t['kf_freq'].update(float(det['freq_idx']))
                filt_aoa = t['kf_aoa'].update(float(det['aoa']))
                t['age'], t['hits'] = 0, t.get('hits', 0) + 1
                updated_ids.add(best_id)
                det.update({'track_id': f"TRK-{best_id:04d}", 'track_hits': t['hits'], 'aoa': round(filt_aoa, 1)})
            else:
                nid = self.next_id
                self.next_id += 1
                self.tracks[nid] = {
                    'age': 0, 'hits': 1,
                    'kf_freq': UKF1D(det['freq_idx'], KALMAN_PROCESS_NOISE_FREQ, KALMAN_MEAS_NOISE_FREQ),
                    'kf_aoa': UKF1D(det['aoa'], KALMAN_PROCESS_NOISE_AOA, KALMAN_MEAS_NOISE_AOA)
                }
                updated_ids.add(nid)
                det.update({'track_id': f"TRK-{nid:04d}", 'track_hits': 1})
            results.append(det)

        for tid in list(self.tracks.keys()):
            if tid not in updated_ids:
                self.tracks[tid]['age'] += 1
                if self.tracks[tid]['age'] > self.max_age: del self.tracks[tid]
        return results
