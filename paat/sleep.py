"""
Sleep Module
------------

*paat.sleep* provides functions to detect periods of sleep in the raw
acceleration signals.

"""
import os

import pandas as pd
from torch import nn
import torch

from . import features


class _SleepModel(nn.Module):
    def __init__(self, input_dim, hid_dim, output_dim, n_layers, dropout, batch_first=False):
        super().__init__()

        self.output_dim = output_dim
        self.hid_dim = hid_dim
        self.n_layers = n_layers
        self.name = "LSTM"

        self.rnn = nn.LSTM(input_dim, hid_dim, n_layers, dropout=dropout, batch_first=batch_first)

        self.fc_out = nn.Linear(hid_dim, output_dim)

        self.sigmoid = nn.Sigmoid()

        self.dropout = nn.Dropout(dropout)

    def forward(self, X, lens):
        """
        Performs model's forward pass
        """

        packed_input = nn.utils.rnn.pack_padded_sequence(X, lens.to('cpu'), batch_first=True, enforce_sorted=False)
        packed_output, _ = self.rnn(packed_input)
        output, lens = nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)

        return self.sigmoid(self.fc_out(output))


def detect_sleep_weitz2022(time, acceleration, means=None, stds=None):
    """
    Infer time in bed from raw acceleration signal.

    Parameters
    ----------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    acceleration : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values in
        the default order of ActiGraph which is ['Y','X','Z'].
    means : array_like (optional)
        a numpy array with the channel means, will be calculated for the sample
        if not specified
    stds : array_like (optional)
        a numpy array with the channel stds, will be calculated for the sample
        if not specified

    Returns
    -------
    is_sleep : np.array (n_samples,)
        a numpy array indicating whether the values of the acceleration data is
        sleep on minute resolution

    """

    time, feature_vec = features.calculate_frequency_features(time, acceleration)

    X = torch.from_numpy(feature_vec).float()

    # If no means and stds are given, calculate it
    if not means or not stds:
        means, stds = X.mean(axis=0), X.std(axis=0)

    # Normalize input
    X = (X - means) / stds

    X = X.unsqueeze(0)
    lengths = torch.Tensor([X.shape[1]])

    # Load model hard coded. Should later be changed to ONNX or similar
    model = _SleepModel(160, 4, 1, 1, dropout=0, batch_first=True)
    model_path = os.path.join(os.path.pardir, os.path.dirname(__file__), 'models', 'SleepModel.pt')
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # Predict sleep periods
    is_sleep = (model(X, lengths) >= .5).squeeze().numpy()

    return is_sleep


def detect_time_in_bed_weitz2022(time, acceleration, resampled_frequency="1min", means=None, stds=None, model_path=None):
    """
    Infer time in bed from raw acceleration signal.

    Parameters
    ----------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    acceleration : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values in
        the default order of ActiGraph which is ['Y','X','Z'].
    resampled_frequency : str (optional)
        a str indicating to what frequency the data should be resampled. This depends
        on the model used to predict, defaults to 1min.
    means : array_like (optional)
        a numpy array with the channel means, will be calculated for the sample
        if not specified
    stds : array_like (optional)
        a numpy array with the channel stds, will be calculated for the sample
        if not specified
    model_path : str (optional)
        an optional path to a custom model.

    Returns
    -------
    predicted_time_in_bed : np.array (n_samples,)
        a numpy array indicating whether the values of the acceleration data were spent in bed

    """
    if resampled_frequency:
        data = pd.DataFrame(acceleration, columns=['Y', 'X', 'Z'])
        data = data.set_index(time)
        data = data.resample(resampled_frequency).mean()
        X = torch.from_numpy(data[['Y', 'X', 'Z']].values)
    else:
        X = torch.from_numpy(acceleration)

    # The models were trained with XYZ axis ordering while the standard ordering is YXZ
    # Therefore, we have to switch X and Y axis
    X = X[:, [1, 0, 2]]
    X = X.float()

    # If no means and stds are given, calculate subject's mean and std
    # to normalize by this
    if not means or not stds:
        means, stds = X.mean(axis=0), X.std(axis=0)

    # Normalize input
    X = (X - means) / stds
    lengths = torch.Tensor(X.shape[0]).float().unsqueeze(0)

    X = X.unsqueeze(0)
    lengths = torch.Tensor([X.shape[1]])

    # Load model if not specified
    if not model_path:
        model = _SleepModel(3, 2, 1, 1, dropout=0, batch_first=True)
        model_path = '/home/msw/Documents/PhD/Discrimination of sleep and wake periods/source/experiments/exp02_models/06_best_1l_LSTM2_model_fold_6.pt'
        model.load_state_dict(torch.load(model_path))
        model.eval()

    data.loc[:, 'Time in Bed'] = (model(X, lengths) >= .5).squeeze().numpy()
    data.loc[:, 'Time'] = data.index
    data = data[['Time', 'Time in Bed']]

    data = pd.merge_asof(pd.DataFrame({'Time': time}), data, on="Time")
    predicted_time_in_bed = data['Time in Bed'].values

    return predicted_time_in_bed
