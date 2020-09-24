import math
import os
import time

import numpy as np
import librosa
import tensorflow as tf
import tqdm

from .MelGAN import Discriminator, Generator


class MelGANTrainer:
    def __init__(self, epochs, save_dir, log_dir):

        self.epochs = epochs

        self.save_dir = save_dir
        self.generator_dir = os.path.join(save_dir, 'generator')
        self.discriminator_dir = os.path.join(save_dir, 'discriminator')

        self.writer = tf.summary.create_file_writer(log_dir)

        self.mse = tf.keras.losses.MeanSquaredError()
        self.mae = tf.keras.losses.MeanAbsoluteError()

        self.metrics_name = [
            'adversarial_loss',
            'feature_matching_loss',
            'gen_loss',
            'real_loss',
            'fake_loss',
            'dis_loss'
        ]

        self.train_metrics = {}
        self.validation_metrics = {}

        self._init_metrics()

        self.steps = 0

    def _init_metrics(self):
        for name in self.metrics_name:
            self.train_metrics[name] = tf.keras.metrics.Mean()
            self.validation_metrics[name] = tf.keras.metrics.Mean()

    def _reset_metrics(self):
        for name in self.metrics_name:
            self.train_metrics[name].reset_states()
            self.validation_metrics[name].reset_states()

    def compile(self, d_opt, g_opt):
        self.discriminator = Discriminator()
        self.generator = Generator()

        self.d_opt = d_opt
        self.g_opt = g_opt

    def use_sample(self, sample_dir, sample_save_dir, sr):
        if sample_dir:
            self.sample_mels = np.array([np.load(sample_dir)])

        self.sample_save_dir = sample_save_dir
        self.sr = sr

    def write_sameple(self, file_name):
        data = self.predict(self.sample_mels)
        data = np.array(tf.squeeze(data))
        librosa.output.write_wav(os.path.join(self.sample_save_dir, file_name), data, sr=sr)

    def train(self, train_dataset, validation_dataset=None):

        for epoch in tqdm.tqdm(range(self.epochs)):
            self.steps = epoch + 1

            print('\ntraining steps')
            for batch in tqdm.tqdm(train_dataset.create(),
                                   total=math.ceil(train_dataset.get_length() / train_dataset.batch_size)):
                self._train_step(batch)

            self._write_on_tensorboard(self.train_metrics, stage='train')

            if validation_dataset:
                print('\nvalidation steps')
                for batch in tqdm.tqdm(validation_dataset.create(),
                                       total=math.ceil(validation_dataset.get_length() / validation_dataset.batch_size)):
                    self._validation_step(batch)
                    self._write_on_tensorboard(self.validation_metrics, stage='valid')

            self._reset_metrics()

            self.save_weight()

            if self.sample_mels:
                self.write_sameple(str(epoch) + '.wav')

        self.save_model()

    def _train_step(self, batch, training=True):
        y, mels = batch
        y_hat = self._generator_step(y, mels, training)
        self._discriminator_step(y, y_hat, training)

    @tf.function(experimental_relax_shapes=True)
    def _discriminator_step(self, y, y_hat, training=True):
        with tf.GradientTape() as d_tape:
            _y = tf.expand_dims(y, 2)
            p = self.discriminator(_y)

            p_hat = self.discriminator(y_hat)

            real_loss = 0
            fake_loss = 0

            for i in range(len(p)):
                real_loss += self.mse(p[i][-1], tf.ones_like(p[i][-1], tf.float32))
                fake_loss += self.mse(p_hat[i][-1], tf.ones_like(p_hat[i][-1], tf.float32))

            real_loss /= i + 1
            fake_loss /= i + 1

            dis_loss = real_loss + fake_loss

        if training:
            gradient = d_tape.gradient(dis_loss, self.discriminator.trainable_variables)
            self.d_opt.apply_gradients(zip(gradient, self.discriminator.trainable_variables))

            self.train_metrics['real_loss'].update_state(real_loss)
            self.train_metrics['fake_loss'].update_state(fake_loss)
            self.train_metrics['dis_loss'].update_state(dis_loss)

        else:
            self.validation_metrics['real_loss'].update_state(real_loss)
            self.validation_metrics['fake_loss'].update_state(fake_loss)
            self.validation_metrics['dis_loss'].update_state(dis_loss)

    @tf.function(experimental_relax_shapes=True)
    def _generator_step(self, y, mels, training=True):
        with tf.GradientTape() as g_tape:
            y_hat = self.generator(mels)
            p_hat = self.discriminator(y_hat)
            adversarial_loss = 0
            for i in range(len(p_hat)):
                adversarial_loss += self.mse(p_hat[i][-1], tf.ones_like(p_hat[i][-1], dtype=tf.float32))
            adversarial_loss /= i + 1

            _y = tf.expand_dims(y, 2)
            p = self.discriminator(_y)

            feature_matching_loss = 0
            for i in range(len(p_hat)):
                for j in range(len(p_hat[i]) - 1):
                    feature_matching_loss += self.mae(p_hat[i][j], p[i][j])

            # lambda = 10
            feature_matching_loss /= (i + 1) * (j + 1)
            gen_loss = adversarial_loss + feature_matching_loss * 10

        if training:
            gradient = g_tape.gradient(gen_loss, self.generator.trainable_variables)
            self.g_opt.apply_gradients(zip(gradient, self.generator.trainable_variables))

            self.train_metrics['adversarial_loss'].update_state(adversarial_loss)
            self.train_metrics['feature_matching_loss'].update_state(feature_matching_loss)
            self.train_metrics['gen_loss'].update_state(gen_loss)

        else:
            self.validation_metrics['adversarial_loss'].update_state(adversarial_loss)
            self.validation_metrics['feature_matching_loss'].update_state(feature_matching_loss)
            self.validation_metrics['gen_loss'].update_state(gen_loss)

        y_hat = self.generator(mels)

        return y_hat

    def predict(self, mels):
        return self.generator(mels)

    def load_model(self):
        self.discriminator = tf.keras.models.load_model(os.path.join(self.discriminator_dir, 'discriminator.h5'))
        self.generator = tf.keras.models.load_model(os.path.join(self.generator_dir, 'generator.h5'))

    def save_model(self):
        self.discriminator.save(os.path.join(self.discriminator_dir, 'discriminator.h5'))
        self.generator.save(os.path.join(self.generator_dir, 'generator.h5'))

    def load_weight(self):
        self.discriminator.load_weights(os.path.join(self.discriminator_dir, 'discriminator'))
        self.generator.load_weights(os.path.join(self.generator_dir, 'generator'))

    def save_weight(self):
        self.discriminator.save_weights(os.path.join(self.discriminator_dir, 'discriminator'))
        self.generator.save_weights(os.path.join(self.generator_dir, 'generator'))

    def _write_on_tensorboard(self, metrics, stage):
        with self.writer.as_default():
            for key, value in metrics.items():
                tf.summary.scalar(stage + '/' + key, value.result(), self.steps)
                self.writer.flush()
