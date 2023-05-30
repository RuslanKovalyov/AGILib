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
        if self.received_transmitter != "":
            nt = self.received_transmitter # Store the type of the received neurotransmitter
            self.received_transmitter = "" # Reset the received neurotransmitter to an empty string
            return nt # Return the type of the received neurotransmitter
        else:
            return ""
