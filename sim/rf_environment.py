import numpy as np
import random
import socket
import pickle
import threading
import time
from core.config import SAMPLING_RATE, CENTER_FREQ, FFT_SIZE, NOISE_FLOOR

UDP_HOST = '127.0.0.1'
UDP_PORT = 5005
UDP_TIMEOUT = 2.0


class RFEnvironment:
    """RF environment: receives spectrum via UDP when available, falls back to
    built-in simulation. Jamming effects are applied to whichever source is active."""

    def __init__(self, udp_host=UDP_HOST, udp_port=UDP_PORT):
        self.center_freq    = CENTER_FREQ
        self.fs             = SAMPLING_RATE
        self.fft_size       = FFT_SIZE
        self.noise_floor    = NOISE_FLOOR
        self.active_signals = []
        self.jamming_action = "STANDBY"

        self._udp_psd         = None
        self._udp_last_rx     = 0.0
        self._udp_lock        = threading.Lock()

        self._start_udp_listener(udp_host, udp_port)

    def set_jamming(self, action):
        self.jamming_action = action

    def _start_udp_listener(self, host, port):
        def _listen():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((host, port))
                sock.settimeout(1.0)
            except OSError:
                return
            while True:
                try:
                    data, _ = sock.recvfrom(65535)
                    payload = pickle.loads(data)
                    with self._udp_lock:
                        if "psd" in payload:
                            self._udp_psd = payload["psd"]
                        if "active_signals" in payload:
                            self.active_signals = payload["active_signals"]
                        self._udp_last_rx = time.time()
                except socket.timeout:
                    continue
                except Exception:
                    time.sleep(0.1)

        t = threading.Thread(target=_listen, daemon=True)
        t.start()

    def _udp_active(self):
        with self._udp_lock:
            return (self._udp_psd is not None and
                    (time.time() - self._udp_last_rx) < UDP_TIMEOUT)

    def generate_spectrum_frame(self):
        if self._udp_active():
            with self._udp_lock:
                psd = np.array(self._udp_psd, dtype=float)
        else:
            psd = self._local_simulate()

        psd = self._apply_jamming(psd)
        return psd.tolist()

    def _local_simulate(self):
        # 1. Base thermal noise floor
        noise = (np.random.normal(0, 1, self.fft_size) +
                 1j * np.random.normal(0, 1, self.fft_size))
        psd = 10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(noise, n=self.fft_size))) ** 2 + 1e-12)
        psd += self.noise_floor

        if np.random.rand() > 0.93:
            self._spawn_random_signal()

        now = time.time()
        for sig in self.active_signals[:]:
            # 2. Sequential behavior logic
            if sig.get('hopping', False) and np.random.rand() > 0.8:
                sig['freq'] = self.center_freq + (np.random.rand() - 0.5) * self.fs * 0.8
            
            # 3. FMCW / Chirp logic: frequency sweeps over time
            current_freq = sig['freq']
            if sig.get('type') == 'Radar' and sig.get('fmcw', False):
                # Linear sweep: start_freq + (k * t mod sweep_duration)
                sweep_range = sig.get('sweep_hz', 500e3)
                period = sig.get('sweep_period', 2.0)
                offset = (now % period) / period
                current_freq += (offset - 0.5) * sweep_range

            # 4. Multipath Fading: simulate time-variant signal fluctuation
            # simple model: I + Q where Q is a delayed/phase-shifted reflection
            distort_phase = (now * 5.0) + sig.get('phase_offset', 0)
            fading = 1.0 + 0.3 * np.sin(distort_phase) # Reflection interference simulation
            
            current_amp = sig['amplitude'] * fading
            freq_idx    = int((current_freq - (self.center_freq - self.fs / 2)) / (self.fs / self.fft_size))
            
            if 0 <= freq_idx < self.fft_size:
                width = sig['bw'] / (self.fs / self.fft_size)
                x     = np.arange(self.fft_size)
                # Gaussian pulse representation
                peak  = current_amp * np.exp(-((x - freq_idx) ** 2) / (2 * (width / 2) ** 2))
                psd   = np.maximum(psd, self.noise_floor + peak)

            sig['duration'] -= 0.1
            if sig['duration'] <= 0:
                self.active_signals.remove(sig)

        return psd

    def _apply_jamming(self, psd):
        action = self.jamming_action
        if action == "JAM_BARRAGE":
            psd = psd + np.random.uniform(12, 22, self.fft_size)
        elif action == "JAM_SPOT":
            for sig in self.active_signals:
                freq_idx = int((sig['freq'] - (self.center_freq - self.fs / 2)) / (self.fs / self.fft_size))
                if 0 <= freq_idx < self.fft_size:
                    lo, hi = max(0, freq_idx - 15), min(self.fft_size, freq_idx + 15)
                    psd[lo:hi] = self.noise_floor + np.random.uniform(0, 2, hi - lo)
        elif action == "DECEPTIVE_JAM":
            for _ in range(random.randint(2, 5)):
                fake_idx = random.randint(50, self.fft_size - 50)
                half_w   = random.randint(5, 20)
                x        = np.arange(self.fft_size)
                fake_amp = random.uniform(15, 35)
                psd      = np.maximum(psd, self.noise_floor +
                                      fake_amp * np.exp(-((x - fake_idx) ** 2) / (2 * half_w ** 2)))
        elif action == "DRFM_GHOSTS":
            # Simulate DRFM by creating frequency-offset copies of active signals
            for sig in self.active_signals:
                if sig.get('amplitude', 0) > 30:
                    for offset in [-60, 60]: # +/- bin offsets
                        freq_idx = int((sig['freq'] - (self.center_freq - self.fs / 2)) / (self.fs / self.fft_size))
                        ghost_idx = freq_idx + offset
                        if 0 <= ghost_idx < self.fft_size:
                            width = sig['bw'] / (self.fs / self.fft_size)
                            x     = np.arange(self.fft_size)
                            ghost_peak = (sig['amplitude'] * 0.7) * np.exp(-((x - ghost_idx) ** 2) / (2 * (width / 2) ** 2))
                            psd = np.maximum(psd, self.noise_floor + ghost_peak)
        return psd

    def _spawn_random_signal(self):
        mod_types = ["BPSK", "QPSK", "AM", "FM", "LoRa", "Radar"]
        weights   = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        sig_type  = random.choices(mod_types, weights=weights, k=1)[0]
        
        amplitude = np.random.uniform(35, 65) if sig_type == "Radar" else np.random.uniform(20, 55)
        bw        = np.random.uniform(5e3, 30e3) if sig_type == "Radar" else np.random.uniform(10e3, 100e3)
        
        is_fmcw = (sig_type == "Radar") and (random.random() > 0.4)
        
        self.active_signals.append({
            "freq":           self.center_freq + (np.random.rand() - 0.5) * self.fs * 0.8,
            "bw":             bw,
            "amplitude":      amplitude,
            "type":           sig_type,
            "duration":       np.random.uniform(1.5, 9),
            "hopping":        np.random.rand() > 0.7 if not is_fmcw else False,
            "fmcw":           is_fmcw,
            "sweep_hz":       np.random.uniform(200e3, 800e3),
            "sweep_period":   np.random.uniform(1.0, 4.0),
            "phase_offset":   np.random.uniform(0, 2 * np.pi),
            "phase_noise":    np.random.uniform(0.01, 0.2),
            "carrier_offset": np.random.uniform(-500, 500),
        })


if __name__ == "__main__":
    env   = RFEnvironment()
    time.sleep(0.5)
    frame = env.generate_spectrum_frame()
    mode  = "UDP" if env._udp_active() else "LOCAL"
    print(f"[{mode}] Frame size: {len(frame)}, active signals: {len(env.active_signals)}")
