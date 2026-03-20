import torch
import torch.nn as nn
import numpy as np
from collections import deque

class HopLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=32, num_layers=1):
        super(HopLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc   = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class FrequencyHopPredictor:
    """
    Predicts the next frequency hop using a sequence-to-one LSTM model.
    Learns patterns in frequency-hopping signals in real-time.
    """
    def __init__(self, history_len=10):
        self.history_len = history_len
        self.histories  = {} # track_id -> deque
        
        self.model = HopLSTM()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.MSELoss()
        
    def update_and_predict(self, track_id, current_freq_mhz):
        if track_id not in self.histories:
            self.histories[track_id] = deque(maxlen=self.history_len)
        
        history = self.histories[track_id]
        
        # Training step if we have enough history
        prediction = None
        if len(history) == self.history_len:
            # Simple online learning (stochastic gradient descent on current sequence)
            seq = np.array(list(history), dtype=np.float32).reshape(1, self.history_len, 1)
            target = np.array([[current_freq_mhz]], dtype=np.float32)
            
            self.model.train()
            input_tensor = torch.from_numpy(seq)
            target_tensor = torch.from_numpy(target)
            
            output = self.model(input_tensor)
            loss   = self.criterion(output, target_tensor)
            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # Predict next
            self.model.eval()
            with torch.no_grad():
                # Add current to sequence for next prediction
                next_seq = np.append(seq[0, 1:, :], target.reshape(1,1), axis=0).reshape(1, self.history_len, 1)
                prediction = self.model(torch.from_numpy(next_seq)).item()
        
        history.append(current_freq_mhz)
        return prediction

    def get_all_predictions(self):
        # Useful for UI visualization
        preds = {}
        for tid, hist in self.histories.items():
            if len(hist) == self.history_len:
                seq = np.array(list(hist), dtype=np.float32).reshape(1, self.history_len, 1)
                self.model.eval()
                with torch.no_grad():
                    preds[tid] = self.model(torch.from_numpy(seq)).item()
        return preds
