import argparse
import gc
import math
import multiprocessing
import os
import random

import tqdm

from hparams.AudioParams import AudioParams
from preprocess.audio import *
from preprocess.mels import *
from utils.audio import *


def to_mel_and_save(save_dir, file_name, data, hparams):
    mels = wav_to_mels(data, hparams)

    save_wav_to_npy(os.path.join(save_dir, 'wav/' + file_name), np.array(data))
    save_mels(os.path.join(save_dir, 'mels/' + file_name), mels)


def preprocess(file_list, save_dir, args):
    audio_params = AudioParams()

    pool = multiprocessing.Pool(args.n_workers)

    for i in tqdm.tqdm(range(len(file_list) // args.load_size + 1)):
        if args.load_size * i + 20 < len(file_list):
            wav_data = pool.starmap(load_wav, [(os.path.join(args.data_dir, file_name), audio_params)
                                               for file_name in
                                               file_list[args.load_size * i: args.load_size * (i + 1)]])
        else:
            wav_data = pool.starmap(load_wav, [(os.path.join(args.data_dir, file_name), audio_params)
                                               for file_name in
                                               file_list[args.load_size * i:]])

        name_number = len(os.listdir(os.path.join(save_dir, 'wav')))

        preprocessed_wav = pool.starmap(split_data, [(data, audio_params) for data in wav_data])

        preprocessed_wav = sum(preprocessed_wav, [])

        pool.starmap(to_mel_and_save,
                     [(save_dir, str(name_number + i), data, audio_params) for i, data in enumerate(preprocessed_wav)])

        # To Prevent Memory Shortage
        gc.collect()


def main(args):
    random.seed(args.random_seed)
    wav_list = os.listdir(args.data_dir)
    random.shuffle(wav_list)

    train_index = int(len(wav_list) * (1 - args.validation_splits))
    train_list = wav_list[:train_index]
    validation_list = wav_list[train_index:]

    print('making train data')
    train_output = os.path.join(args.outputs_dir, 'train')
    preprocess(train_list, train_output, args)

    print('making validation data')
    validation_output = os.path.join(args.outputs_dir, 'validation')
    preprocess(validation_list, validation_output, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', default='./data/music', type=str)
    parser.add_argument('--load_size', default=20, type=int)
    parser.add_argument('--outputs_dir', default='./preprocessed_data/MelGAN', type=str)
    parser.add_argument('--n_workers', default=multiprocessing.cpu_count(), type=int)
    parser.add_argument('--validation_splits', default=0.2, type=float)
    parser.add_argument('--random_seed', default=None, type=int)
    args = parser.parse_args()

    # making save dir
    os.makedirs(args.outputs_dir, exist_ok=True)
    train_dir = os.path.join(args.outputs_dir, 'train')
    validation_dir = os.path.join(args.outputs_dir, 'validation')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(os.path.join(train_dir, 'wav'), exist_ok=True)
    os.makedirs(os.path.join(train_dir, 'mels'), exist_ok=True)
    os.makedirs(validation_dir, exist_ok=True)
    os.makedirs(os.path.join(validation_dir, 'wav'), exist_ok=True)
    os.makedirs(os.path.join(validation_dir, 'mels'), exist_ok=True)
    main(args)
