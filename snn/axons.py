class Axon:
    def __init__(self, synapses):
        # banch of synapses
        self.synapses = synapses # A list of synapses


    def step(self, v_m, spike):
        # If the neuron spiked, transmit a neurotransmitter else process ather stuff like growth, connection creation, etc
        if spike:
            for synapse in self.synapses:
                synapse.transmit()
        else:
            for synapse in self.synapses:
                synapse.regenerate()
            
            # TODO: Add code to process growth, connection creation, etc depending on the value of v_m