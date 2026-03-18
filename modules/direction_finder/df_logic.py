import random
import numpy as np

class DirectionFinder:
    """Estimates the Angle of Arrival (AoA) for a signal based on TDOA logic."""
    def __init__(self):
        self.antenna_spacing = 0.5 # meters
        self.speed_of_light = 3e8

    def estimate_aoa(self, detection):
        # Mocks TDOA/Phase Difference calculation
        # We use the center_idx as a unique-ish identifier to keep AoA stable for the same signal
        # and add slight noise to simulate measurement error.
        
        base_angle = (detection['center_idx'] * 137.5) % 360  # Golden ratio dispersion
        noise = np.random.normal(0, 2.0) # +/- 2 degrees error
        
        estimated_aoa = (base_angle + noise) % 360
        return estimated_aoa
