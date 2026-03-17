import random

class ModulationClassifier:
    """Classifies the modulation type of a detected signal."""
    def __init__(self):
        self.classes = ["BPSK", "QPSK", "16QAM", "AM", "FM", "LoRa", "Noise"]

    def classify(self, signal_data):
        # In production, this would be a CNN/LSTM inference
        # For simulation, we return a mock classification based on signal strength
        return random.choice(self.classes[:-1]) if signal_data['snr'] > 10 else "Noise"
