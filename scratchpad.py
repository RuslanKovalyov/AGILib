from snn.dendrites import Dendrite
from snn.membranes import Membrane
from snn.axons import Axon
from snn.synapses import Synapse
from snn.cores import Core
from snn.neurons import Neuron

# Examples of using modules, separated with input/output simulation

def synapse_usage():
    # Example of Synapse usage
    print('\n\n\n')
    print('Synapse usage example:')
    print('\n\n')

    synapse = Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1)

    synapse.transmit()
    print("Neurotransmitter level: ", synapse.neurotransmitter_level)   # Should be 99
    print("Received neurotransmitter: ", synapse.receive())             # Should be "dopamine"
    print("Received neurotransmitter: ", synapse.receive())
    synapse.regenerate()
    print("Neurotransmitter level after regenerate: ", synapse.neurotransmitter_level) # Should be 99.1

def axon_usage():
    # Example of Axon usage
    print('\n\n\n')
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

def neuron_usage():
    # Example of Neuron usage
    print('\n\n\n')
    print('Neuron usage example:')
    print('\n\n')


    neuron = Neuron(core = Core(
                                dendrites =[Dendrite(weight=10) for _ in range(2)], # 2 dendrites TODO: randomize weights on first init
                                membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                                axon = Axon(
                                    [Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1) for _ in range(2)]), # 2 synapses
                                refractory_period=1.0
                                )
                    )

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


synapse_usage()
axon_usage()
neuron_usage()