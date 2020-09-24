import tensorflow as tf
from tensorflow.keras.layers import Activation, Add, AveragePooling1D, Concatenate, Conv1D, Conv2DTranspose, LeakyReLU


class ReflectionPad1d(tf.keras.layers.Layer):
    def __init__(self, pad_size, mode='REFLECT', **kwargs):
        super(ReflectionPad1d, self).__init__(**kwargs)

        self.pad_size = pad_size
        self.mode = mode

    def call(self, inputs):
        return tf.pad(inputs, [[0, 0], [self.pad_size, self.pad_size], [0, 0]], mode=self.mode)


class Conv1DTranspose(tf.keras.layers.Layer):
    def __init__(self, filters, kernel_size, strides=1, padding='valid', **kwargs):
        super(Conv1DTranspose, self).__init__(**kwargs)

        self.transpose = Conv2DTranspose(filters=filters, kernel_size=(kernel_size, 1),
                                         strides=(strides, 1), padding=padding)

    def call(self, inputs):
        x = tf.expand_dims(inputs, 2)
        x = self.transpose(x)
        x = tf.squeeze(x, 2)

        return x


class ResidualStack(tf.keras.layers.Layer):
    def __init__(self, filters, kernel_size, dilation_rate=1, **kwargs):
        super(ResidualStack, self).__init__(**kwargs)

        self.layers = [
            LeakyReLU(alpha=0.2),
            ReflectionPad1d((kernel_size - 1) // 2 * dilation_rate),
            Conv1D(filters=filters, kernel_size=kernel_size, dilation_rate=dilation_rate),
            LeakyReLU(alpha=0.2),
            Conv1D(filters=filters, kernel_size=1, dilation_rate=1)
        ]

        self.shortcut = Conv1D(filters=filters, kernel_size=1)
        self.add = Add()

    def call(self, inputs):
        x = inputs

        for layer in self.layers:
            x = layer(x)

        shortcut = self.shortcut(inputs)

        x = self.add([x, shortcut])

        return x


class Conv1DGroup(tf.keras.layers.Layer):
    def __init__(self, filters, kernel_size, strides=1, padding='valid', groups=1, **kwargs):
        super(Conv1DGroup, self).__init__(**kwargs)

        self.groups = groups

        n_filters = [filters // groups] * groups

        for i in range(filters % groups):
            filters[i] += 1

        self.layers = []

        for i, n_filter in enumerate(n_filters):
            self.layers.append(Conv1D(filters=n_filter, kernel_size=kernel_size,
                                      strides=strides, padding=padding))

        self.concat = Concatenate()

    def call(self, inputs):
        splited_inputs = tf.split(inputs, self.groups, axis=-1)

        outputs = []

        for input_tensor, layer in zip(splited_inputs, self.layers):
            outputs.append(layer(input_tensor))
        outputs = self.concat(outputs)

        return outputs


class Generator(tf.keras.Model):
    def __init__(self, **kwargs):
        super(Generator, self).__init__(**kwargs)

        input_size = 512

        upsampling = [8, 8, 2, 2]

        self.layer_blocks = [
            ReflectionPad1d(pad_size=3),
            Conv1D(filters=input_size, kernel_size=7)
        ]

        for i, upsample in enumerate(upsampling):
            self.layer_blocks += [
                LeakyReLU(alpha=0.2),
                Conv1DTranspose(input_size // 2 ** (i + 1), upsample * 2, upsample, padding='same')
            ]

            for j in range(3):
                self.layer_blocks += [
                    ResidualStack(input_size // 2 ** (i + 1), kernel_size=3, dilation_rate=3 ** j)
                ]

        self.layer_blocks += [
            LeakyReLU(alpha=0.2),
            Conv1D(filters=1, kernel_size=7, strides=1, padding='same'),
            Activation('tanh')
        ]

    def call(self, inputs):
        x = inputs

        for layer in self.layer_blocks:
            x = layer(x)

        return x


class Discriminator_Block(tf.keras.Model):
    def __init__(self, **kwargs):
        super(Discriminator_Block, self).__init__(**kwargs)

        downsampling = [4, 4, 4, 4]
        filter_list = [64, 256, 1024, 1024]

        self.layer_blocks = []

        self.layer_blocks += [
            ReflectionPad1d(7),
            Conv1D(filters=16, kernel_size=15, strides=1),
        ]

        for i in range(4):
            self.layer_blocks.append(Conv1DGroup(filters=filter_list[i], kernel_size=41,
                                                 strides=downsampling[i], groups=4 ** (1 + i), padding='same'))

        self.layer_blocks += [
            Conv1D(filters=1024, kernel_size=5, strides=1, padding='same'),
            Conv1D(filters=1, kernel_size=3, strides=1, padding='same')]

        self.activation = LeakyReLU(alpha=0.2)

    def call(self, inputs):
        outputs = []
        x = self.layer_blocks[0](inputs)
        for layer in self.layer_blocks[1:-1]:
            x = layer(x)
            x = self.activation(x)
            outputs.append(x)

        x = self.layer_blocks[-1](x)
        outputs.append(x)

        return outputs


class Discriminator(tf.keras.Model):
    def __init__(self, **kwargs):
        super(Discriminator, self).__init__(**kwargs)

        self.discriminator_blocks = [Discriminator_Block() for i in range(3)]

        self.avgpool = AveragePooling1D(pool_size=4, strides=2)

    def call(self, inputs):
        outputs = []
        for discriminator in self.discriminator_blocks:
            x = discriminator(inputs)
            outputs.append(x)
            inputs = self.avgpool(inputs)

        return outputs
