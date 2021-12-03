import warnings
import torch
import torch.nn.functional as func
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence
warnings.filterwarnings("ignore")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class bLSTM(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, linear_dim, output_dim):
        super(bLSTM, self).__init__()
        self.blstm = torch.nn.LSTM(input_size = input_dim, hidden_size = hidden_dim, num_layers = 1, bidirectional = True, batch_first = True, dropout = 0.33)
        self.linear = torch.nn.Linear(hidden_dim*2, linear_dim)
        self.dropout = torch.nn.Dropout(p = 0.33)
        self.classifier = torch.nn.Linear(linear_dim, output_dim)
    
    def forward(self, x, lens):
        packed = pack_padded_sequence(x, lens, batch_first = True, enforce_sorted = False)
        blstm_out, _ = self.blstm(packed)
        blstm_out, _ = pad_packed_sequence(blstm_out, batch_first = True, padding_value = 0, total_length = 251)
        lin_out = func.relu(self.linear(blstm_out))
        lin_out = self.dropout(lin_out)
        class_out = self.classifier(lin_out)
        return class_out
    
    def init_weights(self):
        for name, param in self.named_parameters():
            torch.nn.init.normal_(param.data, mean=0, std=0.1)