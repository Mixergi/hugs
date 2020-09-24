import argparse
import os

import numpy as np
import tensorflow as tf
import tqdm

from hparams.AudioParams import AudioParams
from datasets.MelGANDataset import MelGANDataset
from hparams.MelGANparams import MelGANparams
from models.MelGAN.trainer import MelGANTrainer


def main(args):
    audioparams = AudioParams()
    melganparams = MelGANparams()

    train_dataset = MelGANDataset(args.train_dir, args.batch_size, args.random_seed)
    validation_dataset = MelGANDataset(args.validation_dir, args.batch_size, args.random_seed)

    trainer = MelGANTrainer(melganparams.epochs, args.save_dir, args.log_dir)

    d_opt = tf.keras.optimizers.Adam(melganparams.discriminator_optimizer_lr)
    g_opt = tf.keras.optimizers.Adam(melganparams.generator_optimizer_lr)

    if args.load_model:
        trainer.load_model()

    trainer.compile(d_opt, g_opt)
    trainer.use_sample(args.sample_dir, args.sample_save_dir, audioparams.sample_rate)

    trainer.train(train_dataset, validation_dataset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', default=50, type=int)
    parser.add_argument('--batch_size', default=10, type=int)
    parser.add_argument('--train_dir', default='./preprocessed_data/MelGAN/train', type=str)
    parser.add_argument('--validation_dir', default='./preprocessed_data/MelGAN/validation', type=str)
    parser.add_argument('--save_dir', default='./saved_models/MelGAN', type=str)
    parser.add_argument('--load_model', default=False, type=bool)
    parser.add_argument('--sample_dir', default=None, type=str)
    parser.add_argument('--sample_save_dir', default='./sample/MelGAN', type=str)
    parser.add_argument('--random_seed', default=None, type=int)
    parser.add_argument('--log_dir', default='./logs/MelGAN/', type=str)
    args = parser.parse_args()

    generator_dir = os.path.join(args.save_dir, 'generator')
    args.generator_dir = generator_dir
    os.makedirs(generator_dir, exist_ok=True)

    discriminator_dir = os.path.join(args.save_dir, 'discriminator')
    args.discriminator_dir = discriminator_dir
    os.makedirs(discriminator_dir, exist_ok=True)

    os.makedirs(args.sample_save_dir, exist_ok=True)

    os.makedirs(args.log_dir, exist_ok=True)

    main(args)
