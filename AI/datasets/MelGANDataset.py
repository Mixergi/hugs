import os
import random
import sys

import numpy
import tensorflow as tf

from .MelDataset import MelDataset
from .WavDataset import WavDataset


class MelGANDataset:
    def __init__(self,
                 root_dir,
                 batch_size,
                 random_seed):

        random.seed(random_seed)
        random_seed = random.randint(0, sys.maxsize)

        self.root_dir = root_dir
        self.batch_size = batch_size
        self.meldataset = MelDataset(os.path.join(root_dir, 'mels'), random_seed)
        self.wavdataset = WavDataset(os.path.join(root_dir, 'wav'), random_seed)

    def get_length(self):
        return len(self.meldataset.file_list)

    def create(self):
        return tf.data.Dataset.zip((self.wavdataset.create(), self.meldataset.create()))\
            .prefetch(tf.data.experimental.AUTOTUNE)\
            .batch(self.batch_size)
