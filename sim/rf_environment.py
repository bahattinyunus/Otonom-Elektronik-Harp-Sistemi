import numpy as np
import random
import time
from core.config import SAMPLING_RATE, CENTER_FREQ, FFT_SIZE, NOISE_FLOOR


class RFEnvironment:
    """Simulates a live RF spectrum with multiple active signals, noise, and jamming feedback."""

    def __init__(self):
        self.center_freq = CENTER_FREQ
        self.fs          = SAMPLING_RATE
        self.fft_size    = FFT_SIZE
        self.noise_floor = NOISE_FLOOR
        self.active_signals = []
        self.jamming_action = "STANDBY"

    def set_jamming(self, action):
        self.jamming_action = action

    def generate_spectrum_frame(self):
        noise = (np.random.normal(0, 1, self.fft_size) +
                 1j * np.random.normal(0, 1, self.fft_size))
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(noise, n=self.fft_size))) ** 2 + 1e-12)
        psd += self.noise_floor

        if np.random.rand() > 0.93:
            self._spawn_random_signal()

        for sig in self.active_signals[:]:
            if sig.get('hopping', False) and np.random.rand() > 0.8:
                hop_offset = (np.random.rand() - 0.5) * (self.fs * 0.8)
                sig['freq'] = self.center_freq + hop_offset

            fading = 1.0 + 0.2 * np.sin(time.time() * 10.0 + sig.get('phase_offset', 0))
            current_amp = sig['amplitude'] * fading

            freq_idx = int((sig['freq'] - (self.center_freq - self.fs / 2)) / (self.fs / self.fft_size))
            if 0 <= freq_idx < self.fft_size:
                width = sig['bw'] / (self.fs / self.fft_size)
                x     = np.arange(self.fft_size)
                peak  = current_amp * np.exp(-((x - freq_idx) ** 2) / (2 * (width / 2) ** 2))
                psd   = np.maximum(psd, self.noise_floor + peak)

            sig['duration'] -= 0.1
            if sig['duration'] <= 0:
                self.active_signals.remove(sig)

        psd = self._apply_jamming(psd)
        return psd.tolist()

    def _apply_jamming(self, psd):
        action = self.jamming_action
        if action == "JAM_BARRAGE":
            jam_noise = np.random.uniform(12, 22, self.fft_size)
            psd = psd + jam_noise
        elif action == "JAM_SPOT":
            for sig in self.active_signals:
                freq_idx = int((sig['freq'] - (self.center_freq - self.fs / 2)) / (self.fs / self.fft_size))
                if 0 <= freq_idx < self.fft_size:
                    half_w = 15
                    lo, hi = max(0, freq_idx - half_w), min(self.fft_size, freq_idx + half_w)
                    psd[lo:hi] = self.noise_floor + np.random.uniform(0, 2, hi - lo)
        elif action == "DECEPTIVE_JAM":
            for _ in range(random.randint(2, 5)):
                fake_idx = random.randint(50, self.fft_size - 50)
                half_w   = random.randint(5, 20)
                x        = np.arange(self.fft_size)
                fake_amp = random.uniform(15, 35)
                psd      = np.maximum(psd, self.noise_floor + fake_amp * np.exp(-((x - fake_idx) ** 2) / (2 * half_w ** 2)))
        return psd

    def _spawn_random_signal(self):
        mod_types = ["BPSK", "QPSK", "AM", "FM", "LoRa", "Radar"]
        weights   = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        freq_offset = (np.random.rand() - 0.5) * (self.fs * 0.8)
        sig_type    = random.choices(mod_types, weights=weights, k=1)[0]
        amplitude   = np.random.uniform(35, 65) if sig_type == "Radar" else np.random.uniform(20, 55)
        bw          = np.random.uniform(5e3, 30e3) if sig_type == "Radar" else np.random.uniform(10e3, 100e3)
        self.active_signals.append({
            "freq":           self.center_freq + freq_offset,
            "bw":             bw,
            "amplitude":      amplitude,
            "type":           sig_type,
            "duration":       np.random.uniform(1.5, 9),
            "hopping":        np.random.rand() > 0.7,
            "phase_offset":   np.random.uniform(0, 2 * np.pi),
            "phase_noise":    np.random.uniform(0.01, 0.2),
            "carrier_offset": np.random.uniform(-500, 500),
        })


if __name__ == "__main__":
    env   = RFEnvironment()
    frame = env.generate_spectrum_frame()
    print(f"Frame size: {len(frame)}, active signals: {len(env.active_signals)}")
