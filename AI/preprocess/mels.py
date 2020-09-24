import os
import gc

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tqdm.notebook import tqdm

def wav_to_mels(data, hparams):
    return librosa.feature.melspectrogram(data[:-1],
                                          sr=hparams.sample_rate,
                                          n_fft=hparams.n_fft,
                                          hop_length=hparams.hop_length,
                                          win_length=hparams.win_length,
                                          window=hparams.window,
                                          n_mels=hparams.n_mels).astype(np.float32)


def save_mels(file_name, mels):
    np.save(file_name, mels.T)

#for gpu process
class LogMelSpectrogram(tf.keras.layers.Layer):

    def __init__(self, sample_rate, fft_size, hop_size, n_mels,
                 f_min=0.0, f_max=None, **kwargs):
        super(LogMelSpectrogram, self).__init__(**kwargs)
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_size = hop_size
        self.n_mels = n_mels
        self.f_min = f_min
        self.f_max = f_max if f_max else sample_rate / 2
        self.mel_filterbank = tf.signal.linear_to_mel_weight_matrix(
            num_mel_bins=self.n_mels,
            num_spectrogram_bins=fft_size // 2 + 1,
            sample_rate=self.sample_rate,
            lower_edge_hertz=self.f_min,
            upper_edge_hertz=self.f_max)

    def build(self, input_shape):
        self.non_trainable_weights.append(self.mel_filterbank)
        super(LogMelSpectrogram, self).build(input_shape)

    def call(self, waveforms):
        
        def _tf_log10(x):
            numerator = tf.math.log(x)
            denominator = tf.math.log(tf.constant(10, dtype=numerator.dtype))
            return numerator / denominator

        def power_to_db(magnitude, amin=1e-16, top_db=80.0):
            ref_value = tf.reduce_max(magnitude)
            log_spec = 10.0 * _tf_log10(tf.maximum(amin, magnitude))
            log_spec -= 10.0 * _tf_log10(tf.maximum(amin, ref_value))
            log_spec = tf.maximum(log_spec, tf.reduce_max(log_spec) - top_db)

            return log_spec

        spectrograms = tf.signal.stft(waveforms,
                                      frame_length=self.fft_size,
                                      frame_step=self.hop_size,
                                      pad_end=False)

        magnitude_spectrograms = tf.abs(spectrograms)

        mel_spectrograms = tf.matmul(tf.square(magnitude_spectrograms),
                                     self.mel_filterbank)

        log_mel_spectrograms = power_to_db(mel_spectrograms)

        # add channel dimension
        log_mel_spectrograms = tf.expand_dims(log_mel_spectrograms, 3)
        
        return log_mel_spectrograms

    def get_config(self):
        config = {
            'fft_size': self.fft_size,
            'hop_size': self.hop_size,
            'n_mels': self.n_mels,
            'sample_rate': self.sample_rate,
            'f_min': self.f_min,
            'f_max': self.f_max,
        }
        config.update(super(LogMelSpectrogram, self).get_config())

        return config

def GPU_Mel_process(data_path, mel_save, sound_save, SAMPLE_RATE, FFT_SIZE, HOP_SIZE, N_MEL_BINS, F_MIN, F_MAX):
   process_layer = LogMelSpectrogram(SAMPLE_RATE, FFT_SIZE, HOP_SIZE, N_MEL_BINS, F_MIN, F_MAX)

   for genre in tqdm(os.listdir(data_path)):
      genre_path = os.path.join(data_path, genre)

      mel_path = os.path.join(mel_save, genre)
      sound_path = os.path.join(sound_save, genre)

      os.makedirs(mel_path, exist_ok=True)
      os.makedirs(sound_path, exist_ok=True)

      for i, file_name in tqdm(enumerate(os.listdir(genre_path)), total=len(os.listdir(genre_path))):

        file_path = os.path.join(genre_path, file_name)

        mel_save_dir = os.path.join(mel_path, f'{i}.npy')
        sound_save_dir = os.path.join(sound_path, f'{i}.npy')

        if os.path.isfile(mel_save_dir):
          continue

        data, _ = librosa.load(file_path, SAMPLE_RATE, duration=DURATION)

        data = pad_sequences(np.array([data]), HOP_SIZE*(MEL_WIDTH+1), 'float32', padding='post', truncating='post')

        mel = process_layer(data)

        mel = tf.squeeze(mel, 0).numpy()

        np.save(mel_save_dir, mel)
        np.save(sound_save_dir, data[0])

        gc.collect()
