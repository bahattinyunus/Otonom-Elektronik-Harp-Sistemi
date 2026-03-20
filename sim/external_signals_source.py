import numpy as np
import socket
import pickle
import time
import random
from core.config import SAMPLING_RATE, CENTER_FREQ, FFT_SIZE, NOISE_FLOOR

# Configuration for the external simulator
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 5005
UPDATE_RATE_HZ = 10

class ExternalSignalSource:
    """
    Advanced External RF Simulator.
    Generates high-fidelity spectrum data and streams it via UDP.
    """
    def __init__(self):
        self.fs = SAMPLING_RATE
        self.center_freq = CENTER_FREQ
        self.fft_size = FFT_SIZE
        self.noise_floor = NOISE_FLOOR
        self.active_signals = []
        self.start_time = time.time()
        
    def generate_frame(self):
        t = time.time() - self.start_time
        
        # Base noise
        noise = (np.random.normal(0, 1, self.fft_size) + 
                 1j * np.random.normal(0, 1, self.fft_size))
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(noise, n=self.fft_size)))**2 + 1e-12)
        psd += self.noise_floor

        # --- DYNAMIC SCENARIO LOGIC ---
        self.active_signals = []

        # 1. Moving Radar (Low freq to High freq over 30s)
        radar_freq = self.center_freq - 0.7e6 + (t % 30) * 0.05e6
        self.active_signals.append({
            "freq": radar_freq, "bw": 30e3, "amplitude": 55, "type": "Radar",
            "duration": 5, "hopping": False, "phase_noise": 0.02, "carrier_offset": 50
        })

        # 2. Frequency Hopper (Jumps every 2 seconds)
        hop_idx = int(t / 2) % 5
        hop_freqs = [0.2e6, -0.3e6, 0.5e6, -0.1e6, 0.8e6]
        self.active_signals.append({
            "freq": self.center_freq + hop_freqs[hop_idx], "bw": 50e3, "amplitude": 40, "type": "QPSK",
            "duration": 2, "hopping": True, "phase_noise": 0.1, "carrier_offset": -120
        })

        # 3. Constant Communications Node
        self.active_signals.append({
            "freq": self.center_freq - 0.45e6, "bw": 120e3, "amplitude": 35, "type": "FM",
            "duration": 99, "hopping": False, "phase_noise": 0.05, "carrier_offset": 0
        })

        # 4. Periodic "Pop-up" Burst (Every 8 seconds)
        if (t % 8) < 1.5:
            self.active_signals.append({
                "freq": self.center_freq + 0.35e6, "bw": 15e3, "amplitude": 65, "type": "LoRa",
                "duration": 1.5, "hopping": False, "phase_noise": 0.2, "carrier_offset": 200
            })

        # Render signals to PSD
        for sig in self.active_signals:
            freq_idx = int((sig['freq'] - (self.center_freq - self.fs/2)) / (self.fs / self.fft_size))
            if 0 <= freq_idx < self.fft_size:
                width = sig['bw'] / (self.fs / self.fft_size)
                x = np.arange(self.fft_size)
                # Gaussian peak
                peak = sig['amplitude'] * np.exp(-((x - freq_idx)**2) / (2 * (width/2)**2))
                psd = np.maximum(psd, self.noise_floor + peak)

        return psd.tolist(), self.active_signals

    def _spawn_popup(self):
        self.active_signals.append({
            "freq": self.center_freq + (random.random() - 0.5) * self.fs * 0.6,
            "bw": random.uniform(20e3, 50e3),
            "amplitude": random.uniform(30, 50),
            "type": random.choice(["BPSK", "FM", "LoRa"]),
            "duration": random.uniform(2, 5),
            "hopping": random.random() > 0.5,
            "phase_offset": random.uniform(0, 6),
            "phase_noise": 0.15,
            "carrier_offset": random.uniform(-400, 400)
        })

def run_simulator():
    sim = ExternalSignalSource()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[*] External RF Simulator started. Streaming to {TARGET_HOST}:{TARGET_PORT}")
    
    try:
        while True:
            psd, sigs = sim.generate_frame()
            payload = {
                "psd": psd,
                "active_signals": sigs
            }
            data = pickle.dumps(payload)
            sock.sendto(data, (TARGET_HOST, TARGET_PORT))
            time.sleep(1.0 / UPDATE_RATE_HZ)
    except KeyboardInterrupt:
        print("\n[*] Simulator stopped.")

if __name__ == "__main__":
    run_simulator()
