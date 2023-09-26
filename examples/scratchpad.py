import os
import random
import sys
import time

# Adjusting the path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from snn.dendrites import Dendrite
from snn.membranes import Membrane
from snn.axons import Axon
from snn.synapses import Synapse
from snn.cores import Core
from snn.neurons import Neuron, SensorNeuron, MotorNeuron

#-------------------------------------------------------------------------------------------------------------#
# IT IS NOT A TESTS !!!, JUST SOME SCRATCHPAD TO PLAY WITH MODULES AND SEE HOW THEY WORK                      #
# input/output simulations written hronologically together with development of modules and can be not actual. #
#-------------------------------------------------------------------------------------------------------------#

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
                neuron_3.simple_cycle_by_cycle_learning(error = -0.1)
            else:
                print('error  0.1', "fire=",neuron_3.core.membrane.spike,'\t', 'weights', neuron_3.core.dendrites[0].weight, neuron_3.core.dendrites[1].weight, '\t output', neuron_3.core.axon.synapses[0].receive())
                neuron_3.simple_cycle_by_cycle_learning(error = 0.1)
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

def simple_net(): # hand builded network
    # Please note that this network does not include back propagation mechanism, it's just a basic feed-forward network with simple cycle by cycle lerning.
    # Creating sensory neurons
    sensor_1 = SensorNeuron()
    sensor_2 = SensorNeuron()

    # Creating middle layer neurons
    neuron_1 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=0.5)], 
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='simple-signal-mediator', initial_level=10, regenerate_rate=1)]),
                        refractory_period=0,
                        mode='cycle-train')
    )

    neuron_2 = Neuron(core = Core(
                        dendrites =[Dendrite(weight=0.5)], 
                        membrane = Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                        axon = Axon(
                            [Synapse(transmitter_type='simple-signal-mediator', initial_level=10, regenerate_rate=1)]),
                        refractory_period=0,
                        mode='cycle-train')
    )

    # Creating motor neurons
    motor_1 = MotorNeuron()
    motor_2 = MotorNeuron()

    # Connecting sensory neurons to middle layer neurons
    neuron_1.core.dendrites[0].connect(sensor_1)
    neuron_2.core.dendrites[0].connect(sensor_2)

    # Connecting middle layer neurons to motor neurons
    motor_1.connect([neuron_1.core.axon.synapses[0]])
    motor_2.connect([neuron_2.core.axon.synapses[0]])

    # Training the network
    for _ in range(200):  # Run for 100 cycles
        # Set the inputs
        sensor_1.set_input(0.6)
        sensor_2.set_input(0.4)

        # Step through the network
        sensor_1.step()
        sensor_2.step()
        neuron_1.step()
        neuron_2.step()

        # Print current weights and apply learning
        if neuron_1.core.membrane.spike:
            print(f'Neuron 1 spiked, current weight: {neuron_1.core.dendrites[0].weight}')
            neuron_1.simple_cycle_by_cycle_learning(error = 0.3)
        else:
            print(f'Neuron 1 did not spike, current weight: {neuron_1.core.dendrites[0].weight}')
            neuron_1.simple_cycle_by_cycle_learning(error = -0.3)

        if neuron_2.core.membrane.spike:
            print(f'Neuron 2 spiked, current weight: {neuron_2.core.dendrites[0].weight}')
            neuron_2.simple_cycle_by_cycle_learning(error = 0.3)
        else:
            print(f'Neuron 2 did not spike, current weight: {neuron_2.core.dendrites[0].weight}')
            neuron_2.simple_cycle_by_cycle_learning(error = -0.3)

        motor_1.step()
        motor_2.step()

        # Print output values from the motor neurons
        print("Output from Motor Neuron 1:", motor_1.output_value)
        print("Output from Motor Neuron 2:", motor_2.output_value)
        print('\n')

def simple_net_2(): # builded network by using list comprehensions but back propagation is not implemented!
    # Create sensor neurons
    num_sensors = 4
    sensors = [SensorNeuron() for _ in range(num_sensors)]

    # Define network topology
    topology = [8,]

    # Initialize empty list to hold all layers of neurons
    layers = []

    # Create each layer
    for i, num_neurons in enumerate(topology):
        # Create neurons for the layer
        layer = [
            Neuron(core=Core(
                dendrites=[Dendrite(weight=random.uniform(0.1, 0.9))], 
                membrane=Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                axon=Axon([Synapse(transmitter_type='simple-signal-mediator', initial_level=10, regenerate_rate=1)]),
                refractory_period=0, mode='cycle-train')) for _ in range(num_neurons)
        ]
        # If this is the first layer, connect the neurons to the sensors
        if i == 0:
            for j in range(num_neurons):
                layer[j].core.dendrites[0].connect(sensors[j % num_sensors])
        # If this is not the first layer, connect the neurons to the neurons in the previous layer
        else:
            for j in range(num_neurons):
                layer[j].core.dendrites[0].connect(layers[i-1][j % len(layers[i-1])].core.axon.synapses[0])
        # Add the layer to the list of layers
        layers.append(layer)

    # Create motor neurons, each connected to a neuron in the last layer
    num_motors = 4
    motors = [MotorNeuron() for _ in range(num_motors)]
    for i in range(num_motors):
        motors[i].connect([layers[-1][i].core.axon.synapses[0]])

    # Training
    for _ in range(80):
        # Set input for the sensors
        for sensor in sensors:
            sensor.set_input(random.uniform(0.5, 0.9))
            sensor.step()

        # Process the inputs with the neurons in each layer and train them
        for layer in layers:
            for neuron in layer:
                neuron.step()
                if neuron.core.membrane.spike:
                    neuron.simple_cycle_by_cycle_learning(error = 0.3)
                else:
                    neuron.simple_cycle_by_cycle_learning(error = -0.3)

        # Step the motors
        for motor in motors:
            motor.step()

        # Output
        for i, motor in enumerate(motors):
            print(f"Output from Motor Neuron {i+1}: {motor.output_value}")
        print('\n')

def back_propagation_simple_cycle_by_cycle_train():

    # Create sensor neurons
    num_sensors = 4
    sensors = [SensorNeuron() for _ in range(num_sensors)]

    # Define network topology (first layer neurons will be connected to the sensors)
    topology = [32, 32, 4]

    # Initialize empty list to hold all layers of neurons
    layers = []

    # Create each layer
    for i, num_neurons in enumerate(topology):
        # Create neurons for the layer
        layer = [
            Neuron(core=Core(
                dendrites=[Dendrite(weight=random.uniform(0.1, 20))], 
                membrane=Membrane(threshold=20.0, reset_ratio=0.1, leakage=0.5),
                axon=Axon([Synapse(transmitter_type='simple-signal-mediator', initial_level=10, regenerate_rate=1)]),
                refractory_period=0, mode='cycle-train')) for _ in range(num_neurons)
        ]
        # bind Synapse to parent Neuron
        for neuron in layer:
            neuron.core.axon.synapses[0].parent_neuron = neuron
            

        # If this is the first layer, connect the neurons to the sensors
        if i == 0:
            for j in range(num_neurons):
                layer[j].core.dendrites[0].connect(sensors[j % num_sensors])
        # If this is not the first layer, connect the neurons to the neurons in the previous layer
        else:
            for j in range(num_neurons):
                layer[j].core.dendrites[0].connect(layers[i-1][j % len(layers[i-1])].core.axon.synapses[0])
        # Add the layer to the list of layers
        layers.append(layer)

    # Create motor neurons, each connected to a neuron in the last layer
    num_motors = 4
    motors = [MotorNeuron() for _ in range(num_motors)]
    for i in range(num_motors):
        motors[i].connect([layers[-1][i].core.axon.synapses[0]])

    # Training
    for _ in range(50):
        # Set input for the sensors
        for sensor in sensors:
            sensor.set_input(random.uniform(0.5, 0.9))
            sensor.step()

        # Process the inputs with the neurons in each layer and train them
        for layer in layers:
            for neuron in layer:
                neuron.step()

                    
        errors = []  # Calculate the appropriate errors here
        for i, neuron in enumerate(layers[-1]):
            # neuron.backward_propagate(errors[i])
            if neuron.core.membrane.spike:
                    neuron.backward_propagate(error = 10)
            else:
                neuron.backward_propagate(error = -10)




        # Step the motors
        for motor in motors:
            motor.step()

        # Output
        for i, motor in enumerate(motors):
            print(f"Output from Motor Neuron {i+1}: {motor.output_value}")
        print('\n')

# benchmark start time
start_time = time.time()

# synapse_usage()
# axon_usage()
# neuron_usage()
# pyramid()
# PyramedTrainer()
# simple_net()
# simple_net_2()
back_propagation_simple_cycle_by_cycle_train()

# benchmark end time
print("--- %s seconds ---" % (time.time() - start_time))