import tensorflow as tf
from tensorflow.keras import Input, Model


def inception_resnet_v2(input_shape, classes=1000):

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

    x = Dropout(0.8)(x)

    x = Dense(units=classes, activation='softmax')(x)

    return Model(image_input, x)

if __name__ == "__main__":
    from tensorflow.keras.utils import plot_model

    model = inception_resnet_v2((299, 299, 3))

    plot_model(model)

    model.summary()
