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

class Brain:
    def __init__(self, input_size, hidden_size=[4,], output_size=1):
         # Create sensor neurons
        self.sensors = [SensorNeuron() for _ in range(input_size)]

        # Define network topology
        self.topology = hidden_size

        # Initialize empty list to hold all layers of neurons
        self.layers = []
        # Create each layer
        for i, num_neurons in enumerate(self.topology):
            # Create neurons for the layer
            layer = [
                Neuron(core=Core(
                    dendrites=[Dendrite(weight=random.uniform(-20, 20))], 
                    membrane=Membrane(threshold=20.0, reset_ratio=0.0, leakage=1),
                    axon=Axon([Synapse(transmitter_type='simple-signal-mediator', initial_level=100, regenerate_rate=1)]),
                    refractory_period=0, mode='cycle-train')) for _ in range(num_neurons)
            ]
            # bind Synapse to parent Neuron
            for neuron in layer:
                neuron.core.axon.synapses[0].parent_neuron = neuron
                

            # If this is the first layer, connect the neurons to the sensors
            if i == 0:
                for j in range(num_neurons):
                    layer[j].core.dendrites[0].connect(self.sensors[j % input_size])
            # If this is not the first layer, connect the neurons to the neurons in the previous layer
            else:
                for j in range(num_neurons):
                    layer[j].core.dendrites[0].connect(self.layers[i-1][j % len(self.layers[i-1])].core.axon.synapses[0])
            # Add the layer to the list of layers
            self.layers.append(layer)

        # Create motor neurons, each connected to a neuron in the last layer
        self.motors = [MotorNeuron() for _ in range(output_size)]
        for i in range(output_size):
            self.motors[i].connect([self.layers[-1][i].core.axon.synapses[0]])

        # Training
        # for _ in range(50):
    def input(self, input_data):
        # Set input for the sensors
        for i in range(len(self.sensors)):
            self.sensors[i].set_input(input_data[i])

    def step(self):

        # Step the sensors
        for sensor in self.sensors:
            sensor.step()

        # Process the inputs with the neurons in each layer and train them
        for layer in self.layers:
            for neuron in layer:
                neuron.step()

        # Step the motors
        for motor in self.motors:
            motor.step()
        
        return [motor.output_value for motor in self.motors]

    def train(self, error):                    
        errors = []  # Calculate the appropriate errors here
        for i, neuron in enumerate(self.layers[-1]):
            # neuron.backward_propagate(errors[i])
            if neuron.core.membrane.spike:
                    neuron.backward_propagate(error = error)
            else:
                neuron.backward_propagate(error = -error)

        # more errors stimulations for all layers to fasten the training ( not sure if it is correct )
        for i in range(len(self.layers)-1, -1, -1):
            layer = self.layers[i]
            for j in range(len(layer)):
                neuron = layer[j]
                if neuron.core.membrane.spike:
                    neuron.backward_propagate(error = error)
                else:
                    neuron.backward_propagate(error = -error)

                

