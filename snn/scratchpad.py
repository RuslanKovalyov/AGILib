class Dendrite:
    def __init__(self, synapse_weight=1.0):
        self.synapse_weight = synapse_weight  # Synaptic weight
        self.input_value = 0.0  # Input value received through the dendrite

    def set_input(self, input_value):
        self.input_value = input_value

    def step(self):
        output = self.input_value * self.synapse_weight  # Calculate the output signal
        self.input_value = 0  # Reset the input after it's been used
        return output

# class Membrane is Tested and already stored in membranes.py
from membranes import Membrane


class Core:
    def __init__(self, num_dendrites=1, refractory_period=2.0):
        self.refractory_period = refractory_period  # Refractory period after a spike
        self.refractory_time_remaining = 0  # Time left in refractory period
        self.membrane = Membrane()
        self.dendrites = [Dendrite() for _ in range(num_dendrites)]  # A list of dendrites

    def step(self):
        total_input = sum(dendrite.step() for dendrite in self.dendrites)   # Accumulate all the dendrite signals
        refractory = self.refractory_time_remaining > 0                     # Check if the neuron is in refractory period
        self.membrane.step(total_input, refractory)                         # Update the membrane potential
        if self.membrane.spike:                                             # If the neuron spiked...
            self.refractory_time_remaining = self.refractory_period         # Enter the refractory period
        else:
            self.refractory_time_remaining = max(0, self.refractory_time_remaining - 1)  # Decrease the time remaining in the refractory period

class Neuron:
    #core responsible for the neuron's behavior (all logic staff of dendrites, membrane, etc).
    #kernel responsible for the genomics of the neuron (how many dendrites, how many neurons, etc. it's also sets the parameters of all blocks like membrane lykage, dendrite weight, etc)
    def __init__(self, num_dendrites=1):
        # Initialize core
        self.core = Core(num_dendrites)

    def step(self):
        self.core.step()


# Example of usage
neuron = Neuron(num_dendrites=2)
neuron.core.dendrites[0].set_input(10.5)
neuron.core.dendrites[1].set_input(10.3)
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m)
print("spike: ", neuron.core.membrane.spike)
