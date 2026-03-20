import numpy as np
from core.config import CENTER_FREQ


class DirectionFinder:
    """4-element ULA Direction Finder using phase-difference TDOA simulation.

    Models a Uniform Linear Array (ULA) with half-wavelength element spacing.
    Phase differences between adjacent elements are computed from the signal's
    ground-truth frequency index, then corrupted with SNR-dependent noise,
    and finally inverted to produce an AoA estimate with a confidence score.
    """

    def __init__(self, n_elements: int = 4):
        self.n_elements  = n_elements
        self.c           = 3e8
        self.center_freq = CENTER_FREQ

    def estimate_aoa(self, detection: dict):
        freq_hz    = detection.get("freq_mhz", self.center_freq / 1e6) * 1e6
        wavelength = self.c / freq_hz
        d          = wavelength / 2.0        # Half-wavelength spacing

        # Deterministic ground-truth angle (stable per freq_idx)
        true_aoa_deg = (detection["center_idx"] * 137.5) % 360
        true_theta   = np.deg2rad(true_aoa_deg)

        snr = max(detection.get("snr", 5.0), 0.5)

        # Expected inter-element phase difference for ULA broadside
        expected_pd = 2.0 * np.pi * d * np.cos(true_theta) / wavelength

        # Simulate n_elements-1 noisy phase measurements
        noise_std    = np.pi / max(snr * 0.4, 1.0)
        measurements = expected_pd + np.random.normal(0.0, noise_std, self.n_elements - 1)
        avg_phase    = float(np.mean(measurements))

        # Invert phase → angle estimate
        cos_val   = np.clip(avg_phase * wavelength / (2.0 * np.pi * d), -1.0, 1.0)
        theta_est = float(np.rad2deg(np.arccos(cos_val)))   # [0, 180]

        # Resolve 180° ambiguity using sign of sine component
        aoa_est = (360.0 - theta_est) % 360.0 if np.sin(true_theta) < 0 else theta_est % 360.0

        # Small residual measurement noise
        aoa_est = (aoa_est + np.random.normal(0.0, max(0.3, 2.0 / snr))) % 360.0

        # Confidence increases with SNR, caps at 0.98
        confidence = round(min(0.98, 0.40 + 0.025 * min(snr, 24.0)), 3)

        return round(aoa_est, 2), confidence
