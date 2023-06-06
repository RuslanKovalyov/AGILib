import random
class Neuron:
    #core responsible for the neuron's behavior (all logic staff of dendrites, membrane, etc).
    #kernel responsible for the genomics of the neuron (how many dendrites, how many neurons, etc. it's also sets the parameters of all blocks like membrane lykage, dendrite weight, etc)
    def __init__(self, core):
        # Initialize core
        self.core = core
        # self.kernel ...

        is_training = False # if true then neuron will be trained, else it will be used as trained neuron.
        # Next some different types of lerning which need to be separated out of the neuron logic, and wiill be picked up by the kernel's genomics.
        
        
    
    def simple_cycle_by_cycle_lerning(self, error):
        # modify connections between neurons in one network calculation cycle.

        # if error>0 then is positive error (motivation) witch will make connections stronger.
        # if error<0 then is negative error (punishment) witch will make connections weaker.
        # if error=0 then is no error (no lerning).
        # weight can flip positive to negative and vice versa automatically through leraning.

        if error != 0:
            for dendrite in self.core.dendrites:
                # if the neuron fires, reward or punish the dendrites involved in this calculation.

                # if dendrite.input_mediator != "":
                if dendrite.history_of_inputs[-1][0] != "":
                    # then reward or punish the dendrite
                    if self.core.membrane.spike:
                        dendrite.weight = round(dendrite.weight + error, 3)
                    else:
                        dendrite.weight = round(dendrite.weight - error, 3)
                    
                    # limit the weight of the dendrite
                    if dendrite.weight > dendrite.max_weight:
                        dendrite.weight = dendrite.max_weight
                    if dendrite.weight < dendrite.min_weight:
                        dendrite.weight = dendrite.min_weight

                pass # propagate the error with same sign to presynaptic neuron (connected to this dendrite)
                # error will be divided (ower learning time/cycles ) in range form 1 to number of post synaptic neurons(this layer) for minimising the error in pretrained network.
    
    def backward_propagate(self, error):
        # Apply the error to the current neuron
        self.simple_cycle_by_cycle_lerning(error = error)
        
        # If this neuron has been activated in the previous step,
        # propagate the error backwards recursively
        if self.core.membrane.spike:

            for dendrite in self.core.dendrites:
                if dendrite.history_of_inputs[-1][0] != "":
                    # Propagate the error backwards to the presynaptic neuron
                    # associated with this dendrite
                    if dendrite.post_synapse:
                        if hasattr(dendrite.post_synapse, 'parent_neuron'):
                            dendrite.post_synapse.parent_neuron.backward_propagate(error = error * dendrite.weight/10 ) # error * dendrite.weight? (not sure)
            
            pass
        else:
            for dendrite in self.core.dendrites:
                if dendrite.history_of_inputs[-1][0] != "":
                    # Propagate the error backwards to the presynaptic neuron
                    # associated with this dendrite
                    if dendrite.post_synapse:
                        if hasattr(dendrite.post_synapse, 'parent_neuron'):
                            dendrite.post_synapse.parent_neuron.backward_propagate(error = -error * dendrite.weight*random.uniform(0.5, 2) ) # error * dendrite.weight? (not sure)
            pass # 1 if neuron is not activated then no need to propagate error backwards.
                 # 2 propagate error with opposite sign? (not sure)

    def cumulative_lerning(self): # write error to history, make sum of all errors and make corrections of weights in sleep mode.
        pass

    def long_term_associative_lerning(self):
        # growth and development of connections (creation new, destruction, modification, etc.) between unobvious interconnected neurons with relatively long time intervals between their activation.
        pass

    def step(self):
        self.core.step()

class SensorNeuron:
    def __init__(self):
        self.input_value = 0 # input value from sensor can be any number from 0 to 1
        self.sensitivity = 0.5 # sensitivity of the sensor
        self.descharge_rate = 0.1 # rate at which the sensor discharges
        self.output_value = False # output value to sensor can be True or False

    def set_input(self, value):
        self.input_value = round(self.input_value + value, 3)
        if self.input_value > 1:
            self.input_value = 1
        
    def step(self):
        if self.input_value > self.sensitivity:
            self.output_value = True
            self.input_value = 0
        else:
            self.output_value = False
            if self.input_value > 0:
                self.input_value = round(self.input_value - self.descharge_rate, 3)
                if self.input_value < 0:
                    self.input_value = 0

    def receive(self):
        if self.output_value:
            return "simple-signal-mediator"
        else:
            return ""

class MotorNeuron:
    def __init__(self):
        self.output_value = 0 # output value to motor can be any number from 0 to 1
        self.post_synapses = []  # List of Dendritic synapse objects

    def connect(self, synapse_objects = []): # connect MotorNeuron to axonic synapses of MiddleNeurons
        self.post_synapses = synapse_objects

    def step(self):
        self.output_value = 0
        for synapse in self.post_synapses:
            if synapse.receive() != "":
                self.output_value += 1
        self.output_value = round(self.output_value / len(self.post_synapses), 3)


    
    
