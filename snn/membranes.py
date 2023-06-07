class Membrane:
    """Basic membrane model for neuron.
    
    Attributes:
        rest (float): Resting membrane potential.
        threshold (float): Threshold for spike generation.
        reset_ratio (float): Used for calculating the reset membrane potential after a spike.
                             Range is between rest and threshold (0=rest, 1=threshold).
        leakage (float): Rate of leakage of the membrane in percent. (0 = no leakage, 100 = instant leakage)
        v_m (float): Current membrane potential.
        spike (bool): Spike generated or not.
    """
    
    def __init__(self, rest=0.0, threshold=20.0, reset_ratio=0.05, leakage=0.5):
        """Initializes Membrane with the given attributes."""
        self.rest = rest
        self.threshold = threshold
        self.reset_ratio = reset_ratio
        self.leakage = leakage
        self.v_m = self.rest
        self.spike = False

    def reset(self):
        """Calculates and returns the reset membrane potential after a spike."""
        return self.rest + (self.reset_ratio * (self.threshold - self.rest))

    def step(self, input_value, refractory):
        """Updates the membrane based on the provided input value (sum of dendrite signals) and refractory status.
        
        Args:
            input_value (float): The input value to the membrane.
            refractory (bool): The refractory status of the neuron.
        """
        if refractory:
            # If in refractory period, reset the membrane potential and set spike to False
            self.v_m = self.reset()
            self.spike = False
        else:
            # If not in refractory period, update the membrane potential
            self.v_m += input_value
            
            if self.v_m >= self.threshold:
                # If membrane potential has reached the threshold, reset the membrane potential and set spike to True
                self.v_m = self.reset()
                self.spike = True
            else:
                # If potential is below threshold, leak the membrane potential and set spike to False
                self.v_m = round(self.v_m - ((self.v_m - self.rest) / 100 * self.leakage), 6)
                self.spike = False
