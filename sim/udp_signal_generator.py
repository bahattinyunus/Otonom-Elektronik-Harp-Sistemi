import numpy as np
import time
import socket
import pickle
import sys

# Simulation configuration
SAMPLING_RATE = 2.0e6
CENTER_FREQ = 433.0e6
FFT_SIZE = 1024
NOISE_FLOOR = -100

class UdpSignalGenerator:
    def __init__(self, host='127.0.0.1', port=5005):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.center_freq = CENTER_FREQ
        self.fs = SAMPLING_RATE
        self.fft_size = FFT_SIZE
        self.noise_floor = NOISE_FLOOR
        self.active_signals = []
        
    def generate_and_send(self):
        # Base noise
        noise = np.random.normal(0, 1, self.fft_size) + 1j * np.random.normal(0, 1, self.fft_size)
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(noise, n=self.fft_size)))**2 + 1e-12)
        psd += self.noise_floor
        
        # Add random signals for simulation
        if np.random.rand() > 0.95:  # 5% chance to spawn a new signal
            self._spawn_random_signal()
            
        # Apply active signals to PSD
        for sig in self.active_signals[:]:
            try:
                if sig.get('hopping', False) and np.random.rand() > 0.8:
                    hop_offset = (np.random.rand() - 0.5) * (self.fs * 0.8)
                    sig['freq'] = self.center_freq + hop_offset

                fading_factor = 1.0 + 0.2 * np.sin(time.time() * 10.0 + sig.get('phase_offset', 0))
                current_amp = sig['amplitude'] * fading_factor

                freq_idx = int((sig['freq'] - (self.center_freq - self.fs/2)) / (self.fs / self.fft_size))
                if 0 <= freq_idx < self.fft_size:
                    width = sig['bw'] / (self.fs / self.fft_size)
                    x = np.arange(self.fft_size)
                    peak = current_amp * np.exp(-((x - freq_idx)**2) / (2 * (width/2)**2))
                    psd = np.maximum(psd, self.noise_floor + peak)
                    
                sig['duration'] -= 0.1
                if sig['duration'] <= 0:
                    self.active_signals.remove(sig)
            except Exception:
                pass

        # Send via UDP
        data = {
            "psd": psd.tolist(),
            "active_signals": self.active_signals
        }
        
        try:
            payload = pickle.dumps(data)
            self.sock.sendto(payload, (self.host, self.port))
            print(f"[X] Sent {len(payload)} bytes to {self.host}:{self.port} | Signals: {len(self.active_signals)}", end='\r')
        except Exception as e:
            print(f"Error sending payload: {e}")

    def _spawn_random_signal(self):
        mod_types = ["BPSK", "QPSK", "AM", "FM", "LoRa"]
        freq_offset = (np.random.rand() - 0.5) * (self.fs * 0.8)
        self.active_signals.append({
            "freq": self.center_freq + freq_offset,
            "bw": np.random.uniform(10e3, 100e3),
            "amplitude": np.random.uniform(20, 60),
            "type": np.random.choice(mod_types),
            "duration": np.random.uniform(2, 8),
            "hopping": np.random.rand() > 0.7,
            "phase_offset": np.random.uniform(0, 2 * np.pi),
            "phase_noise": np.random.uniform(0.01, 0.2), 
            "carrier_offset": np.random.uniform(-500, 500) 
        })

if __name__ == "__main__":
    generator = UdpSignalGenerator()
    print("--------------------------------------------------")
    print(" EXTERNAL UDP SIGNAL GENERATOR (SIMULATION NODE)  ")
    print("--------------------------------------------------")
    print("Streaming UDP packets to 127.0.0.1:5005...")
    try:
        while True:
            generator.generate_and_send()
            time.sleep(0.1)  # Match exactly to UPDATE_INTERVAL_MS = 100
    except KeyboardInterrupt:
        print("\nStopping simulation.")
        sys.exit(0)
