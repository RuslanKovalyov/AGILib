class Synapse:
    """
    A class representing a synapse in a neuron network. 

    By default, when a Synapse object is created, it is designed to connect to an Axon object.
    A dendrite, upon its growth reaching the vicinity of this synapse, will connect to it.
    If there aren't enough synapses, a new Synapse object will be created with the chosen neurotransmitter

    Attributes:
    neurotransmitter_level (int): the current level of neurotransmitter available in the synapse. (initial_level = fully loaded)
    max_level (int): the maximum level of available neurotransmitter in the synapse
    regenerate_rate (float): the rate at regenerates amount of neurotransmitter (progressive regeneration: less transmitters = faster regeneration)
    transmitter_type (str): the type of neurotransmitter this synapse uses
    received_transmitter (str): the type of received neurotransmitter (empty string if no transmitter)
    parent_neuron (object): the neuron object that this synapse belongs to (used for back propagation)
    """

    def __init__(self, transmitter_type='simple-signal', initial_level=100, regenerate_rate=0.5):
        """Initialize a Synapse instance with given parameters."""
        self.neurotransmitter_level = initial_level 
        self.max_level = initial_level              
        self.regenerate_rate = regenerate_rate      
        self.transmitter_type = transmitter_type    
        self.received_transmitter = ""              
        self.parent_neuron = None 

    def transmit(self):
        """
        Transmit the neurotransmitter from this synapse.
        
        This function is called whenever the neuron connected to this 
        synapse's dendrite fires. If there is neurotransmitter left, 
        it decreases the level by 1 and set the received_transmitter 
        to the type. If the neurotransmitter level is 0, it sets 
        received_transmitter to an empty string.
        """
        if self.neurotransmitter_level >= 1:
            self.neurotransmitter_level -= 1    
            self.received_transmitter = self.transmitter_type   
        else:
            self.received_transmitter = ""      

    def regenerate(self):
        """
        Regenerate neurotransmitter in this synapse.

        This function should be called each timestep to regenerate neurotransmitter. 
        It calculates the amount to regenerate based on the regenerate rate and 
        the remaining capacity, and ensures the neurotransmitter level doesn't exceed the maximum.
        minimum amount to regenerate is 0.001. 
        """
        regenerate_amount = max(0.001, round(self.regenerate_rate * (self.max_level - self.neurotransmitter_level), 3))
        self.neurotransmitter_level += regenerate_amount 
        self.neurotransmitter_level = min(self.max_level, self.neurotransmitter_level)

    def receive(self):
        """
        Receive the neurotransmitter to this synapse.
        
        This function should be called to receive the neurotransmitter.
        It stores the type of the received neurotransmitter and returns it.
        If there is no received neurotransmitter, it returns an empty string.
        """
        if self.received_transmitter != "":
            nt = self.received_transmitter 
            self.received_transmitter = "" 
            return nt
        else:
            return ""
