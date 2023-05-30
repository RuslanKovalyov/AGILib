class Neuron:
    #core responsible for the neuron's behavior (all logic staff of dendrites, membrane, etc).
    #kernel responsible for the genomics of the neuron (how many dendrites, how many neurons, etc. it's also sets the parameters of all blocks like membrane lykage, dendrite weight, etc)
    def __init__(self, core):
        # Initialize core
        self.core = core
        # self.kernel ...

    def step(self):
        self.core.step()
