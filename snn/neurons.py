import random


class Neuron:
    """
    Represents a single neuron in a neural network.
    """
    def __init__(self, core):
        """
        Initializes a Neuron instance.

        Args:
            core: Represents the neuron's core which contains all the logic staff of dendrites, membrane, etc.

        Attributes:
            core: Represents the neuron's core.
            is_training: A boolean representing whether the neuron is in the training phase or not.
        """
        self.core = core
        self.is_training = False

    def simple_cycle_by_cycle_learning(self, error):
        """
        Modifies connections between neurons in one network calculation cycle.

        Args:
            error: Represents the error used in the learning process. Can be positive, negative or zero.
                   Positive errors make connections stronger (motivation).
                   Negative errors make connections weaker (punishment).
                   Zero errors lead to no learning.
        """
        if error != 0:
            for dendrite in self.core.dendrites:
                if dendrite.last_input_state and dendrite.last_input_state[0] != "":        # if input of dendrite have some transmitter (not empty string)
                    # the error is applied to the dendrite's weight
                    dendrite.weight = round(dendrite.weight + error, 3)
                    # the weight is limited to the range [min_weight, max_weight]
                    dendrite.weight = max(min(dendrite.weight, dendrite.max_weight), dendrite.min_weight)

    def backward_propagate(self, error):
        """
        Applies the error to the current neuron and recursively propagates the error backwards.

        Args:
            error: Represents the error used in the learning process.
        """
        self.simple_cycle_by_cycle_learning(error)

        
        # for dendrite in self.core.dendrites:
        #     if dendrite.last_input_state and dendrite.last_input_state[0] != "":                # if input of dendrite have some transmitter (not empty string)
        #         if dendrite.post_synapse and hasattr(dendrite.post_synapse, 'parent_neuron'):   # if dendrite have post_synapse and post_synapse have parent_neuron
        #             if self.core.membrane.spike:
        #                 dendrite.post_synapse.parent_neuron.backward_propagate(error=error + dendrite.weight)
        #             else:
        #                 # opposite sign of error with random coefficient
        #                 dendrite.post_synapse.parent_neuron.backward_propagate(error=-(error + dendrite.weight * random.uniform(0.7, 1.3)))

    def cumulative_learning(self):
        """
        Writes error to history. Correct weights in sleep mode.
        """
        pass

    def long_term_associative_learning(self):
        """
        Growth and development of connections (creation new, destruction, modification, etc.) 
        between unobvious interconnected neurons with relatively long time intervals between their activation.
        """
        pass

    def step(self):
        """
        Executes a step in the neuron's life-cycle.
        """
        self.core.step()


class SensorNeuron:
    """
    Represents a sensor neuron in a neural network.
    """
    def __init__(self):
        """
        Initializes a SensorNeuron instance.

        Attributes:
            input_value: Represents the input value from the sensor, can be any number from 0 to 1.
            sensitivity: Represents the sensitivity of the sensor ( simplyfied as a threshold value).
            leak_rate: Represents the rate at which the sensor discharges.
            output_value: Represents the output value to sensor, can be True or False.
        """
        self.input_value = 0
        self.sensitivity = 0.5
        self.leak_rate = 0.1
        self.output_value = False 

    def set_input(self, value):
        """
        Sets the input value for the sensor.

        Args:
            value: Represents the input value to set.
        """
        self.input_value = round(self.input_value + value, 3)
        # the input value is limited to the range [0, 1]
        self.input_value = min(self.input_value, 1)

    def step(self):
        """
        Executes a step in the sensor neuron's life-cycle.
        """
        if self.input_value > self.sensitivity:
            self.output_value = True
            self.input_value = 0
        else:
            self.output_value = False
            if self.input_value > 0:
                self.input_value = round(self.input_value - self.leak_rate, 3)
                # the input value is limited to the range [0, 1]
                self.input_value = max(self.input_value, 0)

    def receive(self):
        """
        Gets the output value of the sensor neuron.

        Returns:
            str: Returns "transmitter" if the output_value is True, otherwise returns an empty string.
        """
        return "simple-signal-mediator" if self.output_value else ""


class MotorNeuron:
    """
    Represents a motor neuron in a neural network.
    """
    def __init__(self):
        """
        Initializes a MotorNeuron instance.

        Attributes:
            output_value: Represents the output value to the motor, can be any number from 0 to 1.
            post_synapses: A list of Dendritic synapse objects.
        """
        self.output_value = 0
        self.post_synapses = []

    def connect(self, synapse_objects=[]):
        """
        Connects the MotorNeuron to axonic synapses of Middle layer neurons.

        Args:
            synapse_objects: A list of synapse objects to connect.
        """
        self.post_synapses = synapse_objects

    def step(self):
        """
        Executes a step in the motor neuron's life-cycle.
        """
        self.output_value = 0
        for synapse in self.post_synapses:
            if synapse.receive() != "": # if synapse have some transmitter (not empty string)
                self.output_value += 1
        self.output_value = self.output_value
