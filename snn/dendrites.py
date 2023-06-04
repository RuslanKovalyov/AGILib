class Dendrite:
    # A synapse will choisen from the list of axon's free synapses. if not enough synapses, new synapse will be created with chosen neurotransmitter type.
    # For now the input_mediator work just like a flag, but in future it will be used to spread neurotransmitters to core.

    def __init__(self, weight=10):
        self.weight = weight  # Synaptic weight
        self.max_weight = 50  # Maximum synaptic weight
        self.min_weight = -50  # Minimum synaptic weight
        
        self.input_mediator = ""  # Input neuromediator
        self.post_synapse = None  # Dendritic synapse object (will be set by core from axon's free synapses)
        
        self.history_of_inputs = []  # history (for learning) list of tuples (input_mediator, weight)

    def connect(self, synapse_object): # connect this dendrite to axonic synapse
        self.post_synapse = synapse_object

    def set_weight(self, new_weigth_value):
        self.weight = new_weigth_value

    def step(self, mode="default"):
        if self.post_synapse:
            self.input_mediator = self.post_synapse.receive()
        
        if mode == "cycle-train":
            self.history_of_inputs = [(self.input_mediator, self.weight)]
            # self.history_of_inputs.append((self.input_mediator, self.weight)) # add to history


        if self.input_mediator != "":
            # TODO: do some mediators logic here (like spreading dopamine to core, changing weights, etc.)

            self.input_mediator = ""
            return self.weight
        else:
            return 0