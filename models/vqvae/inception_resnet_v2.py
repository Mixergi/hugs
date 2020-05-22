import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Activation, Add, BatchNormalization, Concatenate, Conv2D, Dense, GlobalAveragePooling2D, Lambda, MaxPooling2D


def Conv2D_bn(x, filters, num_row, num_col, padding='same', strides=(1, 1), activation='relu'):
    x = Conv2D(filters, kernel_size=(num_row, num_col),
               padding=padding, strides=strides)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    return x


def Scaling_Down(input_layer, scale):
    x = Lambda(lambda input_layer, scale: input_layer *
               scale, arguments={'scale': scale})(input_layer)
    x = Activation('relu')(x)

    return x


def Stem(input_layer):
    x = Conv2D_bn(input_layer, 32, 3, 3, strides=(2,2),padding='valid')
    x = Conv2D_bn(x, 32, 3, 3,padding='valid')
    x = Conv2D_bn(x, 64, 3, 3)

    branch_0 = MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='valid')(x)
    
    branch_1 = Conv2D_bn(x, 96, 3, 3, strides=(2,2), padding='valid')
    
    x = Concatenate()([branch_0, branch_1])
    
    branch_0 = Conv2D_bn(x, 64, 1, 1)
    branch_0 = Conv2D_bn(branch_0, 96, 3, 3, padding='valid')
    
    branch_1 = Conv2D_bn(x, 64, 1, 1)
    branch_1 = Conv2D_bn(branch_1, 64, 7, 1)
    branch_1 = Conv2D_bn(branch_1, 64, 1, 7)
    branch_1 = Conv2D_bn(branch_1, 96, 3, 3, padding='valid')
    
    x = Concatenate(name='test')([branch_0, branch_1])
    
    branch_0 = Conv2D_bn(x, 192, 3, 3, strides=(2,2), padding='valid')
    
    branch_1 = MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='valid')(x)
    
    x = Concatenate()([branch_0, branch_1])
    
    return x

def inception_resnet_v2_A(input_layer, scale=0.1):
    
    branch_1 = Conv2D_bn(input_layer, 32, 1, 1)
    
    branch_2 = Conv2D_bn(input_layer, 32, 1, 1)
    branch_2 = Conv2D_bn(branch_2, 32, 3, 3)

    branch_3 = Conv2D_bn(input_layer, 32, 1, 1)
    branch_3 = Conv2D_bn(branch_3, 48, 3, 3)
    branch_3 = Conv2D_bn(branch_3, 64, 3, 3)

    branches = Concatenate()([branch_1, branch_2, branch_3])
    branches = Conv2D_bn(branches, 384, 1, 1, activation=None)

    stem = Scaling_Down(branches, scale=scale)

    stem = Add()([input_layer, stem])

    return stem
    
def inception_resnet_v2_B(input_layer, scale=0.1):

    branch_1 = Conv2D_bn(input_layer, 192, 1, 1)

    branch_2 = Conv2D_bn(input_layer, 128, 1, 1)
    branch_2 = Conv2D_bn(branch_2, 160, 1, 7)
    branch_2 = Conv2D_bn(branch_2, 192, 7, 1)

    branches = Concatenate()([branch_1, branch_2])
    branches = Conv2D_bn(branches, 1152, 1, 1, activation=None)

    stem = Scaling_Down(branches, scale=scale)
    stem = Add()([input_layer, stem])

    return stem

def inception_resnet_v2_C(input_layer, scale=0.1):

    branch_1 = Conv2D_bn(input_layer, 192, 1, 1)

    branch_2 = Conv2D_bn(input_layer, 192, 1, 1)
    branch_2 = Conv2D_bn(branch_2, 224, 1, 3)
    branch_2 = Conv2D_bn(branch_2, 256, 3, 1)

    branches = Concatenate()([branch_1, branch_2])
    branches = Conv2D_bn(branches, 2144, 1, 1, activation=None)

    stem = Scaling_Down(branches, scale=scale)
    stem = Add()([input_layer, stem])

    return stem

def Reduction_A(input_layer):
    branch_1 = MaxPooling2D(pool_size=(3, 3), padding='valid', strides=(2, 2))(input_layer)

    branch_2 = Conv2D_bn(input_layer, 384, 3, 3, padding='valid', strides=(2, 2))

    branch_3 = Conv2D_bn(input_layer, 256, 1, 1)
    branch_3 = Conv2D_bn(branch_3, 256, 3, 3)
    branch_3 = Conv2D_bn(branch_3, 384, 3, 3, padding='valid', strides=(2, 2))

    x = Concatenate()([branch_1, branch_2, branch_3]) 
    
    return x

def Reduction_B(input_layer):

    branch_1 = MaxPooling2D(pool_size=(3, 3), padding='valid', strides=(2, 2))(input_layer)

    branch_2 = Conv2D_bn(input_layer, 256, 1, 1)
    branch_2 = Conv2D_bn(branch_2, 384, 3, 3, padding='valid', strides=(2, 2))

    branch_3 = Conv2D_bn(input_layer, 256, 1, 1)
    branch_3 = Conv2D_bn(input_layer, 288, 3, 3, padding='valid', strides=(2, 2))

    branch_4 = Conv2D_bn(input_layer, 256, 1, 1)
    branch_4 = Conv2D_bn(branch_4, 288, 3, 3)
    branch_4 = Conv2D_bn(branch_4, 320, 3, 3, padding='valid', strides=(2, 2))

    x = Concatenate()([branch_1, branch_2, branch_3, branch_4])
    
    return x

def inception_resnet_v2(input_shape):

    image_input = Input(shape=input_shape)

    x = Stem(image_input)

    for _ in range(5):
        x = inception_resnet_v2_A(x)

    x = Reduction_A(x)

    for _ in range(10):
        x = inception_resnet_v2_B(x)

    x = Reduction_B(x)

    for _ in range(5):
        x = inception_resnet_v2_C(x)

    x = GlobalAveragePooling2D()(x)

    return Model(image_input, x)

if __name__ == "__main__":
    from tensorflow.keras.utils import plot_model

    model = inception_resnet_v2((299, 299, 3))

    plot_model(model)

    model.summary()
