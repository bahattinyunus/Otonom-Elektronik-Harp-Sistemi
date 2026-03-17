import numpy as np
import time
from core.config import SAMPLING_RATE, CENTER_FREQ, FFT_SIZE, NOISE_FLOOR

class RFEnvironment:
    """Simulates a live RF spectrum with multiple active signals and noise."""
    
    def __init__(self):
        self.center_freq = CENTER_FREQ
        self.fs = SAMPLING_RATE
        self.fft_size = FFT_SIZE
        self.noise_floor = NOISE_FLOOR
        self.active_signals = []
        
    def generate_spectrum_frame(self):
        """Generates one frame of FFT magnitude data (Power Spectral Density)."""
        # Base noise
        noise = np.random.normal(0, 1, self.fft_size) + 1j * np.random.normal(0, 1, self.fft_size)
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(noise, n=self.fft_size)))**2 + 1e-12)
        psd += self.noise_floor
        
        # Add random signals for simulation
        if np.random.rand() > 0.95:  # 5% chance to spawn a new signal
            self._spawn_random_signal()
            
        # Apply active signals to PSD
        for sig in self.active_signals[:]:
            # Simple gaussian-like signal peak
            freq_idx = int((sig['freq'] - (self.center_freq - self.fs/2)) / (self.fs / self.fft_size))
            if 0 <= freq_idx < self.fft_size:
                width = sig['bw'] / (self.fs / self.fft_size)
                x = np.arange(self.fft_size)
                peak = sig['amplitude'] * np.exp(-((x - freq_idx)**2) / (2 * (width/2)**2))
                psd = np.maximum(psd, self.noise_floor + peak)
                
            # Signal duration decay
            sig['duration'] -= 0.1
            if sig['duration'] <= 0:
                self.active_signals.remove(sig)
                
        return psd.tolist()

    def _spawn_random_signal(self):
        """Creates a dummy signal entry for simulation."""
        mod_types = ["BPSK", "QPSK", "AM", "FM", "LoRa"]
        freq_offset = (np.random.rand() - 0.5) * (self.fs * 0.8)
        self.active_signals.append({
            "freq": self.center_freq + freq_offset,
            "bw": np.random.uniform(10e3, 100e3),
            "amplitude": np.random.uniform(20, 60),
            "type": np.random.choice(mod_types),
            "duration": np.random.uniform(1, 5)
        })

if __name__ == "__main__":
    env = RFEnvironment()
    print("Simulating environment...")
    frame = env.generate_spectrum_frame()
    print(f"Generated frame of size: {len(frame)}")
