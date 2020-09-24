class MelGANparams:
    def __init__(self,
                 discriminator_optimizer_lr=1e-3,
                 generator_optimizer_lr=1e-3,
                 epochs=50
                 ):

        self.discriminator_optimizer_lr = discriminator_optimizer_lr
        self.generator_optimizer_lr = generator_optimizer_lr
        self.epochs = epochs
