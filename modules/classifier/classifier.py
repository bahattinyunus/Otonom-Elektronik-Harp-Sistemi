import numpy as np
from core.config import THREAT_MAP


class ModulationClassifier:
    """Classifies RF signal modulation type using advanced spectral features."""

    def __init__(self):
        self.classes = ["BPSK", "QPSK", "16QAM", "AM", "FM", "LoRa", "Radar", "Noise"]

    def _calculate_spectral_moments(self, psd_slice):
        """Calculates 1st-4th order spectral moments and flatness."""
        if psd_slice is None:
            return 0.0, 3.0, 0.5, 0.0
        
        arr = np.array(psd_slice, dtype=float)
        if len(arr) < 5:
            return 0.0, 3.0, 0.5, 0.0
            
        # Normalize PSD to linear scale for moment calculation
        lin_psd = 10**(arr / 10.0)
        norm_psd = lin_psd / (np.sum(lin_psd) + 1e-12)
        
        bins = np.arange(len(norm_psd))
        mean = np.sum(bins * norm_psd)
        std  = np.sqrt(np.sum(((bins - mean)**2) * norm_psd) + 1e-12)
        
        # Skewness (3rd moment) & Kurtosis (4th moment)
        skewness = np.sum(((bins - mean)**3) * norm_psd) / (std**3 + 1e-12)
        kurtosis = np.sum(((bins - mean)**4) * norm_psd) / (std**4 + 1e-12)
        
        # Spectral Flatness (Wiener entropy)
        geometric_mean = np.exp(np.mean(np.log(lin_psd + 1e-12)))
        arithmetic_mean = np.mean(lin_psd)
        flatness = geometric_mean / (arithmetic_mean + 1e-12)
        
        return round(float(skewness), 3), round(float(kurtosis), 3), round(float(flatness), 4), round(float(std), 2)

    def classify(self, signal_data, psd_slice=None):
        bw  = float(signal_data.get('bandwidth_idx', 0))
        snr = float(signal_data.get('snr', 0))

        if snr < 6:
            return "Noise", 0.98, "LOW"

        # Extract real spectral features
        skew, kurt, flat, std = self._calculate_spectral_moments(psd_slice)
        
        # Decision Engine (Spectral Heuristics as an Expert System)
        if kurt > 4.5 and snr > 35:
            mod_type = "Radar"
            conf = 0.94
        elif (bw > 25 if flat > 0.5 else bw > 40): # Wide signals (LoRa or Wideband)
            mod_type = "LoRa" if flat > 0.5 else "QPSK"
            conf = 0.88
        elif 2.0 < kurt < 3.8 and bw > 10:
            mod_type = "QPSK" if bw > 15 else "BPSK"
            conf = 0.85
        elif bw < 12:
            mod_type = "FM" if std > 2.5 else "AM"
            conf = 0.82
        else:
            mod_type = "16QAM"
            conf = 0.70

        threat_level = THREAT_MAP.get(mod_type, "MEDIUM")
        
        # Attach moments for RFI fingerprinting
        signal_data['kurtosis'] = kurt
        signal_data['skewness'] = skew
        
        return mod_type, conf, threat_level

    def extract_rfi_signature(self, signal_data):
        """Generates a stable RFI fingerprint based on spectral moments."""
        kurt = signal_data.get('kurtosis', 3.0)
        skew = signal_data.get('skewness', 0.0)
        snr  = signal_data.get('snr', 10.0)
        
        # Combine moments with SNR for a unique, emitter-specific fingerprint
        val = abs(kurt * 1337) + abs(skew * 777) + (snr * 6.6)
        return f"0x{(int(val * 42) % 0xFFFFF):05X}"
