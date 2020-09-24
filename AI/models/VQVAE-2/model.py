import os

import numpy as np
import tensorflow as tf

def initializer(initializer_seed):
  return tf.keras.initializers.glorot_uniform(initializer_seed)

class Quantizer(tf.keras.layers.Layer):
  def __init__(self, k, **kwargs):
        super(Quantizer, self).__init__(**kwargs)
        self.k = k
    
  def build(self, input_shape):
      self.d = int(input_shape[-1])
      rand_init = tf.keras.initializers.VarianceScaling(distribution="uniform")
      self.codebook = self.add_weight(shape=(self.k, self.d), initializer=rand_init, trainable=True)
      
  def call(self, inputs):
      lookup_ = tf.reshape(self.codebook, shape=(1, 1, 1, self.k, self.d))
      z_e = tf.expand_dims(inputs, -2)
      dist = tf.norm(z_e - lookup_, axis=-1)
      k_index = tf.argmin(dist, axis=-1)
      return k_index
  
  def sample(self, k_index):
      lookup_ = tf.reshape(self.codebook, shape=(1, 1, 1, self.k, self.d))
      k_index_one_hot = tf.one_hot(k_index, self.k)
      z_q = lookup_ * k_index_one_hot[..., None]
      z_q = tf.reduce_sum(z_q, axis=-2)
      return z_q

class ResBlock(tf.keras.layers.Layer):
  def __init__(self, filters, initializer_seed=42, **kwargs):
    super(ResBlock, self).__init__(**kwargs)

    self.filters = filters
    self.initializer_seed = initializer_seed

  def build(self, input_shape):
    output_filters = input_shape[-1]

    self.blocks = [
      tf.keras.layers.ReLU(),
      tf.keras.layers.Conv2D(self.filters,
                             3,
                             padding='same',
                             kernel_initializer=initializer(self.initializer_seed)),
      tf.keras.layers.ReLU(),
      tf.keras.layers.Conv2D(output_filters,
                             1,
                             padding='same',
                             kernel_initializer=initializer(self.initializer_seed))
    ]

  def call(self, inputs):
    x = inputs 

    for block in self.blocks:
      x = block(x)
    
    return inputs + x

class Resnet(tf.keras.layers.Layer):
  def __init__(self, n_residual, filters, initializer_seed=42, **kwargs):
    super(Resnet, self).__init__(**kwargs)

    self.blocks = []

    for i in range(n_residual):
      self.blocks.append(ResBlock(filters, initializer_seed))
      
  def call(self, inputs):
    x = inputs 

    for block in self.blocks:
      x = block(x)

    return x

class Encoder(tf.keras.layers.Layer):
  def __init__(self, filters, kernel_size, strides, n_residual, res_filters, **kwargs):
    super(Encoder, self).__init__(**kwargs)

    blocks = []

    for f, k, s in zip(filters, kernel_size, strides):
      blocks += [ 
                 tf.keras.layers.Conv2D(f, k, s, padding='same'),
                 tf.keras.layers.ReLU()
      ]

    blocks = blocks[:-1]

    blocks += [
               Resnet(n_residual, res_filters),
               tf.keras.layers.ReLU()
    ]

    self.layers = blocks

  def call(self, inputs):

    x = inputs

    for layer in self.layers:
      x = layer(x)

    return x


class Decoder(tf.keras.layers.Layer):
  def __init__(self, filters, kernel_size, strides, n_residual, res_filters, **kwargs):
    super(Decoder, self).__init__(**kwargs)

    blocks = [tf.keras.layers.Conv2D(filters[0], 3, padding='same'),
              Resnet(n_residual, res_filters),
               tf.keras.layers.ReLU()]

    for f, k, s in zip(filters, kernel_size, strides):
      blocks += [ 
                 tf.keras.layers.Conv2DTranspose(f, k, s, padding='same'),
                 tf.keras.layers.ReLU()
      ]


    self.layers = blocks

  def call(self, inputs):

    x = inputs

    for layer in self.layers:
      x = layer(x)

    return x

class VQVAE(tf.keras.Model):
  def __init__(self):
    super(VQVAE, self).__init__()

    self.encoder_b =  Encoder([128, 256], [3, 3], [(2, 1), (2, 2)], 1, 256)
    self.encoder_m = Encoder([256, 512], [3, 3], [2, 2], 1, 512)
    self.encoder_t = Encoder([512, 512], [3, 3], [2, 2], 1, 768)

    self.vq_conv_b = tf.keras.layers.Conv2D(256, 1, padding='same')
    self.vq_conv_m = tf.keras.layers.Conv2D(512, 1, padding='same')

    self.vq_b = Quantizer(256)
    self.vq_m = Quantizer(256)
    self.vq_t = Quantizer(256)

    self.decoder_b = Decoder([256, 128], [3, 3], [(2, 2), (2, 1)], 1, 256)
    self.decoder_m = Decoder([512, 256], [3, 3], [2, 2], 1, 512)
    self.decoder_t = Decoder([512, 512], [3, 3], [2, 2], 1, 768)

    self.upsample = tf.keras.layers.Conv2D(1, 1, 1, padding='same')

  def call(self, inputs):
    return self.encoder(inputs)

  def encoder(self, inputs):
    enc_b = self.encoder_b(inputs)
    enc_m = self.encoder_m(enc_b)
    enc_t = self.encoder_t(enc_m)

    idx_t = self.vq_t(enc_t)
    vq_t = self.vq_t.sample(idx_t)
    dec_t = self.decoder_t(vq_t)
    
    mid_cat = tf.concat([enc_m, dec_t], -1)
    mid = self.vq_conv_m(mid_cat)

    idx_m = self.vq_m(mid)
    vq_m = self.vq_m.sample(idx_m)
    dec_m = self.decoder_m(vq_m)

    bot_cat = tf.concat([enc_b, dec_m], -1)
    bot = self.vq_conv_b(bot_cat)

    idx_b = self.vq_b(bot)
    vq_b = self.vq_b.sample(idx_b)
    dec_b = self.decoder_b(vq_b)

    output = self.upsample(dec_b)

    return output

def get_data_dir(data_folder):

  file = []

  for genre in os.listdir(data_folder):
    genre_dir = os.path.join(data_folder, genre)

    for file_name in os.listdir(genre_dir):
      file_dir = os.path.join(genre_dir, file_name)

      file.append(file_dir)


  return file