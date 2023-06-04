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

    membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5)
    membrane.v_m = 0
    membrane.spike = True

    # Example of Axon usage
    print('\n\n\n')
    print('Axon usage example:')
    print('\n\n')

    synapses = [Synapse(transmitter_type='dopamine', initial_level=100, regenerate_rate=0.1) for _ in range(10)]
    axon = Axon(synapses)
    axon.step(membrane) # Transmit neurotransmitter
    print("Neurotransmitter level: ", synapses[0].neurotransmitter_level)   # Should be 99
    print("Received neurotransmitter: ", synapses[0].receive())             # Should be "dopamine"
    membrane.spike = False
    axon.step(membrane) # Regenerate neurotransmitter
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

def pyramid(): # three neurons, two of them sensory, one of them motor [1,2] -> [3]
    neuron_1 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=20) for _ in range(1)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=100, regenerate_rate=0.1) for _ in range(1)]), # 1 synapses
                        refractory_period=0
                        )
            )# seted like sensory neuron

    neuron_2 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=20) for _ in range(1)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=100, regenerate_rate=0.1) for _ in range(1)]), # 1 synapses
                        refractory_period=0
                        )
            )# seted like sensory neuron

    neuron_3 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=5) for _ in range(2)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=100, regenerate_rate=0.1) for _ in range(1)]), # 1 synapses
                        refractory_period=0
                        )
            ) # seted like motor neuron
    nList = []
    nList.append(neuron_1)
    nList.append(neuron_2)
    nList.append(neuron_3)

    # initialize connections between neurons
    neuron_3.core.dendrites[0].connect(neuron_1.core.axon.synapses[0])
    neuron_3.core.dendrites[1].connect(neuron_2.core.axon.synapses[0])


    for _ in range(10):
        # initialize input to sensory neurons
        neuron_1.core.dendrites[0].input_mediator = ""
        neuron_2.core.dendrites[0].input_mediator = "some_neurotransmitter"
        # signal forwarding
        for n in nList:
            n.step()
        # print results
        print( '\n\n Neuron_3 | mV-', neuron_3.core.membrane.v_m, '| output: ', neuron_3.core.axon.synapses[0].receive())

def PyramedTrainer(): # create pyramid and train it
    neuron_1 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=20) for _ in range(1)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=10, regenerate_rate=1) for _ in range(1)]), # 1 synapses
                        refractory_period=0
                        )
            )# seted like sensory neuron

    neuron_2 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=20) for _ in range(1)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=10, regenerate_rate=1) for _ in range(1)]), # 1 synapses
                        refractory_period=0
                        )
            )# seted like sensory neuron

    neuron_3 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=2) for _ in range(2)], # 2 dendrites TODO: randomize weights on first init
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='some_neurotransmitter', initial_level=100, regenerate_rate=0.01) for _ in range(1)]), # 1 synapses
                        refractory_period=0,
                        mode='cycle-train',
                        )
            ) # seted like motor neuron
    nList = []
    nList.append(neuron_1)
    nList.append(neuron_2)
    nList.append(neuron_3)

    # initialize connections between neurons
    neuron_3.core.dendrites[0].connect(neuron_1.core.axon.synapses[0])
    neuron_3.core.dendrites[1].connect(neuron_2.core.axon.synapses[0])

    for _ in range(100): # train neuron_3 to react on active Neuron_1 if Neuron_2 is not active. if both active - no reaction
        # initialize input to sensory neurons
        neuron_1.core.dendrites[0].input_mediator = "some_neurotransmitter"
        neuron_2.core.dendrites[0].input_mediator = "some_neurotransmitter"

        # signal forwarding
        for n in nList:
            n.step()

        # train neuron_3
        if neuron_3.core.mode == 'cycle-train':
            if neuron_3.core.axon.synapses[0].received_transmitter != "some_neurotransmitter":
                print('error -0.1', "fire=",neuron_3.core.membrane.spike,'\t', 'weights', neuron_3.core.dendrites[0].weight, neuron_3.core.dendrites[1].weight, '\t output', neuron_3.core.axon.synapses[0].receive())
                neuron_3.simple_cycle_by_cycle_lerning(error = -0.1)
            else:
                print('error  0.1', "fire=",neuron_3.core.membrane.spike,'\t', 'weights', neuron_3.core.dendrites[0].weight, neuron_3.core.dendrites[1].weight, '\t output', neuron_3.core.axon.synapses[0].receive())
                neuron_3.simple_cycle_by_cycle_lerning(error = 0.1)
            # print( '\n', neuron_3.core.dendrites[0].history_of_inputs, '\n',neuron_3.core.dendrites[1].history_of_inputs,'\n\n')
            

    # train neuron_3 to react on Neuron_1 or Neuron_2 but not both
    # for _ in range(10):
    #     # initialize input to sensory neurons
    #     neuron_1.core.dendrites[0].input_mediator = ""
    #     neuron_2.core.dendrites[0].input_mediator = "some_neurotransmitter"
    #     # signal forwarding
    #     for n in nList:
    #         n.step()
    #     # print results
    #     print( '\n\n Neuron_3 | mV-', neuron_3.core.membrane.v_m, '| output: ', neuron_3.core.axon.synapses[0].receive())



# synapse_usage()
# axon_usage()
# neuron_usage()
# pyramid()
PyramedTrainer()