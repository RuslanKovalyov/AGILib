class BaseNeuron:
    """
    The BaseNeuron serves as a protoneuron, providing foundational functionality and structure for more specialized neuron types.
    """
    def __init__(self):
        """
        Initialize basic properties of the neuron.
        """
        pass

    def forward(self, input):
        """
        Define the basic computation for the neuron.
        
        Args:
            input: The input data to the neuron.

        Returns: 
            The output of the neuron's computation.
        """
        pass


class LIFNeuron(BaseNeuron): # LIF = Leaky Integrate-and-Fire
    """
    The SpecialNeuron class represents a more specialized type of neuron, building upon the base functionality provided by BaseNeuron.
    """
    def __init__(self):
        """
        Initialize properties specific to this type of neuron, in addition to the basic properties initialized in BaseNeuron.
        """
        super().__init__()

    def forward(self, input):
        """
        Define the specialized computation for the neuron, possibly building on the base computation defined in BaseNeuron.
        
        Args:
            input: The input data to the neuron.

        Returns: 
            The output of the neuron's specialized computation.
        """
        pass