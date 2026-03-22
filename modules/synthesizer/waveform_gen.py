import numpy as np
from datetime import datetime

class WaveformSynthesizer:
    """Cognitive Waveform Synthesizer for LPI and Deceptive EW."""
    
    def __init__(self, sample_rate: float = 2e6):
        self.sample_rate = sample_rate
        self.active_phantoms = []

    def generate_lpi_noise(self, center_freq: float, bw: float, duration: float = 0.1):
        """Generates a Low Probability of Intercept (LPI) spread spectrum noise signal."""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        # Baseband noise
        noise = (np.random.randn(len(t)) + 1j*np.random.randn(len(t)))
        # Filter noise to requested bandwidth (simplified)
        # Shift to center frequency
        phase = 2 * np.pi * center_freq * t
        lpi_signal = (noise * np.exp(1j * phase)).real
        # Scale to very low SNR (LPI property)
        lpi_signal *= 0.1 
        return lpi_signal

    def create_phantom_target(self, target_id: str, freq: float, power: float):
        """Registers a deceptive phantom target in the synthesizer."""
        phantom = {
            "id": f"GHOST_{target_id}",
            "freq": freq,
            "power": power,
            "start_time": datetime.now()
        }
        self.active_phantoms.append(phantom)
        return phantom

    def get_spectrum_overlay(self, num_points: int = 512, f_start: float = 0, f_end: float = 2e6):
        """Generates a PSD overlay representing current phantom targets."""
        overlay = np.zeros(num_points)
        freq_axis = np.linspace(f_start, f_end, num_points)
        
        for p in self.active_phantoms:
            # Lorentzian or Gaussian peak for the phantom
            idx = np.abs(freq_axis - p["freq"]).argmin()
            # Spread power over a few bins
            sigma = 2 
            dist = np.arange(num_points) - idx
            peak = p["power"] * np.exp(-0.5 * (dist / sigma)**2)
            overlay += peak
            
        return overlay.tolist()

    def clear_phantoms(self):
        self.active_phantoms = []

if __name__ == "__main__":
    synth = WaveformSynthesizer()
    synth.create_phantom_target("RADAR_1", 1000000, 25.0)
    overlay = synth.get_spectrum_overlay(512, 0, 2000000)
    print(f"Max Overlay Power: {max(overlay):.2f}")
