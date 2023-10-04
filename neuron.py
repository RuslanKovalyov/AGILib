import random

class Neuron:
    def __init__(self):
        # Connection properties
        self.connections = [] # list of dicts [ {'neuron': neuron, 'weight': weight, 'ttl': ttl}, ...]
        # "ttl" is "time of transmitter leakage", or Time-Transmitter-Live (TTL) mechanism for synaptic weights, mimics the idea of short-term plasticity in biology.
        # impruve performance by changing list of dicts to numpy arrays
        self.min_max_weight = (-127, 127)
        self.min_max_ttl = (0, 255)

        self.input = 0 # current sum of inputs, and old inputs eith ttl > 0
        self.output_history = [] # append spike to this list every tick

        # Membrane properties
        self.rest = 0 # resting potential of v_membrane
        self.threshold = 100 # action potential threshold
        self.reset_ratio = {'val': 0.05, 'min': 0, 'max': 1 } # ratio of threshold to reset to. reset = rest + (reset_ratio * (threshold - rest)).
        self.v_m = 0 # current membrane potential
        self.leakage = {'val': 0.5, 'min': 0, 'max': 100} # leakage of membrane potential per tick in percent (%) of current v_m
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
        
    def set_properties(self, rest=0, threshold=100, reset_ratio=0.05, leakage=0.1, sensitivity=100, sensitivity_adjust_rate=-10, sensitivity_restore_rate=1, refractory_period=1):
        """
        Set properties of neuron with boundary checks.
        """

        self.rest = rest
        self.threshold = threshold
        
        # Boundary checks for reset_ratio
        if self.reset_ratio['min'] <= reset_ratio <= self.reset_ratio['max']:
            self.reset_ratio['val'] = reset_ratio
        else:
            self.reset_ratio['val'] = 0.05
            
        # Boundary checks for leakage
        if self.leakage['min'] <= leakage <= self.leakage['max']:
            self.leakage['val'] = leakage
        else:
            self.leakage['val'] = 0.1
        
        # Boundary checks for sensitivity
        if self.sensitivity['min'] <= sensitivity <= self.sensitivity['max']:
            self.sensitivity['val'] = sensitivity
        else:
            self.sensitivity['val'] = 100
        
        # Boundary checks for sensitivity_adjust_rate
        if self.sensitivity_adjust_rate['min'] <= sensitivity_adjust_rate <= self.sensitivity_adjust_rate['max']:
            self.sensitivity_adjust_rate['val'] = sensitivity_adjust_rate
        else:
            self.sensitivity_adjust_rate['val'] = -10
        
        # Boundary checks for sensitivity_restore_rate
        if self.sensitivity_restore_rate['min'] <= sensitivity_restore_rate <= self.sensitivity_restore_rate['max']:
            self.sensitivity_restore_rate['val'] = sensitivity_restore_rate
        else:
            self.sensitivity_restore_rate['val'] = 1
        
        # Boundary checks for refractory_period
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
    def connect(self, other_neuron, weight=None, ttl=0):
        """
        Connect to other neuron.
        """
        if weight is None:
            weight = random.uniform(-50, 50)  
        self.connections.append({'neuron': other_neuron, 'weight': weight, 'ttl': ttl})

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
                self.v_m = round(self.rest + (self.reset_ratio['val'] * (self.threshold - self.rest)), 4)
                self.refractory_period_counter = self.refractory_period['val']
                self.sensitivity['val'] += self.sensitivity_adjust_rate['val']

            else: # parameters restoration
                self.spike = False
                if self.v_m > active_potential:  # if v_m is bigger than active_potential because of refractory period, it must be decreased to threshold
                    self.v_m = active_potential
                self.v_m = round(self.v_m * (1 - self.leakage['val']/100), 4) # leakage of membrane potential per tick in percent (%) of current v_m
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
    def Backprop(self):
        """
        Backpropagation of error. Take care of TTL weights in propagation implementation.
        """
        # NOT IMPLEMENTED YET. TODO: Backpropagation logic
        pass

    def Hebbian(self):
        """
        Hebbian Learning. 
        """
        # NOT IMPLEMENTED YET. TODO: Hebbian Learning logic
        pass

    def Reinforcement(self):
        """
        Reinforcement Learning. 
        """
        # NOT IMPLEMENTED YET. TODO: Reinforcement Learning logic
        pass

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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="SET_PROPERTIES", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="CONNECT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="DISCONNECT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="SET_WEIGHT_AND_TTL", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
            
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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="GET_WEIGHT_AND_TTL", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="GET_OUTPUT_HISTORY", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
        
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
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="PROCESS_INPUT", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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
                assert neuron2.v_m == 9, f"Neuron2 membrane potential is incorrect. It should be 9."  # V_M = (v_m 0 + input 10) * (1 - leakage 10 / 100) = 9
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
                neuron2.set_properties(leakage=10)
                neuron2.v_m = 10
                neuron1.spike = False
                neuron2.forward()
                assert neuron2.v_m == 9, f"Neuron2 membrane potential is incorrect. It should be 9."  # V_M = (v_m 10 + input 0) * (1 - leakage 10 / 100) = 9

                # print(neuron2.input, 'input', ' | ', neuron2.v_m, 'v_m', ' | ', neuron2.threshold, 'threshold', ' | ', neuron2.spike, 'spike', ' | ', neuron2.sensitivity, 'sensitivity', ' | ', neuron2.refractory_period_counter, 'refractory_period_counter', ' | ', neuron2.refractory_period, 'refractory_period')

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="PROCESS_ACTIVATION", test_passed=True)
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="PROCESS_ACTIVATION", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))

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

# Run the test
def run_test():
    """
    Run test for Neuron class.
    """
    Neuron.Test.connect()
    Neuron.Test.set_properties_test()
    Neuron.Test.disconnect()
    Neuron.Test.set_weight_and_ttl_test()
    Neuron.Test.get_weight_and_ttl()
    Neuron.Test.get_output_history()
    Neuron.Test.process_input()
    Neuron.Test.process_activation()

if __name__ == "__main__":
    run_test()
