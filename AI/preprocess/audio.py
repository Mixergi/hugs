import librosa
import numpy as np


def preprocess_wav(data, hparams):
    cut_off_index = -(len(data) % hparams.hop_length)
    if cut_off_index != 0:
        return data[:-(len(data) % hparams.hop_length)]
    else:
        return data


def split_data(data, hparams):
    splited_data = []

    data_size = hparams.hop_length * hparams.spec_length
    n_splits = len(data) // data_size
    for i in range(n_splits):
        splited_data.append(data[data_size * i:data_size * (i + 1)])

    return splited_data


def save_wav(file_name, data, hparams):
    librosa.output.write_wav(file_name, data, hparams.sample_rate)


def save_wav_to_npy(file_name, data):
    np.save(file_name, data)
