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

    def cumulative_lerning(self): # write error to history, make sum of all errors and make corrections of weights in sleep mode.
        pass

    def long_term_associative_lerning(self):
        # growth and development of connections (creation new, destruction, modification, etc.) between unobvious interconnected neurons with relatively long time intervals between their activation.
        pass

    def step(self):
        self.core.step()
    
