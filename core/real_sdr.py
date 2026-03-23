import numpy as np
from core.sdr_interface import SDRInterface
from core.config import SAMPLING_RATE, CENTER_FREQ, FFT_SIZE

try:
    from rtlsdr import RtlSdr
except ImportError:
    RtlSdr = None

class RealSDR(SDRInterface):
    """Actual SDR hardware integration for RTL-SDR devices."""

    def __init__(self):
        self._fs = SAMPLING_RATE
        self._center_freq = CENTER_FREQ
        self._fft_size = FFT_SIZE
        self.sdr = None
        self.active = False
        
        self._initialize_hardware()

    def _initialize_hardware(self):
        if RtlSdr is None:
            print("[RealSDR] Error: pyrtlsdr not installed. Use 'pip install pyrtlsdr'.")
            return

        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self._fs
            self.sdr.center_freq = self._center_freq
            self.sdr.gain = 'auto'
            self.active = True
            print(f"[RealSDR] Hardware connected: {self._center_freq/1e6:.2f} MHz @ {self._fs/1e6:.2f} Msps")
        except Exception as e:
            print(f"[RealSDR] Hardware connection failed: {e}")
            self.active = False

    @property
    def fs(self) -> float:
        return self._fs

    @property
    def center_freq(self) -> float:
        return self._center_freq

    @property
    def fft_size(self) -> int:
        return self._fft_size

    def generate_spectrum_frame(self) -> list:
        if not self.active or self.sdr is None:
            # Fallback to noise floor if hardware is missing
            return [-100.0] * self.fft_size

        try:
            # Read complex samples from hardware
            samples = self.sdr.read_samples(self.fft_size * 2)
            # Compute FFT
            window = np.blackman(len(samples))
            fft_res = np.fft.fftshift(np.fft.fft(samples * window))
            psd = 10 * np.log10(np.abs(fft_res)**2 + 1e-12)
            
            # Map PSD to exactly fft_size bins
            return psd[:self.fft_size].tolist()
        except Exception as e:
            print(f"[RealSDR] Frame capture error: {e}")
            return [-100.0] * self.fft_size

    def set_jamming(self, action: str):
        # Hardware specific GPIO/TX commands for Emitter.
        print(f"[RealSDR] Hardware TX (Action: {action}) - Requires daughterboard or distinct TX hardware.")

    def set_center_freq(self, freq_hz: float):
        self._center_freq = freq_hz
        if self.active and self.sdr:
            try:
                self.sdr.center_freq = freq_hz
                print(f"[RealSDR] Hardware retuned to: {freq_hz / 1e6:.2f} MHz")
            except Exception as e:
                print(f"[RealSDR] Retune failed: {e}")

    def is_active(self) -> bool:
        return self.active

    def close(self):
        if self.sdr:
            self.sdr.close()
            self.active = False
