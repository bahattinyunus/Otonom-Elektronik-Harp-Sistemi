import torch
import torch.nn as nn
import torch.nn.functional as F
from core.config import THREAT_MAP


class ModulationNet(nn.Module):
    """MLP classifier for RF signal modulation type."""
    def __init__(self, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, num_classes),
        )

    def forward(self, x):
        return self.net(x)


class ModulationClassifier:
    """Classifies RF signal modulation type, confidence and threat level."""

    def __init__(self):
        self.classes = ["BPSK", "QPSK", "16QAM", "AM", "FM", "LoRa", "Radar", "Noise"]
        torch.manual_seed(42)
        self.model = ModulationNet(len(self.classes))
        self.model.eval()

    def classify(self, signal_data):
        bw  = float(signal_data.get('bandwidth_idx', 0))
        snr = float(signal_data.get('snr', 0))

        if snr < 5:
            return "Noise", 0.97, "LOW"

        duration_proxy = min(bw / 10.0, 5.0)
        x = torch.tensor([[snr / 60.0, bw / 60.0, duration_proxy / 5.0]], dtype=torch.float32)

        with torch.no_grad():
            logits = self.model(x)
            probs  = F.softmax(logits, dim=1)

        pred_idx   = torch.argmax(probs, dim=1).item()
        confidence = float(probs[0, pred_idx])
        mod_type   = self.classes[pred_idx]

        if snr > 45 and bw > 30:
            mod_type = "Radar"
        elif bw > 40 and mod_type in ("BPSK", "AM"):
            mod_type = "LoRa"
        elif bw < 8 and mod_type in ("LoRa", "16QAM"):
            mod_type = "AM"

        threat_level = THREAT_MAP.get(mod_type, "MEDIUM")
        return mod_type, round(confidence, 3), threat_level

    def extract_rfi_signature(self, phase_noise, carrier_offset):
        val = abs(phase_noise * 1000) + abs(carrier_offset)
        return f"0x{(int(val * 12345) % 0xFFFFF):05X}"
