class Dendrite:
    """
    This class represents a dendrite in a neuron.
    A dendrite represents a branch of a neuron that receives signals from the synapse of an axon.

    Notes
    -----
    The dendrite is designed to take the job of post-synaptic signal processing and potentially will change self work mode, core settings, etc.

    Attributes:
        weight (float): The synaptic weight. Ranges from -50 to 50.
        max_weight (float): The maximum synaptic weight.
        min_weight (float): The minimum synaptic weight.
        input_mediator (str): Represents the neuromediator input. Functions like a flag.
        post_synapse (Synapse): Represents the dendritic synapse object. It will be set by core from axon's free synapses.
        last_input_state (str): Stores the last input state (input_mediator, weight).
        history_of_inputs (list): Stores the history of inputs for learning. It's a list of tuples (input_mediator, weight).
    """

    def __init__(self, weight=10):
        """
        Initializes the Dendrite with a given weight.

        Parameters
        ----------
        weight : float, optional
            The synaptic weight. By default, it is 10.
        """
        self.weight = weight
        self.max_weight = 50
        self.min_weight = -50
        self.input_mediator = ""
        self.post_synapse = None
        self.last_input_state = None
        self.history_of_inputs = []

    def connect(self, synapse):
        """
        Connects this dendrite to the given axonic synapse.

        Parameters
        ----------
        synapse : Synapse
            The synapse object to connect with.
        """
        self.post_synapse = synapse

    def set_weight(self, new_weight):
        """
        Sets the synaptic weight to the given value.

        Parameters
        ----------
        new_weight : float
            The new synaptic weight.
        """
        self.weight = new_weight

    def step(self, mode="default"):
        """
        Processes one step in the dendrite.

        Parameters
        ----------
        mode : str, optional
            The mode of operation. Default is "default".
        """
        if self.post_synapse:
            self.input_mediator = self.post_synapse.receive()

        if mode == "cycle-train":
            self.last_input_state = (self.input_mediator, self.weight)
        elif mode == "associative-train":
            self.history_of_inputs.append((self.input_mediator, self.weight))

        if self.input_mediator != "":
            self.input_mediator = ""
            return self.weight
        else:
            return 0
