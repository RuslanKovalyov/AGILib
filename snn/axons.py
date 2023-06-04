class Axon:
    def __init__(self, synapses):
        # banch of synapses
        self.synapses = synapses # A list of synapses


    def step(self, membrane):
        # If the neuron spiked, transmit a neurotransmitter else process ather stuff like growth, connection creation, etc
        if membrane.spike:
            for synapse in self.synapses:
                synapse.transmit()
                synapse.regenerate()
        else:
            for synapse in self.synapses:
                synapse.regenerate()
            
            # TODO: Add code to process growth, connection creation, etc depending on the value of membrane.v_m