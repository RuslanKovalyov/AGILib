import random

class Neuron:
    def __init__(self):
        # Connection properties
        self.connections = [] # list of dicts [ {'neuron': neuron, 'weight': weight, 'ttl': ttl, 's_stab': s_stab}, ...]
        # "ttl" is "time of transmitter leakage", or Time-Transmitter-Live (TTL) mechanism for synaptic weights, mimics the idea of short-term plasticity in biology.
        # "s_stab" connection (synapse) stability gives for frequently used channels greater resistance to learning. (protection of long experience) min=1, max=100
        # impruve performance by changing list of dicts to numpy arrays

        self.min_max_weight = (-127, 127)
        self.min_max_ttl = (0, 255)

        self.input = 0 # current sum of inputs, and old inputs eith ttl > 0
        self.output_history = [] # append spike to this list every tick
        self.rand_init = 50 # +/- random weight on initilization connection
        self.rand_learning = 10 # +/- random weight adding in cooperation mechanism

        # Membrane properties
        self.rest = 0 # resting potential of v_membrane
        self.threshold = 100 # action potential threshold
        self.reset_ratio = {'val': 0.05, 'min': 0, 'max': 1 } # ratio of threshold to reset to. reset = rest + (reset_ratio * (threshold - rest)).
        self.v_m = 0 # current membrane potential
        self.leakage = {'val': 0.1, 'min': 0, 'max': 100} # leakage of membrane potential per tick in percent (%) of current v_m
        self.spike = False
        self.sensitivity = {'val': 100, 'min': 0, 'max': 200} # sensitivity of neuron - total input moultiplier. Normally is must be 100 (100%)
        self.sensitivity_normal = 100 # normal sensitivity of neuron in percent (%)
        self.sensitivity_adjust_rate = {'val': -10, 'min': -100, 'max': 100} # sensitivity change per spike
        self.sensitivity_restore_rate = {'val': 1, 'min': 0, 'max': 100} # sensitivity restoration per tick in percent (%) of current sensitivity
        self.refractory_period = {'val': 1, 'min': 0, 'max': 1_000_000} # refractory period after spike in ticks (neuron is unresponsive)
        self.refractory_period_counter = 0 # current refractory period counter

        # Mode properties
        self.type = "Hidden" # | Hidden | Sensor | Motor |
        self.activation_function = "step" # | step | sigmoid | Hyperbolic Tangent (Tanh) | Rectified Linear Unit (ReLU) | etc. | - NOTE: work with sensitivity + threshold
        self.mode = "cycle-train" # | cycle-train | cycle | train |

        # Neurotransmitter properties
        self.neurotransmitter_type = 'simple-mediator' # NOT IMPLEMENTED YET | stimulant | inhibitor | etc. (work with weights, ttl, regeneration rate, depletion rate, sensitivity, etc.)
        # possible combinations such as dendritic negative weights and excitatory transmitter... this can work as enhanced suppression, etc. pay special attention to such combinations.
        self.neurotransmitter_level = 100 # current level, may have effect on output, firing pattern might change. Output is still binary and active but neurotransmitter not released in case of zero level
        self.neurotransmitter_regeneration_rate = {'val': 1, 'min': 0, 'max': self.neurotransmitter_level} # rate of neurotransmitter regeneration with no threshold per tick
        self.neurotransmitter_depletion_rate = {'val': 10, 'min': 0, 'max': self.neurotransmitter_level} # rate of neurotransmitter depletion per threshold

        # constants
        self.rounding = 4 # rounding of float numbers like v_m, weight, etc.
        
    def set_properties(self, rest=None, threshold=None, reset_ratio=None, leakage=None, sensitivity=None, sensitivity_adjust_rate=None, sensitivity_restore_rate=None, refractory_period=None):
        """
        Set properties of neuron with boundary checks.
        """
        if rest is not None:
            self.rest = rest
        if threshold is not None:
            self.threshold = threshold
        
        # Boundary checks for reset_ratio
        if reset_ratio is not None:
            if self.reset_ratio['min'] <= reset_ratio <= self.reset_ratio['max']:
                self.reset_ratio['val'] = reset_ratio
            
        # Boundary checks for leakage
        if leakage is not None:
            if self.leakage['min'] <= leakage <= self.leakage['max']:
                self.leakage['val'] = leakage
            else:
                self.leakage['val'] = 0.1
            
        # Boundary checks for sensitivity
        if sensitivity is not None:
            if self.sensitivity['min'] <= sensitivity <= self.sensitivity['max']:
                self.sensitivity['val'] = sensitivity
            else:
                self.sensitivity['val'] = 100
            
        # Boundary checks for sensitivity_adjust_rate
        if sensitivity_adjust_rate is not None:
            if self.sensitivity_adjust_rate['min'] <= sensitivity_adjust_rate <= self.sensitivity_adjust_rate['max']:
                self.sensitivity_adjust_rate['val'] = sensitivity_adjust_rate
            else:
                self.sensitivity_adjust_rate['val'] = -10
            
        # Boundary checks for sensitivity_restore_rate
        if sensitivity_restore_rate is not None:
            if self.sensitivity_restore_rate['min'] <= sensitivity_restore_rate <= self.sensitivity_restore_rate['max']:
                self.sensitivity_restore_rate['val'] = sensitivity_restore_rate
            else:
                self.sensitivity_restore_rate['val'] = 1
            
        # Boundary checks for refractory_period
        if refractory_period is not None:
            if self.refractory_period['min'] <= refractory_period <= self.refractory_period['max']:
                self.refractory_period['val'] = refractory_period
            else:
                self.refractory_period['val'] = 1

    ''' |||CONCEPT STAGE|||

    TODO: add initiallization by genetic algorithms for better aptimization of network structure and parameters.
    
    def step_left(self):
        """
        Half-forwarding. Left Step is Data cycle of all neurons in the network aimed at synchronization, a holistic exchange of data by all neurons before processing outputs.
        """
        # Accumulate input
        pass
    
    def step_right(self):
        """
        Half-forwarding. Right Step is output/core processing cycle of all neurons in the network aimed at synchronization, exchange of outputs by all neurons before next left step.
        """
        # Update action potential
        pass

    def phase_separated_step(self):
        """
        Think how to implement the idea of phase-separated processing, which is interesting as it might mimic rhythmic activity and synchronization observed in real neural systems.
        """
        pass
    '''

    # Connection methods - one to many connections (dendritic).
    def connect(self, other_neuron, weight=None, ttl=0, s_stab=1, ): # s_stab cant be 0! (division by zero error)
        """
        Connect to other neuron.
        """
        if weight is None:
            weight = random.uniform(-self.rand_init, self.rand_init)  
        self.connections.append({'neuron': other_neuron, 'weight': weight, 'ttl': ttl, 's_stab': s_stab})

        # TODO: dendrite growth analogy to emulate neuroplasticity of network.
    
    def disconnect(self, other_neuron):
        """
        Disconnect from other neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == other_neuron:
                self.connections.remove(connection)
                break
        
        # TODO: dendrite decay analogy to emulate neuroplasticity of network.

    def set_weight_and_ttl(self, target_neuron, weight=None, ttl=None):
        """
        Set weight and ttl of connection to target neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == target_neuron:
                if weight is not None:
                    connection['weight'] = weight
                if ttl is not None:
                    connection['ttl'] = ttl
                break

    def get_weight_and_ttl(self, other_neuron):
        """
        Get weight and ttl of connection to other neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == other_neuron:
                return connection['weight'], connection['ttl']
        return None, None
    
    def add_weight(self, target_neuron, value=None):
        """
        Add weight of connection to target neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == target_neuron:
                if value is not None:
                    new_weight = round(connection['weight'] + value, self.rounding)
                    connection['weight'] = min(self.min_max_weight[1], max(self.min_max_weight[0], new_weight)) # boundary checks
                break

    def set_s_stab(self, target_neuron, s_stab=None):
        """
        Set s_stab of connection to target neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == target_neuron:
                if s_stab is not None:
                    connection['s_stab'] = s_stab
                break
    
    def get_s_stab(self, other_neuron):
        """
        Get s_stab of connection to other neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == other_neuron:
                return connection['s_stab']
        return None

    def add_s_stab(self, target_neuron, positive=True):
        """
        Add s_stab of connection to target neuron in negative geometric progression.
        """
        for connection in self.connections:
            if connection['neuron'] == target_neuron:
                if positive:
                    s = round( connection['s_stab'] + (1/((connection['s_stab']+1)*connection['s_stab'])), self.rounding) # the higher the number, the slower it increases
                else:
                    s = round( connection['s_stab'] - (1/((connection['s_stab']+1)*connection['s_stab'])), self.rounding) # the higher the number, the slower it decreases
                connection['s_stab'] = min(100, max(1, s)) # boundary checks min=1, max=100
                break
    
    def get_output_history(self):
        """
        Get output history of neuron.
        """
        # return copy of values to prevent modification of original list
        return self.output_history.copy()

    def get_output(self):
        """
        Get output of neuron.
        """
        return self.spike
    
    def process_input(self):
        """
        Accumulate input from all connections.
        """
        self.input = 0
        for connection in self.connections:
            # ttl processing old inputs
            if connection['ttl'] > 0:
                # weight-to-timer ratio with input persistence
                self.input += connection['weight'] # TODO: tgradual decrease of weight with ttl and last input state
                connection['ttl'] -= 1
                pass # TODO: ttl processing now it's just a dummy placeholder! Must be Ratio of weight to timer and fade-out.
            elif connection['neuron'].get_output():
                self.input += connection['weight'] * connection['neuron'].get_output()

    def process_activation(self):
        """
        Activation function. Choose activation function by setted type.

        * Sigmoind: This is a classic activation function. It outputs values between 0 and 1 and can help introduce non-linearity to the network. This function can be used to simulate graded potentials in biological neurons.

        * Hyperbolic Tangent (Tanh): Similar to the sigmoid but outputs values between -1 and 1. This means neurons can have both excitatory and inhibitory outputs.

        * Exponential Linear Units (ELUs): It tries to make the mean activations closer to zero, which speeds up learning.

        * etc.
        """

        if self.activation_function == "step":
            self.v_m += self.input
            self.input = 0

            # Step function with active potential threshold and refractory period. TODO: more activation functions
            active_potential = self.threshold * self.sensitivity['val'] / 100

            if self.v_m >= active_potential and self.refractory_period_counter == 0:
                self.spike = True
                self.v_m = round(self.rest + (self.reset_ratio['val'] * (self.threshold - self.rest)), self.rounding)
                self.refractory_period_counter = self.refractory_period['val']
                self.sensitivity['val'] += self.sensitivity_adjust_rate['val']

            else: # parameters restoration
                self.spike = False
                if self.v_m > active_potential:  # if v_m is bigger than active_potential because of refractory period, it must be decreased to threshold
                    self.v_m = active_potential
                self.v_m = round(self.v_m * (1 - self.leakage['val']/100), self.rounding) # leakage of membrane potential per tick in percent (%) of current v_m
                self.refractory_period_counter -= 1 if self.refractory_period_counter > 0 else 0
                if self.sensitivity['val'] != self.sensitivity_normal:
                    if self.sensitivity['val'] > self.sensitivity_normal:
                        self.sensitivity['val'] -= self.sensitivity_restore_rate['val']
                    else:
                        self.sensitivity['val'] += self.sensitivity_restore_rate['val']
            self.sensitivity['val'] = min(self.sensitivity['max'], max(self.sensitivity['val'], self.sensitivity['min']))
        
        # TODO: other activation functions
        
        else:
            raise NotImplementedError("Activation function is not implemented yet. Choose another activation function.")

    def process_core(self):
        """
        Update action potential and other core parameters.
        """
        pass
        
    def forward(self):
        """
        forwarding data from left to right with full cycle of neurocalculation, sequential data collection and firing of each neuron, layer by layer, without left and right steps of data sinchronization.
        """

        # Dendrites processing - Accumulate input
        self.process_input()

        # Membrane processing - Update action potential
        self.process_activation()

        # Axon - processing
        self.output_history.append(self.spike)
        # Neurotransmitter processing : TODO: NOT IMPLEMENTED YET
    

    # Learning methods
    def reinforcement(self, error):
        
        """
        A unique version of reinforcement Learning.
        * Encapsulates the logic for correcting its own weights and does not participate in learning at the network level.

        _______________________________________________________
        Logic:
        if error
        check all connections to spik
        if self output is True  and connection's is True as increase weight with error
        if self output is False and connection's is True as increase weight with -error
        if error is positive(>0) increase the stability of all active connections (synapses).
        if error is negative(<0) decrease the stability of all active connections (synapses).
        change stability in reverse geometric progression ( s += (1/(s+1)*s) )
        """
 
        # one epoch learning without long associations of output history (one cycle only)
        if error != 0:
            if self.spike is False:
                # invert error if self output is False
                error = -error
            for connect in self.connections:
                if connect['neuron'].get_output() == True:
                    self.add_weight(connect['neuron'], error)
                    if error > 0:
                        self.add_s_stab(connect, positive=True)
                    else:
                        self.add_s_stab(connect, positive=False)
        
        # TODO: Assative learning with long associations of output history (several cycles)

    def cooperation(self):
        """
        Cooperation mechanism:
        In back3P, penalized neurons promote engagement among less-active neighbors, urging them to partake in the learning process. This mechanism distributes the error, fostering a cooperative environment.
        The aim is to optimize both individual neuron performance and overall network collaboration, tapping into the potential of underutilized neurons for a more holistic learning approach.
        """
        # NOT IMPLEMENTED YET. TODO: Cooperation mechanism logic

        # use random wheigts for not involved neurons in learning process to cooperate them.
        # use s_stab to increase involvement of neurons which long and stable working in other parts of network.
        # look optimisation opportunity by cutting off not involved neurons with high s_stab as they are already stable and not involved in local learning process.
        pass

    def recursive_prop(self):
        """
        Recursive propagation ensures error propagation taking into account the local requirements of specific neurons.
        * Cooperation Mechanism:
        In back3P, penalized neurons promote engagement among less-active neighbors, urging them to partake in the learning process. This mechanism distributes the error, fostering a cooperative environment.
        The aim is to optimize both individual neuron performance and overall network collaboration, tapping into the potential of underutilized neurons for a more holistic learning approach.
        """
        # NOT IMPLEMENTED YET. TODO: Recursive propagation logic
        pass
    
    def Backprop(self):
        """
        Backpropagation of error. 
        """
        # NOT IMPLEMENTED YET. TODO: Backpropagation logic
        
        # NOTE: Take care of TTL weights in propagation implementation.
        pass

    def Hebbian(self):
        """
        Highly extended and adapted Hebbian learning with new features. Name is used for associative purposes for code readability.
        """
        # NOT IMPLEMENTED YET. TODO: Hebbian Learning logic
        pass

    def back3P(self):# Back-Propagation of Polymorphic Plasticity
        """
        Back-Propagation of Polymorphic Plasticity (back3P):

        A biologically-inspired learning mechanism, `back3P` embodies mathematical paradigms that echo biological neural behaviors. 

        Key parallels include:
        - Propagation, which abstractly imitates the chemical communication between neurons for efficient information transmission.
        - The Hebbian principle, acting as an analogue to neurotransmitters that guide neural connection growth.
        - reinforcement learning, mirroring the hormonal reinforcement in biological systems, capturing the reward or penalty associated with different stimuli.

        * Cooperation Mechanism:
        In back3P, penalized neurons promote engagement among less-active neighbors, urging them to partake in the learning process. This mechanism distributes the error, fostering a cooperative environment.
        The aim is to optimize both individual neuron performance and overall network collaboration, tapping into the potential of underutilized neurons for a more holistic learning approach.
        Realisation of Cooperation mechanism is recursive error propagation, which ensures error propagation taking into account the local neurons behavior.
        
        * Plasticity as Neuroplasticity
        Unique to `back3P` is its flexibility in learning modalities:
        - Neurons can switch between various modes: continuous learning, operation without learning, concurrent operation and learning, and individual intensive training.
        - The network can undergo phase-based training, where specific parts or clusters of the network can be trained in isolation or in conjunction with others.
        - One of the hallmark features is the birth of new neurons during operational mode. These neurons, once added, undergo individualized training, showcasing raw neuroplasticity in action. This mimics the biological phenomenon of neurogenesis and integration of new neurons into established neural circuits.

        This methodology isn't just about adjusting weights; it’s about evolving the neural network's architecture and function over time, much like a biological brain. In essence, `back3P` blurs the lines between algorithmic learning methods and natural neural processes, presenting a fresh perspective on neural network learning and adaptability.
        """
        pass


    # Testing, debugging and visualization
    class Test:
        """
        Tests of neuron functionality and consistency.
        Since Python is used to prototype the class and concepts, internal tests are used to simplify it.
        The Neuron class will be rewritten and optimized in C++, use parallel processing, including clustering, etc.
        """
        def print_test_result(test_name=None, test_passed=None):
            """
            Print test result.
            """

            #colors for terminal output
            GREEN = '\033[92m'
            RED = '\033[91m'
            RESET = '\033[0m'
            if test_passed:
                print(f"\nTest {test_name} {GREEN}PASSED!{RESET}\n")
            else:
                print(f"\nTest {test_name} {RED}FAILED!{RESET}\n")
 
        def print_error_message(error_message=None):
            """
            Print error message.
            """

            #colors for terminal output
            YELLOW = '\033[93m'
            RESET = '\033[0m'
            print(f"error - {YELLOW}{error_message}{RESET}\n")

        @staticmethod
        def set_properties_test():
            """
            Test for the set_properties() method of Neuron class.
            """
            # Create a neuron
            neuron = Neuron()

            try:
                # Set some properties
                rest = 0.0
                threshold = 0.5
                reset_ratio = 0.1
                leakage = 0.2
                sensitivity = 0.3
                sensitivity_adjust_rate = 0.4
                sensitivity_restore_rate = 0.5
                refractory_period = 0.6
        
                properties = {
                    'rest': rest,
                    'threshold': threshold,
                    'reset_ratio': reset_ratio,
                    'leakage': leakage,
                    'sensitivity': sensitivity,
                    'sensitivity_adjust_rate': sensitivity_adjust_rate,
                    'sensitivity_restore_rate': sensitivity_restore_rate,
                    'refractory_period': refractory_period
                }

                neuron.set_properties(**properties)

                # Assert that properties are set correctly
                # Checking `rest` property
                assert neuron.rest == rest, "Rest property was not set correctly."

                # Checking `threshold` property
                assert neuron.threshold == threshold, "Threshold property was not set correctly."

                # Checking `reset_ratio` property
                assert getattr(neuron, 'reset_ratio', {}).get('val') == reset_ratio, "Reset ratio property was not set correctly."

                # Checking `leakage` property
                assert getattr(neuron, 'leakage', {}).get('val') == leakage, "Leakage property was not set correctly."

                # Checking `sensitivity` property
                assert getattr(neuron, 'sensitivity', {}).get('val') == sensitivity, "Sensitivity property was not set correctly."

                # Checking `sensitivity_adjust_rate` property
                assert getattr(neuron, 'sensitivity_adjust_rate', {}).get('val') == sensitivity_adjust_rate, "Sensitivity adjust rate property was not set correctly."

                # Checking `sensitivity_restore_rate` property
                assert getattr(neuron, 'sensitivity_restore_rate', {}).get('val') == sensitivity_restore_rate, "Sensitivity restore rate property was not set correctly."

                # Checking `refractory_period` property
                assert getattr(neuron, 'refractory_period', {}).get('val') == refractory_period, "Refractory period property was not set correctly."


                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="SET_PROPERTIES", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="SET_PROPERTIES", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def connect():
            """
            Test for the connect() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                weight = 0.75
                ttl = 5
                neuron2.connect(neuron1, weight=weight, ttl=ttl)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['weight'] == weight, "Connection weight is incorrect."
                        assert conn['ttl'] == ttl, "Connection TTL is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="CONNECT", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="CONNECT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def disconnect():
            """
            Test for the disconnect() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                weight = 0.75
                ttl = 5
                neuron2.connect(neuron1, weight=weight, ttl=ttl)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['weight'] == weight, "Connection weight is incorrect."
                        assert conn['ttl'] == ttl, "Connection TTL is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Disconnect neuron2 from neuron1
                neuron2.disconnect(neuron1)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        break
                    
                assert not connected, "Failed to disconnect neuron2 from neuron1."
                
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="DISCONNECT", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="DISCONNECT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def set_weight_and_ttl_test():
            """
            Test for the set_weight_and_ttl() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                weight = 0.75
                ttl = 5
                neuron2.connect(neuron1, weight=weight, ttl=ttl)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['weight'] == weight, "Connection weight is incorrect."
                        assert conn['ttl'] == ttl, "Connection TTL is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Set weight and ttl of connection
                new_weight = 0.5
                new_ttl = 10
                neuron2.set_weight_and_ttl(neuron1, weight=new_weight, ttl=new_ttl)

                # Check if weight and ttl are set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['weight'] == new_weight, "New connection weight is incorrect."
                        assert conn['ttl'] == new_ttl, " New connection TTL is incorrect."
                        break
                    else:
                        raise AssertionError("Failed to set weight and ttl of connection.")

                    
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="SET_WEIGHT_AND_TTL", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="SET_WEIGHT_AND_TTL", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def get_weight_and_ttl():
            """
            Test for the get_weight_and_ttl() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                weight = 0.75
                ttl = 5
                neuron2.connect(neuron1, weight=weight, ttl=ttl)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['weight'] == weight, "Connection weight is incorrect."
                        assert conn['ttl'] == ttl, "Connection TTL is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Get weight and ttl of connection
                connection_weight, connection_ttl = neuron2.get_weight_and_ttl(neuron1)

                # Check if weight and ttl are set correctly
                assert connection_weight == weight, "Connection weight is incorrect."
                assert connection_ttl == ttl, "Connection TTL is incorrect."
                    
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="GET_WEIGHT_AND_TTL", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="GET_WEIGHT_AND_TTL", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def set_s_stab():
            """
            Test for the set_s_stab() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                weight = 0.75
                ttl = 5
                neuron2.connect(neuron1, weight=weight, ttl=ttl, s_stab=1)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['weight'] == weight, "Connection weight is incorrect."
                        assert conn['ttl'] == ttl, "Connection TTL is incorrect."
                        assert conn['s_stab'] == 1, "Connection s_stab is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Set s_stab of connection
                s_stab = 0.5
                neuron2.set_s_stab(neuron1, s_stab=s_stab)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == s_stab, "New connection s_stab is incorrect."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")

                    
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="SET_S_STAB", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="SET_S_STAB", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed
        @staticmethod
        def get_s_stab():
            """
            Test for the get_s_stab() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:            
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                s_stab = 1
                neuron2.connect(neuron1, s_stab=s_stab)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['s_stab'] == 1, "Connection s_stab is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Get s_stab of connection
                connection_s_stab = neuron2.get_s_stab(neuron1)

                # Check if s_stab is set correctly
                assert connection_s_stab == 1, "Connection s_stab is incorrect."
                    
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="GET_S_STAB", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="GET_S_STAB", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def add_s_stab():
            """
            Test for the add_s_stab() method of Neuron class.
            """
            # Create two neurons
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:           
                # Initial state, there should be no connections
                assert len(neuron1.connections) == 0, "Initial state failed. Neuron1 has connections."
                assert len(neuron2.connections) == 0, "Initial state failed. Neuron2 has connections."
                
                # Connect neuron2 to neuron1 with specified weight and ttl
                s_stab = 1
                neuron2.connect(neuron1, s_stab=s_stab)
                
                # Check if neuron1 is connected to neuron2
                connected = False
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        connected = True
                        assert conn['s_stab'] == 1, "Connection s_stab is incorrect."
                        break
                    
                assert connected, "Failed to connect neuron2 to neuron1."
                
                # Add s_stab of connection
                neuron2.add_s_stab(neuron1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.5, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.5."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection
                neuron2.add_s_stab(neuron1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.7667, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.7."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection
                neuron2.add_s_stab(neuron1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.9713, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.9713."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection with 10 cycles
                for i in range(10):
                    neuron2.add_s_stab(neuron1)
                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 3.1131, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 3.1131."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # decrease s_stab of connection with 5 cycles
                for i in range(10):
                    neuron2.add_s_stab(neuron1, positive=False)
                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 2.0907, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 2.0907."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                #set value of s_stab as 2
                neuron2.set_s_stab(neuron1, s_stab=2)
                # decrease s_stab
                neuron2.add_s_stab(neuron1, positive=False)
                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.8333, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.8333."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                #set value of s_stab as 20
                neuron2.set_s_stab(neuron1, s_stab=20)
                # decrease s_stab
                neuron2.add_s_stab(neuron1, positive=False)
                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 19.9976, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 19.9976."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")

                    
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="ADD_S_STAB", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="ADD_S_STAB", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def get_output_history():
            """
            Test for the get_output_history() method of Neuron class.
            """
            # Create a neuron
            neuron = Neuron()

            try:
                # Initial state, there should be no output history
                assert len(neuron.output_history) == 0, "Initial state failed. Neuron has output history."

                # Forward the neuron
                neuron.forward()

                # Check if output history is updated
                assert len(neuron.output_history) == 1, "Output history was not updated."

                # Forward the neuron
                neuron.forward()

                # Check if output history is updated
                assert len(neuron.output_history) == 2, "Output history was not updated."

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="GET_OUTPUT_HISTORY", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="GET_OUTPUT_HISTORY", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def process_input():
            """
            Test for the process_input() method of Neuron class.
            """
            # Create a neuron
            neuron = Neuron()

            try:
                # Initial state, there should be no input
                assert neuron.input == 0, "Initial state failed. Neuron has input."

                # Connect neuron to itself
                neuron.connect(neuron)

                # Forward the neuron
                neuron.forward()

                # Check if input is updated
                assert neuron.input == 0, "Input Num-1 was updated."

                # Set weight of connection and simulate spike in previous neuron to get input from connection
                
                weight = 5
                neuron.set_weight_and_ttl(neuron, weight=weight)
                neuron.spike = True

                # Forward the neuron
                neuron.process_input()

                # Check if input is updated
                assert neuron.input == weight, "Input Num-2 was not updated."


                # Forward the neuron
                neuron.forward()
                # output in previous neuron is False, so input must be zero
                # Check if input is updated
                assert neuron.input == False, "Input Num-3 was not updated. Output in previous neuron is False, so input must be zero"

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="PROCESS_INPUT", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="PROCESS_INPUT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def process_activation():
            """
            Test for the process_activation() method of Neuron class.
            """
            # Create a neuron
            neuron1 = Neuron()
            neuron2 = Neuron()

            try:
                # Initial state, there should be no spike
                assert neuron1.spike == False, "Initial state failed. Neuron1 has spike."
                assert neuron2.spike == False, "Initial state failed. Neuron2 has spike."

                # Connect neuron2 to neuron1
                neuron2.connect(neuron1)

                # set weight of connection
                weight = 10
                threshold = 50

                neuron2.set_weight_and_ttl(neuron1, weight=weight)
                neuron2.set_properties(threshold=threshold, refractory_period=2, leakage=10)

                # simulate spike in neuron1
                neuron1.spike = True

                # process input
                neuron2.process_input()

                # Check if spike is updated
                assert neuron2.spike == False, f"Neuron2 has spike. It should not have spike whith weight = {weight} and threshold = {threshold}."

                # Forward the neuron
                neuron2.forward()
                
                # Check iinput, membrane addition and leakage
                assert neuron2.input == 0, f"Neuron2 input is incorrect. It should be 0."
                assert neuron2.v_m == 9, f"Neuron2 membrane potential {neuron2.v_m } is incorrect. It should be 9."  # V_M = (v_m 0 + input 10) * (1 - leakage 10 / 100) = 9
                weight = 41
                neuron2.set_weight_and_ttl(neuron1, weight=weight)
                neuron2.forward()
                # V_M = (9 + 41) > threshold as spike = True and v_m = 0 + (0.05 * (50 - 0)) = 2.5
                assert neuron2.spike == True, f"Neuron2 has no spike. It should have spike whith V_M = (9 + 41) and threshold = {threshold}."


                # check refractory period counter
                assert neuron2.refractory_period_counter == 2, f"Neuron2 refractory period counter is incorrect. It should be 2."
                neuron2.forward()
                assert neuron2.refractory_period_counter == 1, f"Neuron2 refractory period counter is incorrect. It should be 1."

                # check spike in time of refractory period
                neuron2.refractory_period_counter = 10
                neuron2.threshold = 10
                neuron2.forward()
                assert neuron2.spike == False, f"Neuron2 has spike. It should not have spike whith threshold = {threshold} and refractory_period_counter = 10."

                #check leakage in time of refractory period
                neuron2.set_properties(leakage=50)
                neuron2.v_m = 10
                neuron1.spike = False
                neuron2.forward()
                assert neuron2.v_m == 4.6, f"Neuron2 membrane potential {neuron2.v_m} incorrect. It should be 4.6."

                # print(neuron2.input, 'input', ' | ', neuron2.v_m, 'v_m', ' | ', neuron2.threshold, 'threshold', ' | ', neuron2.spike, 'spike', ' | ', neuron2.sensitivity, 'sensitivity', ' | ', neuron2.refractory_period_counter, 'refractory_period_counter', ' | ', neuron2.refractory_period, 'refractory_period')

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="PROCESS_ACTIVATION", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="PROCESS_ACTIVATION", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def reinforcement():
            # create 2 layers of neurons first layer has 2 neurons, second layer has 1 neuron (output neuron which will be reinforced)
            layer1 = [Neuron() for i in range(2)]
            layer2 = [Neuron() for i in range(1)]

            try:
                # connect neurons of second layer to neurons of first layer
                # connections = [] # list of dicts [ {'neuron': neuron, 'weight': weight, 'ttl': ttl, 's_stab': s_stab}, ...]
                for neuron in layer1:
                    for neuron2 in layer2:
                        neuron2.connect(neuron)
            
                # check if neurons of first layer are connected to neuron of second layer
                for neuron in layer2:
                    connected = True
                    for conn in neuron.connections:
                        if conn['neuron'] not in layer1:
                            connected = False
                            break
                    assert connected, f"Neuron of second layer is not connected to neuron of first layer."
                
                # set weight of connections for connections 1 and 2. Connection 1 has weight -50 and connection 2 has weight 50
                nuron1 = layer1[0]
                nuron2 = layer1[1]
                layer2[0].set_weight_and_ttl(nuron1, weight=-20)
                layer2[0].set_weight_and_ttl(nuron2, weight=50)

                # check if weight of connections is set correctly
                assert layer2[0].get_weight_and_ttl(nuron1)[0] == -20, f"Weight of connection 1 is incorrect. It should be -20."
                assert layer2[0].get_weight_and_ttl(nuron2)[0] == 50, f"Weight of connection 2 is incorrect. It should be 50."

                # set threshold of neurons of second layer
                layer2[0].set_properties(threshold=50)

                # check if threshold of neurons of second layer is set correctly
                assert layer2[0].threshold == 50, f"Threshold of neuron 1 is incorrect. It should be 50."

                # emulate spike in neurons of first layer
                nuron1.spike = True
                nuron2.spike = True

                # input processing
                for neuron in layer2:
                    neuron.process_input()
                
                # check input of neurons of second layer
                assert layer2[0].input == 30, f"Input of neuron of second layer is incorrect. It should be 30. (-20 + 50)"

                # check process_activation
                for neuron in layer2:
                    neuron.process_activation()
                    assert neuron.spike == False, f"Spike of neuron 1 is incorrect. It should be False."
                
                # check v_m of neurons of second layer to lekage 30 -> 29.97
                assert layer2[0].v_m == 29.97, f"V_M{layer2[0].v_m} of neuron is incorrect. It should be 30."

                # emulate spike in neurons of first layer
                nuron1.spike = True
                nuron2.spike = True

                # now neuron of second layer has should have spike after process_activation
                for neuron in layer2:
                    assert neuron.spike == False, f"Spike of neuron is incorrect. It should be False."
                    # check reset_ratio change to 0,07, after spike v_m = 3.5
                    neuron.set_properties(reset_ratio=0.07)
                    neuron.forward()
                    assert neuron.spike == True, f"Spike of neuron is incorrect. It should be True."
                    
                    # check spike, output and output history after forwarding
                    assert neuron.spike == True, f"Spike of neuron is incorrect. It should be False."
                    assert neuron.get_output() == True, f"Output of neuron is incorrect. It should be True."
                    assert neuron.output_history[-1] == True, f"Output history of neuron is incorrect. It should be True."
                    assert len(neuron.output_history) == 1, f"Output history of neuron is incorrect. It should be 1."


                    # check v_m of neurons of second layer  after spike v_m = 3.5
                    rest = round(neuron.rest + (neuron.reset_ratio['val'] * (neuron.threshold - neuron.rest)), neuron.rounding)
                    assert neuron.v_m == 3.5, f"V_M{neuron.v_m} of neuron is incorrect. It should be {rest}."

                    # reinforce checkinng
                    # provide error signal to neuron and check if weight of connection is changed
                    neuron.reinforcement(error=-5)
                    assert neuron.get_output() == True, f"Output of neuron is incorrect. It should be False."
                    assert neuron.get_weight_and_ttl(nuron1)[0] == -25, f"Weight of connection 1 is incorrect. It should be -25."
                    assert neuron.get_weight_and_ttl(nuron2)[0] == 45, f"Weight of connection 2 is incorrect. It should be 45."

                    # provide error signal to neuron and check if weight of connection is changed
                    neuron.reinforcement(error=15)
                    assert neuron.get_weight_and_ttl(nuron1)[0] == -10, f"Weight of connection 1 is incorrect. It should be -10."
                    assert neuron.get_weight_and_ttl(nuron2)[0] == 60, f"Weight of connection 2 is incorrect. It should be 60."

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="reinforcement", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="reinforcement", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        # Run all tests
        @staticmethod
        def run_all_tests():
            """
            Run tests for Neuron class.
            """
            all_passed = True
            if not Neuron.Test.connect(): all_passed = False
            if not Neuron.Test.set_properties_test(): all_passed = False
            if not Neuron.Test.disconnect(): all_passed = False
            if not Neuron.Test.set_weight_and_ttl_test(): all_passed = False
            if not Neuron.Test.get_weight_and_ttl(): all_passed = False
            if not Neuron.Test.set_s_stab(): all_passed = False
            if not Neuron.Test.get_s_stab(): all_passed = False
            if not Neuron.Test.add_s_stab(): all_passed = False
            if not Neuron.Test.get_output_history(): all_passed = False
            if not Neuron.Test.process_input(): all_passed = False
            if not Neuron.Test.process_activation(): all_passed = False
            if not Neuron.Test.reinforcement(): all_passed = False

            GREEN = '\033[92m'
            RED = '\033[91m'
            RESET = '\033[0m'
            if all_passed:
                print(f"{GREEN}---> All tests passed <---{RESET}")
            else:
                print(f"{RED}---> Some tests failed <---{RESET}")

    class Simulation:
        """
        Aimed at testing the neuron class in the context of the network, environment, other classes, features, efficiency measurements, etc.
        """
        pass

    class Benchmark:
        """
        Speed and efficiency benchmarking of neuron class, isolated methods of classes, in network dynamics, etc.
        pass
        """
        pass

    class Ploting:
        """
        Dinamic ploting of neuron and/or network activity. ex: Heatmaps of membrane potintials, signal routes frequency, spike patterns, overloaded sections of network (potential bottlenecks which can be optimized or expanded by adding new neurons), etc.
        """
        pass

if __name__ == "__main__":
    # Run the test
    Neuron.Test.run_all_tests()
