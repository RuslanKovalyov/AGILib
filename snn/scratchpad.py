

# Tested Classes and already in separate files:
from dendrites import Dendrite
from membranes import Membrane

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

class Synapse:
    #By default creating a synapse connected to axon, and dendrite on growth to nearby axon will find this synapse and connect to it.
    #If not enough synapses, new synapse will be created with chosen neurotransmitter type.

    def __init__(self, transmitter_type='simple-signal', initial_level=100, regenerate_rate=0.5):
        self.neurotransmitter_level = initial_level # Level of neurotransmitter available (100 = fully loaded)
        self.max_level = initial_level              # Maximum level of neurotransmitter
        self.regenerate_rate = regenerate_rate      # Rate at which the synapse regenerates neurotransmitter (progressive)
        self.transmitter_type = transmitter_type    # Type of neurotransmitter this synapse uses
        self.received_transmitter = ""              # The type of received neurotransmitter (empty string if no transmitter)

    # This function could be called whenever the neuron connected to this synapse's dendrite fires
    def transmit(self):
        # If there is neurotransmitter left, decrease the level by 1 and set the received_transmitter to the type
        if self.neurotransmitter_level >= 1:    # cnt transmit less than 1 neurotransmitter
            self.neurotransmitter_level -= 1    # Decrease the neurotransmitter level
            self.received_transmitter = self.transmitter_type   # Set the received neurotransmitter to the corrent type of neurotransmitter stored in the synapse
        else:
            self.received_transmitter = ""      # If the neurotransmitter level is 0, set received_transmitter to an empty string

    # This function should be called each timestep to regenerate neurotransmitter
    def regenerate(self):
        # Calculate the amount to regenerate based on the regenerate rate and the remaining capacity by
        # rounding the result to 3 decimal places
        # minimum amount to regenerate is 0.001
        regenerate_amount = max(0.001,  round(self.regenerate_rate * (self.max_level - self.neurotransmitter_level),3))

        self.neurotransmitter_level += regenerate_amount # Increase the neurotransmitter level
        self.neurotransmitter_level = min(self.max_level, self.neurotransmitter_level) # Make sure the neurotransmitter level doesn't exceed the maximum

    # This function should be called to receive the neurotransmitter
    def receive(self):
        nt = self.received_transmitter # Store the type of the received neurotransmitter
        self.received_transmitter = "" # Reset the received neurotransmitter to an empty string
        return nt # Return the type of the received neurotransmitter

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

class Neuron:
    #core responsible for the neuron's behavior (all logic staff of dendrites, membrane, etc).
    #kernel responsible for the genomics of the neuron (how many dendrites, how many neurons, etc. it's also sets the parameters of all blocks like membrane lykage, dendrite weight, etc)
    def __init__(self):
        # Initialize core
        self.core = Core(   dendrites =[Dendrite(weight=10) for _ in range(2)], # 2 dendrites TODO: randomize weights on first init
                            membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                            axon = Axon(
                                [Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1) for _ in range(2)]), # 2 synapses
                            refractory_period=1.0
                        )
    def step(self):
        self.core.step()



print('\n\n\n')
# Example of Synapse usage
print('Synapse usage example:')
print('\n\n')

synapse = Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1)

synapse.transmit()
print("Neurotransmitter level: ", synapse.neurotransmitter_level)   # Should be 99
print("Received neurotransmitter: ", synapse.receive())             # Should be "dopamine"
print("Received neurotransmitter: ", synapse.receive())
synapse.regenerate()
print("Neurotransmitter level after regenerate: ", synapse.neurotransmitter_level) # Should be 99.1




print('\n\n\n')
# Example of Axon usage
print('Axon usage example:')
print('\n\n')

synapses = [Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1) for _ in range(10)]
axon = Axon(synapses)

axon.step(v_m=0, spike=True) # Transmit neurotransmitter
print("Neurotransmitter level: ", synapses[0].neurotransmitter_level)   # Should be 99
print("Received neurotransmitter: ", synapses[0].receive())             # Should be "dopamine"
axon.step(v_m=0, spike=False) # Regenerate neurotransmitter
print("Neurotransmitter level after regenerate: ", synapses[0].neurotransmitter_level)  # Should be 99.1
print("Received neurotransmitter: ", synapses[0].receive())             # Should be ""




print('\n\n\n')
# Example of Neuron usage
print('Neuron usage example:')
print('\n\n')

neuron = Neuron()

print('providing new weights to dendrites 9 + 10')
neuron.core.dendrites[0].set_weight(9)
neuron.core.dendrites[1].set_weight(10)
neuron.core.dendrites[0].input_mediator = "dopamine" # emulating that synapse 0 received input with dopamine marker
neuron.core.dendrites[1].input_mediator = "dopamine" # emulating that synapse 1 received input with dopamine marker
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m) # Should be 18.905 because of leakage
print("Spike: ", neuron.core.membrane.spike) # Should be False
print("Axon synapse 0 neurotransmitter level: ", neuron.core.axon.synapses[0].neurotransmitter_level) # Should be 100
print("Axon synapse 1 neurotransmitter level: ", neuron.core.axon.synapses[1].neurotransmitter_level) # Should be 100
print('Synapse 0 received neurotransmitter: ', neuron.core.axon.synapses[0].receive()) # Should be ""
print('\n')


print('weights of dendrites 0 + 0 and input mediator to dopamine,dopamine')
neuron.core.dendrites[0].set_weight(0)
neuron.core.dendrites[1].set_weight(0)
neuron.core.dendrites[0].input_mediator = "dopamine" # emulating that synapse 0 received input with dopamine marker
neuron.core.dendrites[1].input_mediator = "dopamine" # emulating that synapse 1 received input with dopamine marker
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m) # Should be less then 18.905 because of leakage
print("Spike: ", neuron.core.membrane.spike) # Should be False
print("Axon synapse 0 neurotransmitter level: ", neuron.core.axon.synapses[0].neurotransmitter_level) # Should be 100
print("Axon synapse 1 neurotransmitter level: ", neuron.core.axon.synapses[1].neurotransmitter_level) # Should be 100
print('Synapse 0 received neurotransmitter: ', neuron.core.axon.synapses[0].receive()) # Should be ""
print('\n')


print('weights of dendrites 0 + 5 and input mediator to dopamine,dopamine')
neuron.core.dendrites[0].set_weight(0)
neuron.core.dendrites[1].set_weight(5)
neuron.core.dendrites[0].input_mediator = "dopamine" # emulating that synapse 0 received input with dopamine marker
neuron.core.dendrites[1].input_mediator = "dopamine" # emulating that synapse 1 received input with dopamine marker
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m) # Should be 2 (reseted after spike)
print("Spike: ", neuron.core.membrane.spike) # Should be True because previous membrane potential was 18.**
print("Axon synapse 0 neurotransmitter level: ", neuron.core.axon.synapses[0].neurotransmitter_level) # Should be 99
print("Axon synapse 1 neurotransmitter level: ", neuron.core.axon.synapses[1].neurotransmitter_level) # Should be 99
print('Synapse 0 received neurotransmitter: ', neuron.core.axon.synapses[0].receive()) # Should be "dopamine"
print('\n')

print('weights of dendrites 0 + 0 and input mediator to dopamine,dopamine')
neuron.core.dendrites[0].set_weight(10)
neuron.core.dendrites[1].set_weight(10)
neuron.core.dendrites[0].input_mediator = "" # emulating that synapse 0 not any transmitter
neuron.core.dendrites[1].input_mediator = "" # emulating that synapse 1 not any transmitter
neuron.core.refractory_period = 1  # Refractory period after a spike (in cycles)
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m) # Should be 2 because of time in refractory period
print("Spike: ", neuron.core.membrane.spike) # Should be False
print("Axon synapse 0 neurotransmitter level: ", neuron.core.axon.synapses[0].neurotransmitter_level) # Should be 99.1 (regenerated)
print("Axon synapse 1 neurotransmitter level: ", neuron.core.axon.synapses[1].neurotransmitter_level) # Should be 99.1 (regenerated)
print('Synapse 0 received neurotransmitter: ', neuron.core.axon.synapses[0].receive()) # Should be ""
print('\n')
neuron.step()
print("Membrane potential: ", neuron.core.membrane.v_m) # Should be less than 2 (1.99) because refractory period is finished and leakage makes it closer to Resting membrane potential


