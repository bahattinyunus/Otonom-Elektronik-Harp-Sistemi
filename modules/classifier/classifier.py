import torch
import torch.nn as nn

class ModulationNet(nn.Module):
    """Simple Multi-Layer Perceptron (MLP) for classifying RF signals."""
    def __init__(self, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, num_classes)
        )
        
    def forward(self, x):
        return self.net(x)

class ModulationClassifier:
    """Classifies the modulation type of a detected signal using a PyTorch MLP."""
    def __init__(self):
        self.classes = ["BPSK", "QPSK", "16QAM", "AM", "FM", "LoRa", "Noise"]
        
        # Initialize an untrained PyTorch network.
        # Set manual_seed for deterministic pseudo-classification logic in simulation.
        torch.manual_seed(42)
        self.model = ModulationNet(len(self.classes))
        self.model.eval()

    def classify(self, signal_data):
        bw = float(signal_data.get('bandwidth_idx', 0))
        snr = float(signal_data.get('snr', 0))
        
        if snr < 5:
            return "Noise"
            
        # 1. Prepare tensor input (Normalized loosely to 0-1 range)
        x = torch.tensor([[snr / 50.0, bw / 50.0]], dtype=torch.float32)
        
        # 2. Forward pass through PyTorch Neutral Network
        with torch.no_grad():
            logits = self.model(x)
            
        # 3. Get predicted class
        pred_idx = torch.argmax(logits, dim=1).item()
        mod_type = self.classes[pred_idx]
        
        # Tactical override: Untrained network might predict AM for wideband, fix obvious physical impossibilities.
        if bw > 25 and mod_type in ["BPSK", "AM"]:
             mod_type = "LoRa"
        elif bw < 10 and mod_type in ["LoRa", "16QAM"]:
             mod_type = "AM"
             
        return mod_type
