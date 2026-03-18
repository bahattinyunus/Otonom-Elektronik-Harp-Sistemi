class ModulationClassifier:
    """Classifies the modulation type of a detected signal using heuristics."""
    def __init__(self):
        self.classes = ["BPSK", "QPSK", "16QAM", "AM", "FM", "LoRa", "Noise"]

    def classify(self, signal_data):
        # Heuristic / Fake Decision Tree based on BW and SNR
        bw = signal_data.get('bandwidth_idx', 0)
        snr = signal_data.get('snr', 0)
        
        if snr < 5:
            return "Noise"
            
        if bw > 25:
            # Wideband
            if snr > 25:
                return "16QAM"
            else:
                return "LoRa"
        elif bw > 12:
            # Mediumband
            if snr > 20:
                return "QPSK"
            else:
                return "FM"
        else:
            # Narrowband
            if snr > 15:
                return "BPSK"
            else:
                return "AM"
