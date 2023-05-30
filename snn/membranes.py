class Membrane: # Basic membrane model
    #def __init__(self, v_rest=-70.0, v_reset=-65.0, v_threshold=-50.0, leakage=0.1): those are more realistic values for a real neuron
    def __init__(self, rest=0.0, threshold=20.0, reset_ratio=0.05, leakage=0.5):
        self.rest = rest                    # Resting membrane potential
        self.threshold = threshold          # Threshold for spike generation
        self.reset_ratio = reset_ratio      # * Reset membrane potential after a spike where reset_ratio is range betweean rest & threshold (0=rest, 1=threshold)
        self.leakage = leakage              # * Rate of leakage of the membrane in percent! (0 = no leakage, 100 = instant leakage)
        self.v_m = self.rest                # Current membrane potential
        self.spike = False                  # Spike generated or not

    def reset(self): # Calculate the reset membrane potential after a spike
        return self.rest + (self.reset_ratio * (self.threshold - self.rest))

    def step(self, input_value, refractory):
        
        if refractory:                      # If in refractory period...
            self.v_m = self.reset()         # Reset the membrane potential
            self.spike = False              # No spike during refractory period
        else:
            self.v_m += input_value             # Update the membrane potential
            
            if self.v_m >= self.threshold:    # If the membrane potential has reached the threshold...
                self.v_m = self.reset()         # Reset the membrane potential
                self.spike = True               # Spike generated
            else:  # If not in the refractory period and the potential is below threshold...
                # leak the membrane potential by a percentage of the difference between the current membrane potential and the resting membrane potential
                # also raund the result to 3 decimal places
                self.v_m = round(self.v_m - ((self.v_m - self.rest) / 100) * self.leakage, 6) # TODO: more testing with different self.rest values
                self.spike = False             # No spike generated