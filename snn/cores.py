class Core:
    """
    This class represents the core component of a Neuron, encompassing the neuron's dendrites, membrane, and axon. 
    It coordinates the interactions between these components in a neuron's operation.

    Attributes:
        dendrites (list): List of dendrites for this neuron.
        membrane (Membrane): The neuron's membrane.
        axon (Axon): The neuron's axon.
        refractory_period (float): Refractory period after a spike (in cycles).
        refractory_time_remaining (float): Time left in refractory period.
        mode (str): Working mode of the neuron. Can be "default" or "train".
    """

    def __init__(self, dendrites, membrane, axon, refractory_period=1.0, mode="default"):
        """Initializes Core with dendrites, membrane, axon and optional parameters."""

        self.dendrites = dendrites
        self.membrane = membrane
        self.axon = axon
        self.refractory_period = refractory_period
        self.refractory_time_remaining = 0  
        self.mode = mode 

    def step(self):
        """Performs a single operation cycle on the neuron's core."""

        # Accumulate all the dendrite signals
        total_input = sum(dendrite.step(mode=self.mode) for dendrite in self.dendrites)   
        
        # Check if the neuron is in refractory period
        refractory = self.refractory_time_remaining > 0                     
        
        # Update the membrane potential
        self.membrane.step(total_input, refractory)                         
        
        if self.membrane.spike:  
            # If the neuron spiked, enter the refractory period
            self.refractory_time_remaining = self.refractory_period         
        else:
            # Decrease the time remaining in the refractory period
            self.refractory_time_remaining = max(0, self.refractory_time_remaining - 1)  
        
        # Provide the membrane potential and spike to the axon
        self.axon.step(self.membrane)
