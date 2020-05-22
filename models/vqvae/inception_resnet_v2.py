import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Activation, BatchNormalization, concatenate, Conv2D, Dense, MaxPool2D

def Conv2d_bn(x, filters, num_row, num_col, padding='same', strides=(1, 1), activation='relu'):
    x = Conv2D(filters, kernel_size=(num_row, num_col), padding=padding, strides=strides)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    return x

def inception_resnet_v2():
    pass