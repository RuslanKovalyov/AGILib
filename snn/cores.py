class Core:
    def __init__(self, dendrites, membrane, axon, refractory_period=1.0):
        self.refractory_period = refractory_period  # Refractory period after a spike (in cycles)
        self.refractory_time_remaining = 0  # Time left in refractory period
        self.dendrites = dendrites # A list of dendrites
        self.membrane = membrane
        self.axon = axon


    def step(self):

        # TODO: set input to dendrites from axon's synapses

        total_input = sum(dendrite.step() for dendrite in self.dendrites)   # Accumulate all the dendrite signals
        refractory = self.refractory_time_remaining > 0                     # Check if the neuron is in refractory period
        self.membrane.step(total_input, refractory)                         # Update the membrane potential
        if self.membrane.spike:                                             # If the neuron spiked...
            self.refractory_time_remaining = self.refractory_period         # Enter the refractory period
        else:
            self.refractory_time_remaining = max(0, self.refractory_time_remaining - 1)  # Decrease the time remaining in the refractory period
        self.axon.step(self.membrane.v_m, self.membrane.spike)              # Provide the membrane potential and spike to the axon
