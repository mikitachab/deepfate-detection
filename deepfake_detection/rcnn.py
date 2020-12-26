import torch
from torch import nn
import torch.nn.functional as F
import torchvision


class RCNN(nn.Module):
    """
    stacks rnn on top of cnn
    """

    def __init__(self, num_classes=2, rnn_hidden_size=128, rnn_num_layers=2, cnn=None):
        super(RCNN, self).__init__()
        if cnn is None:
            cnn = torchvision.models.resnet18(pretrained=True)
        self.cnn = cnn
        n_features = self.cnn.fc.in_features
        self.cnn.fc = nn.Identity()
        self.lstm = nn.LSTM(
            n_features, rnn_hidden_size, rnn_num_layers, batch_first=True
        )
        self.fc = nn.Linear(rnn_hidden_size, num_classes)

    def forward(self, x):
        """
        Note: this works only for input with batch_size=1.
        One sample is sequense of frames.
        """
        c_out = self.cnn(x)
        r_out, (h_n, h_c) = self.lstm(torch.unsqueeze(c_out, 0))
        fc_in = torch.unsqueeze(r_out[0][-1], 0)  # last hidden vector from rnn
        fc_out = self.fc(fc_in)
        out = F.softmax(fc_out, dim=1)
        return out
