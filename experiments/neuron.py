import random
import pygame
import numpy as np
class Neuron:
    """ 0 layer is for input neurons (sensors only layer), have less core processing."""
    def __init__(self, layer_dept = None, signal_type = "binary", refactory_period=0):
        # Connection properties
        self.connections = [] # list of dicts [ {'neuron': neuron, 'weight': weight, 'ttl': ttl, 's_stab': s_stab}, ...]
        # "ttl" is "time of transmitter leakage", or Time-Transmitter-Live (TTL) mechanism for synaptic weights, mimics the idea of short-term plasticity in biology.
        # "s_stab" connection (synapse) stability gives for frequently used channels greater resistance to learning. (protection of long experience) min=1, max=100
        # impruve performance by changing list of dicts to numpy arrays

        self.min_max_weight = (-127, 127)
        self.min_max_ttl = (0, 255)
        self.min_max_input = (-100, 100) #  max total input of neuron
        self.min_max_v_m = (-100, 100) # stability of neuron membrane potential
        self.layer_dept = layer_dept # layer depth of neuron in network. Should be setted by network class. Used for cooperation mechanism  as caunter init, infinite recursion prevention.

        self.input = 0 # current sum of inputs, and old inputs eith ttl > 0
        self.output_history = [] # append spike to this list every tick
        self.rand_weight = 25 # +/- random weight on initilization connection
        self.rand_learning = 10 # +/- random weight adding in cooperation mechanism

        # Membrane properties
        self.rest = 0 # resting potential of v_membrane
        self.threshold = 25 # action potential threshold
        self.reset_ratio = {'val': 0.05, 'min': 0, 'max': 1 } # ratio of threshold to reset to. reset = rest + (reset_ratio * (threshold - rest)).
        self.v_m = 0 # current membrane potential
        self.leakage = {'val': 0.1, 'min': 0, 'max': 100} # leakage of membrane potential per tick in percent (%) of current v_m
        self.spike = False
        self.sensitivity = {'val': 100, 'min': 0, 'max': 200} # sensitivity of neuron - total input moultiplier. Normally is must be 100 (100%)
        self.sensitivity_normal = 100 # normal sensitivity of neuron in percent (%)
        self.sensitivity_adjust_rate = {'val': -0.001, 'min': -100, 'max': 100} # sensitivity change per spike
        self.sensitivity_restore_rate = {'val': 1, 'min': 0, 'max': 100} # sensitivity restoration per tick in percent (%) of current sensitivity
        self.refractory_period = {'val': refactory_period, 'min': 0, 'max': 1_000_000} # refractory period after spike in ticks (neuron is unresponsive)
        self.refractory_period_counter = 0 # current refractory period counter

        # Mode properties
        self.type = "Hidden" # | Hidden | Sensor | Motor |
        self.activation_function = "step" # | step | sigmoid | Hyperbolic Tangent (Tanh) | Rectified Linear Unit (ReLU) | etc. | - NOTE: work with sensitivity + threshold
        self.signal_type = signal_type # | binary | numeric | - NOTE: numeric output is not implemented yet and be used in various ways, for example, to control the speed of the robot's movement, etc.
        self.mode = "cycle-train" # | cycle-train | cycle | train |

        # Neurotransmitter properties
        self.neurotransmitter_type = 'simple-mediator' # NOT IMPLEMENTED YET | stimulant | inhibitor | etc. (work with weights, ttl, regeneration rate, depletion rate, sensitivity, etc.)
        # possible combinations such as dendritic negative weights and excitatory transmitter... this can work as enhanced suppression, etc. pay special attention to such combinations.
        self.neurotransmitter_level = 100 # current level, may have effect on output, firing pattern might change. Output is still binary and active but neurotransmitter not released in case of zero level
        self.neurotransmitter_regeneration_rate = {'val': 1, 'min': 0, 'max': self.neurotransmitter_level} # rate of neurotransmitter regeneration with no threshold per tick
        self.neurotransmitter_depletion_rate = {'val': 10, 'min': 0, 'max': self.neurotransmitter_level} # rate of neurotransmitter depletion per threshold

        # constants
        self.rounding = 4 # rounding of float numbers like v_m, weight, spike, etc.
        
    def set_properties(self, rest=None, threshold=None, reset_ratio=None, leakage=None, sensitivity=None, sensitivity_adjust_rate=None, sensitivity_restore_rate=None, sensitivity_normal=None, refractory_period=None, layer_dept=None, min_max_input=None):
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
        
        if sensitivity_normal is not None:
            self.sensitivity_normal = sensitivity_normal
        
        # Boundary checks for refractory_period
        if refractory_period is not None:
            if self.refractory_period['min'] <= refractory_period <= self.refractory_period['max']:
                self.refractory_period['val'] = refractory_period
            else:
                self.refractory_period['val'] = 1

        # set layer depth
        if layer_dept is not None:
            self.layer_dept = layer_dept
        
        if min_max_input is not None:
            self.min_max_input = min_max_input

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
        if weight == None:
            weight = round(random.uniform(-self.rand_weight, self.rand_weight), self.rounding)
        if s_stab == 0:
            s_stab = 1
            print('\033[93m',"s_stab can't be 0! (division by zero error), for now it's setted to 1.",'\033[0m')
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
                    connection['weight'] = round(weight, self.rounding)
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
                    connection['weight'] = round(min(self.min_max_weight[1], max(self.min_max_weight[0], new_weight)), self.rounding) # boundary checks
                break

    def set_s_stab(self, target_neuron, s_stab=None):
        """
        Set s_stab of connection to target neuron.
        """
        for connection in self.connections:
            if connection['neuron'] == target_neuron:
                if s_stab is not None and s_stab > 0:
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

    def add_s_stab(self, target_neuron, stab_error):
        """
        * Effect on involved connections (conn.spike=True) only.

        it work in cycle with progressive value ( stab_error used as cycle counter and can be negative (abs(stab_error))
        
        Add s_stab of connection to target neuron in negative geometric progression.
        """
        if stab_error != 0: # need in case of stab_error = 0.xxxx
            for _ in range(max(1, abs(round(stab_error)))):
                for connection in self.connections:
                    if connection['neuron'] == target_neuron:
                        if stab_error > 0:
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
        if self.layer_dept != 0: # headen layer
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
            #input bounded by min_max_input
            self.input = round(min(self.min_max_input[1], max(self.min_max_input[0], self.input)), self.rounding)

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
            # v_m boundery checks
            self.v_m = round(min(self.min_max_v_m[1], max(self.min_max_v_m[0], self.v_m)), self.rounding)

            # Step function with active potential threshold and refractory period. TODO: more activation functions
            active_potential = round(self.threshold * (self.sensitivity['val'] / 100), self.rounding)
            if self.v_m >= active_potential and self.refractory_period_counter == 0:
                if self.signal_type == "binary":
                    self.spike = True
                elif self.signal_type == "numeric":
                    norm_min = active_potential
                    norm_max = self.min_max_v_m[1]-active_potential
                    signal = self.v_m - active_potential
                    # map signal to range 0-100 by min-max normalization
                    normaliz_signal = (signal - norm_min) / (norm_max - norm_min + 1) * 100
                    self.spike = max(1, min(100, round(normaliz_signal, self.rounding)))
                if self.layer_dept != 0: # headen layer
                    self.v_m = round(self.rest + (self.reset_ratio['val'] * (self.threshold - self.rest)), self.rounding)
                    self.refractory_period_counter = self.refractory_period['val']
                    self.sensitivity['val'] += self.sensitivity_adjust_rate['val']

            else: # parameters restoration
                if self.signal_type == "binary":
                    self.spike = False
                elif self.signal_type == "numeric":
                    self.spike = 0
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
    def reinforcement(self, error, stabilization=True): # one neuron learning
        # work only with involved connections (conn.spike=True)
        """
        A unique version of reinforcement Learning.
        * Encapsulates the logic for correcting its own weights and does not participate in learning at the network level.

        _______________________________________________________
        Logic:
        if error
        check all spik connections

        if self output is True  and connection's is True then increase weight with error/stab
        if self output is False and connection's is True then increase weight with -error/stab

        if error is positive(>0) increase the stability of all active connections (synapses) including neagtive values.
        if error is negative(<0) decrease the stability of all active connections (synapses).
        change stability in reverse geometric progression ( s += (1/(s+1)*s) )

        """
 
        # one epoch learning without long associations of output history (one cycle only)
        if error != 0:
            stab = error
            # invert error if self output is False
            if self.spike is False:
                error = -error
            for connect in self.connections:
                # separation of connects as involv / without spike
                if connect["neuron"].get_output() != 0:
                    if not stabilization:
                        self.add_weight(connect["neuron"], error)
                    else:
                        self.add_weight(connect["neuron"], error/self.get_s_stab(connect["neuron"]))
                        self.add_s_stab(connect["neuron"], stab_error=stab)
        
        # TODO: Assative learning with long associations of output history (several cycles)
        # return error
    
    def cooperation(self, error):
        """
        Cooperation mechanism:
        In back3P, penalized ( and non-involvement ) neurons promote engagement among less-active neighbors, urging them to partake in the learning process. This mechanism distributes the error, fostering a cooperative environment.
        The aim is to optimize both individual neuron performance and overall network collaboration, tapping into the potential of underutilized neurons for a more holistic learning approach.
        
        Logic:
        Pass the error for not involved,in current pattern, neurons with congruent polarity of weights, to cooperate them.
        use s_stab to dencrease involvement of neurons which long and stable working in other patterns of network.
        dendrites with high s_stab are stable and less sensitive to learning other network patterns.
        but the neuron as a whole can have different stabilities in different dendrites. (simulation of synapce strength)

        * only negative error will activate cooperation mechanism for involving neurons with congruent polarity of weights * low s_stab.
        it will motivate other neurons to solving the problem but only if specific dendrites do not deal with more important pattern image.
        """  
        # 1. check legitimacy of cooperation and retransmission counter
        if error < 0 and self.get_output()==False: # legal cooperation only if error is negative and self spike=False
            if self.layer_dept > 0: # 0 is input layer
                for connect in self.connections:
                    if connect['neuron'].get_output() == False: # check if neuron was not involved in current learning pattern
                        if connect['weight'] >= 0: # weight adding/s_stab+(-error val/s_stab) to not involved connections
                            self.add_weight(connect['neuron'], (random.uniform(0, self.rand_learning)+(-error))/connect['s_stab'])

        else:
            # TODO: potencialy (check it) can prevent overfitting by decreasing excessive connections.
            # positive error and self spike=True will activate "DECOOPERATION"
            # potencialy can be used as network optimization by decreasing excessive connections. (analogous to firing people)
            pass

    def recursive_learning(self, error, retransmission_counter = None, cooperation=True, reinforcement=True): # NOTE: do NOT pass depth_counter from outside! only for self recursion call!
        """
        * recursion SHOULD BE CALLED FOR ALL NEURONS IN LAST LAYER OF NETWORK FROM OUTSIDE OF NEURON CLASS.

        * retransmission counter - is used to prevent infinite recursion in case of network error. On first call couter must be equal to neuron_depth number, then (in recurent call)will passed counter number, and not depth number of next neuron, for decrementing.
        
        Recursive reinforcement back-propagation ensures error propagation taking into account the local requirements of specific neurons.
        """
        if retransmission_counter is None:
            retransmission_counter = self.layer_dept
        if retransmission_counter > 0:
            # neuron learning
            if cooperation:
                self.cooperation(error)
            if reinforcement:
                self.reinforcement(error)
            # print('im here-------------------------------<<< counter is ',retransmission_counter)

            # recursion call. limited by self.layer_depth
            for connect in self.connections:
                connect = connect["neuron"]
                connect.recursive_learning(error, retransmission_counter-1)
                
    def noisy_network(self): # random weights adding
        """
        Random weights adding to all connections in the network.
        s_stab will be decrease noise effect.
        """
        pass
    
    def backprop(self, error):
        for connection in self.connections:
            connection['weight'] = max(min(round(connection['weight'] + error, self.rounding), self.min_max_weight[1]), self.min_max_weight[0])
            if connection['neuron'].layer_dept > 1: # 1 is connection to input layer '0'
                connection['neuron'].backprop(error/len(self.connections))

    def hebbian(self):
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

                # increment s_stab of connection
                neuron2.add_s_stab(neuron1, stab_error=1)
                assert neuron2.get_s_stab(neuron1) == 1.5, "Connection s_stab is incorrect."
                neuron2.add_s_stab(neuron1, stab_error=1)
                assert neuron2.get_s_stab(neuron1) == 1.7667, "Connection s_stab is incorrect."

                # decrement s_stab of connection
                neuron2.add_s_stab(neuron1, stab_error=-1)
                assert neuron2.get_s_stab(neuron1) == 1.5621, "Connection s_stab is incorrect."
                neuron2.add_s_stab(neuron1, stab_error=-1)
                assert neuron2.get_s_stab(neuron1) == 1.3122, "Connection s_stab is incorrect."
                neuron2.add_s_stab(neuron1, stab_error=-1)
                assert neuron2.get_s_stab(neuron1) == 1, "Connection s_stab is incorrect."
                # stab cant be less than 1
                neuron2.add_s_stab(neuron1, stab_error=-1)
                assert neuron2.get_s_stab(neuron1) == 1, "Connection s_stab is incorrect."
                


                # add s_stab of connection through error
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron2.connections[0]['neuron'].spike = True
                neuron2.spike = True
                # positive error
                neuron2.reinforcement(error=1)
                assert neuron2.get_s_stab(neuron1) == 1.5, "Connection s_stab is incorrect."
                # with not spike shuld still work
                neuron2.spike = False # reset spike
                neuron2.reinforcement(error=1)
                assert neuron2.get_s_stab(neuron1) == 1.7667, f"Connection s_stab {neuron2.get_s_stab(neuron1)} is incorrect."
                # max stab check (s_stab cant be more than 100)
                neuron2.set_s_stab(neuron1, s_stab=99)
                # cycle by error (50 times)
                neuron2.reinforcement(error=50)
                assert neuron2.get_s_stab(neuron1) == 99.005, "Connection s_stab is incorrect."
                neuron2.set_s_stab(neuron1, s_stab=100)
                neuron2.reinforcement(error=1)
                assert neuron2.get_s_stab(neuron1) == 100, "Connection s_stab is incorrect."

                # not involved connection shuld not change s_stab
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron2.connections[0]['neuron'].spike = False
                neuron2.spike = True
                # positive error
                neuron2.reinforcement(error=1)
                assert neuron2.get_s_stab(neuron1) == 1, "Connection s_stab is incorrect."
                # with not spike shuld still work
                neuron2.spike = False # reset spike
                neuron2.reinforcement(error=1)
                assert neuron2.get_s_stab(neuron1) == 1, "Connection s_stab is incorrect."
                # negative error
                neuron2.set_s_stab(neuron1, s_stab=10)
                neuron2.reinforcement(error=-1)
                assert neuron2.get_s_stab(neuron1) == 10, "Connection s_stab is incorrect."
                neuron2.reinforcement(error=-1)
                assert neuron2.get_s_stab(neuron1) == 10, "Connection s_stab is incorrect."
                # min stab check (s_stab cant be less than 1)
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron2.reinforcement(error=-1)
                assert neuron2.get_s_stab(neuron1) == 1, "Connection s_stab is incorrect."

                # check cycling with error < 1 ( 0.x ). min value of counter will be set to 1/-1 
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron1.spike = True
                neuron2.reinforcement(error=0.5)
                assert neuron2.get_s_stab(neuron1) == 1.5, f"Connection s_stab is incorrect. {neuron2.get_s_stab(neuron1)}"

                # error 1.4 in cycling same like 1
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron1.spike = True
                neuron2.reinforcement(error=1.4)
                assert neuron2.get_s_stab(neuron1) == 1.5, f"Connection s_stab is incorrect. {neuron2.get_s_stab(neuron1)}"

                # error 1.6 in cycling same like 2
                neuron2.set_s_stab(neuron1, s_stab=1)
                neuron1.spike = True
                neuron2.reinforcement(error=1.6)
                assert neuron2.get_s_stab(neuron1) == 1.7667, f"Connection s_stab is incorrect. {neuron2.get_s_stab(neuron1)}"


                    
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
                neuron2.add_s_stab(neuron1, stab_error=1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.5, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.5."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection
                neuron2.add_s_stab(neuron1, stab_error=1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.7667, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.7."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection
                neuron2.add_s_stab(neuron1, stab_error=1)

                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 1.9713, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 1.9713."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # Add s_stab of connection with 10 cycles
                for i in range(10):
                    neuron2.add_s_stab(neuron1, stab_error=1)
                # Check if s_stab is set correctly
                for conn in neuron2.connections:
                    if conn['neuron'] == neuron1:
                        assert conn['s_stab'] == 3.1131, f"New connection s_stab = {conn['s_stab']} is incorrect. It should be 3.1131."
                        break
                    else:
                        raise AssertionError("Failed to set s_stab of connection.")
                
                # decrease s_stab of connection with cycles
                for i in range(10):
                    neuron2.add_s_stab(neuron1, stab_error=-1)
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
                neuron2.add_s_stab(neuron1, stab_error=-1)
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
                neuron2.add_s_stab(neuron1, stab_error=-1)
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
        def reset_ratio():
            pass #TODO: have issues
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
                assert neuron2.v_m == 5, f"Neuron2 membrane potential {neuron2.v_m} incorrect. It should be 5."

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
        def reinforcement(): # NOTE - this test is not complete HAVE issues with reinforcement function call!!!! TODO
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
                neuron1 = layer1[0]
                neuron2 = layer1[1]
                layer2[0].set_weight_and_ttl(neuron1, weight=-20)
                layer2[0].set_weight_and_ttl(neuron2, weight=50)

                # check if weight of connections is set correctly
                assert layer2[0].get_weight_and_ttl(neuron1)[0] == -20, f"Weight of connection 1 is incorrect. It should be -20."
                assert layer2[0].get_weight_and_ttl(neuron2)[0] == 50, f"Weight of connection 2 is incorrect. It should be 50."

                # set threshold of neurons of second layer
                layer2[0].set_properties(threshold=50)

                # check if threshold of neurons of second layer is set correctly
                assert layer2[0].threshold == 50, f"Threshold of neuron 1 is incorrect. It should be 50."

                # emulate spike in neurons of first layer
                neuron1.spike = True
                neuron2.spike = True

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
                neuron1.spike = True
                neuron2.spike = True

                # now neuron of second layer has should have spike after process_activation
                for neuron in layer2:
                    assert neuron.spike == False, f"Spike of neuron is incorrect. It should be False."
                    # check reset_ratio change to 0,07, after spike v_m = 3.5
                    neuron.set_properties(reset_ratio=0.07)
                    neuron.forward()
                    if neuron.signal_type == 'binary':
                        assert neuron.spike == True, f"Spike {neuron.spike} of neuron is incorrect. It should be True."
                        assert neuron.spike == True, f"Spike {neuron.spike} of neuron is incorrect. It should be True."
                        assert neuron.output_history == [True], f"Output history {neuron.output_history} of neuron is incorrect. It should be [True]."
                    elif neuron.signal_type == 'numeric':
                        assert neuron.spike == 9.97, f"Spike {neuron.spike} of neuron is incorrect. It should be 9.97."
                        assert neuron.get_output() == 9.97, f"Output {neuron.get_output()} of neuron is incorrect. It should be 9.97."
                        assert neuron.output_history == [9.97], f"Output history {neuron.output_history} of neuron is incorrect. It should be [9,97,]."
                    assert len(neuron.output_history) == 1, f"Output history of neuron is incorrect. It should be 1."


                    # check v_m of neurons of second layer  after spike v_m = 3.5
                    rest = round(neuron.rest + (neuron.reset_ratio['val'] * (neuron.threshold - neuron.rest)), neuron.rounding)
                    assert neuron.v_m == 3.5, f"V_M{neuron.v_m} of neuron is incorrect. It should be {rest}."

                    # reinforce checkinng
                    # provide error signal to neuron and check if weight of connection is changed
                    neuron.reinforcement(error=-5)
                    assert neuron.get_weight_and_ttl(neuron1)[0] == -25, f"Weight of connection {neuron.get_weight_and_ttl(neuron1)[0]} is incorrect. It should be -25."
                    assert neuron.get_weight_and_ttl(neuron2)[0] == 45, f"Weight of connection {neuron.get_weight_and_ttl(neuron2)[0]} is incorrect. It should be 45."

                    # provide error signal to neuron and check if weight of connection is changed
                    neuron.reinforcement(error=15)
                    assert neuron.get_weight_and_ttl(neuron1)[0] == -10, f"Weight of connection 1 is incorrect. It should be -10."
                    assert neuron.get_weight_and_ttl(neuron2)[0] == 60, f"Weight of connection 2 is incorrect. It should be 60."
                
                    # check stabilizing weights of connections (not matter positive or negative weights), just spiked (involved) connections must be changed. if error is positive - stability of weights must be increased, if error is negative - decreased.
                    neuron.set_s_stab(neuron1, s_stab=1)
                    neuron.set_s_stab(neuron2, s_stab=1)
                    # emulate spike in neurons of first layer
                    neuron1.spike = True
                    neuron2.spike = True
                    neuron.add_s_stab(neuron1, stab_error=1)
                    neuron.add_s_stab(neuron2, stab_error=1)
                    assert neuron.get_s_stab(neuron1) == 1.5, f"Stability of weight {neuron.get_s_stab(neuron1)} of connection 1 is incorrect. It should be 1.5."
                    assert neuron.get_s_stab(neuron2) == 1.5, f"Stability of weight {neuron.get_s_stab(neuron2)}of connection 2 is incorrect. It should be 1.5."
                    neuron.add_s_stab(neuron1, stab_error=1)
                    neuron.add_s_stab(neuron2, stab_error=1)
                    assert neuron.get_s_stab(neuron1) == 1.7667, f"Stability of weight of connection 1 is incorrect. It should be 1.7667."
                    assert neuron.get_s_stab(neuron2) == 1.7667, f"Stability of weight of connection 2 is incorrect. It should be 1.7667."
                    # negative error
                    neuron.reinforcement(error=-1)
                    neuron.add_s_stab(neuron1, stab_error=-1)
                    neuron.add_s_stab(neuron2, stab_error=-1)
                    assert neuron.get_s_stab(neuron1) == 1.3122, f"Stability of weight of connection 1 is {neuron.get_s_stab(neuron1)} incorrect. It should be 1.3122 ."
                    assert neuron.get_s_stab(neuron2) == 1.3122, f"Stability of weight of connection 2 is {neuron.get_s_stab(neuron2)} incorrect. It should be 1.3122 ."
                    # change just one connection
                    neuron.add_s_stab(neuron1, stab_error=-1)
                    assert neuron.get_s_stab(neuron1) == 1, f"Stability of weight of connection 1 is {neuron.get_s_stab(neuron1)} incorrect. It should be 1.3122."
                    assert neuron.get_s_stab(neuron2) == 1.3122, f"Stability of weight of connection 2 is {neuron.get_s_stab(neuron2)} incorrect. It should be 1.3122."
                    # check it for min value (should be 1)
                    neuron.set_s_stab(neuron1, s_stab=1)
                    neuron.set_s_stab(neuron2, s_stab=1)
                    neuron.add_s_stab(neuron1, stab_error=-1)
                    neuron.add_s_stab(neuron2, stab_error=-1)
                    assert neuron.get_s_stab(neuron1) == 1, f"Stability of weight of connection 1 is {neuron.get_s_stab(neuron1)} incorrect. It should be 1."
                    neuron.reinforcement(error=1)
                    assert neuron.get_s_stab(neuron1) == 1.5, f"Stability of weight of connection 1 is {neuron.get_s_stab(neuron1)} incorrect. It should be 1.5."
                    neuron.reinforcement(error=-1)
                    assert neuron.get_s_stab(neuron1) == 1.2333, f"Stability of weight of connection 1 is {neuron.get_s_stab(neuron1)} incorrect. It should be 1.2333."


                    # stability check
                    layer1 = [Neuron() for i in range(3)]
                    layer2 = [Neuron() for i in range(1)]
                    neuron = layer2[0]
                    neuron.set_properties(layer_dept=1 ,threshold=5, refractory_period=0, leakage=0)
                    neuron.connect(layer1[0], weight=-10, s_stab=7)
                    neuron.connect(layer1[1], weight=0,  s_stab=7)
                    neuron.connect(layer1[2], weight=15, s_stab=7)
                    layer1[0].spike = False
                    layer1[1].spike = False
                    layer1[2].spike = True
                    neuron.forward()
                    error = -10 # error will be decreased 10 times (10 cycles)
                    neuron.reinforcement(error=error)
                    assert neuron.get_s_stab(layer1[0]) == 7, f"Stability of weight of connection 1 is {neuron.get_s_stab(layer1[0])} incorrect. It should be 7."
                    assert neuron.get_s_stab(layer1[1]) == 7, f"Stability of weight of connection 2 is {neuron.get_s_stab(layer1[1])} incorrect. It should be 7."
                    assert neuron.get_s_stab(layer1[2]) == 6.8174, f"Stability of weight of connection 3 is {neuron.get_s_stab(layer1[2])} incorrect. It should be 6.9821"

                    # check learning recursive_learning process with 2 layers, one hidden layer only (Layer2)
                    layer1 = [Neuron(layer_dept=0, signal_type='binary') for i in range(2)]
                    layer2 = [Neuron(layer_dept=1, signal_type='binary') for i in range(1)]
                    # set initial properties
                    for n in layer1:
                        # input layer
                        n.set_properties(threshold=0.001, refractory_period=0, leakage=100)
                    for n in layer2:
                        # hidden layer
                        n.set_properties(threshold=25, refractory_period=0, leakage=0)
                    # connect neurons of second layer to neurons of first layer
                    for neuron1 in layer1:
                        for neuron2 in layer2:
                            neuron2.connect(neuron1)
                    # set weight of connections for connections 1 and 2. Connection 1 has weight -20 and connection 2 has weight 20
                    neuron1 = layer1[0]
                    neuron2 = layer1[1]
                    neuronH = layer2[0]
                    neuronH.set_weight_and_ttl(neuron1, weight=25)
                    neuronH.set_weight_and_ttl(neuron2, weight=-20)
                    # emulate inputs
                    neuron1.input = 1
                    neuron2.input = 1
                    # forwarding L1
                    for neuron in layer1:
                        neuron.forward()
                    # forwarding L2
                    for neuron in layer2:
                        neuron.forward()
                    # print('v_m', neuronH.v_m)
                    # print('self.spike', neuronH.spike)
                    assert neuronH.spike == False, f"Spike of neuron is incorrect. It should be False."
                    # learning
                    neuronH.reinforcement(error=-10)
                    # forwarding L2
                    for neuron in layer2:
                        neuron.forward()
                    # print('v_m', neuronH.v_m)
                    # print('self.spike', neuronH.spike)
                    assert neuronH.spike == True, f"Spike of neuron is incorrect. It should be True."
                    

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="reinforcement", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="reinforcement", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed
        
        @staticmethod
        def cooperation():
            # crate 2 layers of neurons first layer has 2 neurons, second layer has 1 neuron (output neuron which will be cooperate neurons of first layer)
            layer1 = [Neuron() for i in range(2)]
            layer2 = [Neuron() for i in range(1)]

            try:
                # connect neurons, set parameters.
                neuron = layer2[0]
                neuron.set_properties(threshold=50, refractory_period=0, leakage=0)
                neuron.connect(layer1[0], weight=10, s_stab=7)
                neuron.connect(layer1[1], weight=40, s_stab=None)
                assert len(neuron.connections) == 2, f"Neuron has {len(neuron.connections)} connections. It should have 2 connections."
                layer1[0].spike = False
                layer1[1].spike = True
                neuron.set_properties(layer_dept=1)
                
                # forwarding
                neuron.forward()
                assert neuron.spike == neuron.get_output() == False, f"Spike of neuron is incorrect.  (False_S + w40)<trish50 It should be False."

                # check cooperation with  negative weight (not involved connection)
                neuron.set_weight_and_ttl(layer1[0], weight=-10)
                neuron.cooperation(error=-50)
                assert neuron.get_weight_and_ttl(layer1[0])[0] == -10, f"Weight of connection is incorrect. It should be -10."

                # check cooperation with  positive error (not involved connection)
                neuron.set_weight_and_ttl(layer1[0], weight=10)
                neuron.cooperation(error=50)
                assert neuron.get_weight_and_ttl(layer1[0])[0] == 10, f"Weight of connection is incorrect. It should be 10.   # check cooperation with  positive error (not involved connection)"


                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="cooperation", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="cooperation", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed
        
        @staticmethod
        def recursive_learning():
            try:
                # 1. recursive_learning test ( one hidden layer only )
                layer1 = [Neuron() for i in range(3)]
                layer2 = [Neuron() for i in range(1)]
                neuron = layer2[0]
                neuron.set_properties(layer_dept=1 ,threshold=50, refractory_period=0, leakage=0)
                neuron.connect(layer1[0], weight=-10, s_stab=1)
                neuron.connect(layer1[1], weight=1,  s_stab=1)
                neuron.connect(layer1[2], weight=15, s_stab=1)
                layer1[0].spike = False
                layer1[1].spike = False
                layer1[2].spike = False

                # legitimizing error and weight
                weight = 1
                error = -10
                layer1[1].spike = False
                neuron.connections[1]['weight'] = weight
                neuron.forward()
                neuron.recursive_learning(error=error)
                # print(f"recursive cooperation test - layer1[1].spike=({layer1[1].spike}) error({error}), weigh({neuron.connections[1]['weight'] }) after cooperation weight is'", neuron.connections[1]['weight'])
                assert neuron.connections[1]['weight'] > 10, f"Weight ({neuron.connections[1]['weight']}) of connection is incorrect. It should be > 10."

                # legitimizing weight as 0
                weight = 0
                error = -10
                layer1[1].spike = False
                neuron.connections[1]['weight'] = weight
                neuron.forward()
                neuron.recursive_learning(error=error)
                assert neuron.connections[1]['weight'] >= 10, f"Weight ({neuron.connections[1]['weight']}) of connection is incorrect. It should be >= 10."
                
                # unlegitimizing error
                weight = 1
                error = 10
                layer1[1].spike = False
                neuron.connections[1]['weight'] = weight
                neuron.forward()
                neuron.recursive_learning(error=error)
                assert neuron.connections[1]['weight'] == 1, f"Weight ({neuron.connections[1]['weight']}) of connection is incorrect. It should be 1."

                # unlegitimizing error as 0
                weight = 1
                error = 0
                layer1[1].spike = False
                neuron.connections[1]['weight'] = weight
                neuron.forward()
                neuron.recursive_learning(error=error)
                assert neuron.connections[1]['weight'] == 1, f"Weight ({neuron.connections[1]['weight']}) of connection is incorrect. It should be 1."

                # unlegitimizing weight
                weight = -1
                error = -10
                layer1[1].spike = False
                neuron.connections[1]['weight'] = weight
                neuron.forward()
                neuron.recursive_learning(error=error)
                assert neuron.connections[1]['weight'] == -1, f"Weight ({neuron.connections[1]['weight']}) of connection is incorrect. It should be -1."

                # 2. recursive_learning test with two hidden layers (recursion)

                # create neurons with seted layer_dept property
                layer0 = [Neuron(layer_dept=0) for i in range(2)]
                layer1 = [Neuron(layer_dept=1) for i in range(2)]
                layer2 = [Neuron(layer_dept=2) for i in range(2)]

                neuron1 = layer2[0]
                neuron2 = layer2[1]
                # full connections between layers 0, 1
                for n0 in layer0:
                    for n1 in layer1:
                        n1.connect(n0)
                # full connections between layers 1, 2
                for n1 in layer1:
                    for n2 in layer2:
                        n2.connect(n1)
                # connections of layer1
                assert layer1[0].connections[0]['neuron'] == layer0[0], f"connection problem (layer0 to layer1)"
                assert layer1[0].connections[1]['neuron'] == layer0[1], f"connection problem (layer0 to layer1)"
                assert layer1[1].connections[0]['neuron'] == layer0[0], f"connection problem (layer0 to layer1)"
                assert layer1[1].connections[1]['neuron'] == layer0[1], f"connection problem (layer0 to layer1)"
                # connections of layer2
                assert layer2[0].connections[0]['neuron'] == layer1[0], f"connection problem (layer1 to layer2)"
                assert layer2[0].connections[1]['neuron'] == layer1[1], f"connection problem (layer1 to layer2)"
                assert layer2[1].connections[0]['neuron'] == layer1[0], f"connection problem (layer1 to layer2)"
                assert layer2[1].connections[1]['neuron'] == layer1[1], f"connection problem (layer1 to layer2)"

                # set properties
                for n in layer0 + layer1 + layer2:
                    n.set_properties(threshold=50, refractory_period=0, leakage=0)
                    # set congruent weights to all connections
                    for conn in n.connections:
                        conn['weight'] = 1
                        conn['s_stab'] = 1
                
                # emulate forwardinng
                for n in layer0 + layer1 + layer2:
                    n.forward()
                
                # check if spike is False
                for n in layer0 + layer1 + layer2:
                    assert n.spike == False, f"Spike of neuron is incorrect. It should be False."
                    # print([conn['neuron'].spike for conn in n.connections])
                    # print([conn['neuron'].layer_dept for conn in n.connections])
                    # print([conn['weight'] for conn in n.connections])
                
                # learning (pass error to last layer recursive_learning function)
                for i in range(10):
                    # print('\nepoch', i)
                    for n in layer2:
                        n.recursive_learning(error=-10)
                    
                    # check if weights are changed in all layer 1 and 2
                    for n in layer1+layer2:
                        for conn in n.connections:
                            # print(conn['weight'])
                            assert conn['weight'] >1, f"Weight of connection ({conn['weight']}) is incorrect. It should be 1."
                

                # check recursive_learning process with 2 layers, one hidden layer only (Layer2)
                layer1 = [Neuron(layer_dept=0, signal_type='binary') for i in range(2)]
                layer2 = [Neuron(layer_dept=1, signal_type='binary') for i in range(1)]
                # set initial properties
                for n in layer1:
                    # input layer
                    n.set_properties(threshold=0.001, refractory_period=0, leakage=100)
                for n in layer2:
                    # hidden layer
                    n.set_properties(threshold=25, refractory_period=0, leakage=0)
                # connect neurons of second layer to neurons of first layer
                for neuron1 in layer1:
                    for neuron2 in layer2:
                        neuron2.connect(neuron1)
                # set weight of connections for connections 1 and 2. Connection 1 has weight -20 and connection 2 has weight 20
                neuron1 = layer1[0]
                neuron2 = layer1[1]
                neuronH = layer2[0]
                neuronH.set_weight_and_ttl(neuron1, weight=20)
                neuronH.set_weight_and_ttl(neuron2, weight=-5)
                # emulate inputs
                neuron1.input = 1
                neuron2.input = 1
                # forwarding L1
                for neuron in layer1:
                    neuron.forward()
                # forwarding L2
                for neuron in layer2:
                    neuron.forward()
                # print('v_m', neuronH.v_m)
                # print('self.spike', neuronH.spike)
                assert neuronH.spike == False, f"Spike of neuron is incorrect. It should be False."
                # learning
                neuronH.recursive_learning(error=-10)
                # forwarding L2
                for neuron in layer2:
                    neuron.forward()
                # print('v_m', neuronH.v_m)
                # print('self.spike', neuronH.spike)
                assert neuronH.spike == True, f"Spike of neuron is incorrect. It should be True."

                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="recursive_learning", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="recursive_learning", test_passed=False)
                Neuron.Test.print_error_message(error_message=str(e))
                passed = False
            return passed

        @staticmethod
        def simplenet():
            try:
                # create small net with 3 layers an 2 neurons in each layer
                layer1 = [Neuron(0) for i in range(2)]
                layer2 = [Neuron(1) for i in range(2)]
                layer3 = [Neuron(2) for i in range(2)]
                # connect neurons of second layer to neurons of first layer
                for neuron in layer1:
                    for neuron2 in layer2:
                        neuron2.connect(neuron)
                for neuron in layer2:
                    for neuron2 in layer3:
                        neuron2.connect(neuron)
                # set properties
                for neuron in layer1+layer2+layer3:
                    neuron.set_properties(threshold=50, refractory_period=0, leakage=0)

                # emulate inputs
                for n in layer1:
                    n.input = 1
                    n.threshold = 1
                # set weights
                for n in layer2:
                    for conn in n.connections:
                        conn['weight'] = 5
                    n.threshold = 1

                for n in layer3:
                    for conn in n.connections:
                        conn['weight'] = 0
                    n.threshold = 100
                
                # forwarding
                for n in layer1+layer2+layer3:
                    n.forward()

                for n in layer1:
                    assert n.get_output() == 1, f"Output layer1 {n.get_output()} of neuron is incorrect. It should be 1."

                for n in layer2:
                    if neuron.signal_type == 'binary':
                        assert n.get_output() == True, f"Output layer2 {n.get_output()} of neuron is incorrect. It should be True."
                    elif neuron.signal_type == 'numeric':
                        assert n.get_output() == 9, f"Output layer2 {n.get_output()} of neuron is incorrect. It should be 9."
                    
                for n in layer3:
                    assert n.get_output() == False, f"Output layer3 {n.get_output()}  of neuron is incorrect. It should be False."
                
                # If there are no assertion errors, the test passed
                Neuron.Test.print_test_result(test_name="simplenet", test_passed=True)
                passed = True
            except AssertionError as e:
                Neuron.Test.print_test_result(test_name="simplenet", test_passed=False)
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
            if not Neuron.Test.cooperation(): all_passed = False
            if not Neuron.Test.recursive_learning(): all_passed = False
            if not Neuron.Test.simplenet(): all_passed = False

            GREEN = '\033[92m'
            RED = '\033[91m'
            RESET = '\033[0m'
            if all_passed:
                print("                                      "                          f"(  )   (   (  (         ")
                print(f"{GREEN}      ______________                 {RESET} ",          f") (    (    )           ")
                print(f"{GREEN}     /--------------\\               {RESET} ",          f"(  )   (   )  )         ")
                print(f"{GREEN}    /----------------\\              {RESET} ",          f" _____________          ")
                print(f"{GREEN}   /------------------\\             {RESET} ",          f"|_____________|  _      ")
                print(f"{GREEN}  /--------------------\\            {RESET} ",          f"|             |/ _ \    ")
                print(f"{GREEN} /----------------------\\           {RESET} ",          f"|    Like a     | | |   ")
                print(f"{GREEN}\u250C------------------------\u2510 {RESET}          ", f"|     BOSS      | | |   ")
                print(f"{GREEN}|--> All tests passed <--|           {RESET}",           f"|             |\___/    ")
                print(f"{GREEN}\u2514------------------------\u2518 {RESET}          ", f" \___________/          ")
                      
                print("")

            else:
                print(f"{RED}---> Some tests failed <---{RESET}\n\n")

    class Simulation:
        """
        Aimed at testing the neuron class in the context of the network dinamyc, environment, cooperation, features, efficiency measurements, etc.
        """
        class NN:
            """
            Neural network which will be used as brain of snake entity.
            """
            def __init__(self, topology=[], connections_type ='full', signal_type='binary' ):
                """ Topology of network is a list of numbers of neurons in layers. First element of list is number of sensors, last element is number of output neurons.
                    [N-sensors, N-hidden1, N-hidden2, ..., N-output]
                """
                # list comprehension to create layers of neurons
                self.signal_type = signal_type
                self.layer = [[Neuron(layer_dept=depth, signal_type=signal_type) for i in range(layer_size)] for depth, layer_size in enumerate(topology)]
                
                # print topology as table
                print('\n\n')
                print(f'Topology of network: in-->{topology}<--out')
                print('-------------------')
                for i, layer in enumerate(self.layer):
                    print(f'Layer {i}:', f'N({len(layer)}) \t', 'n '*len(layer))
                
                # connect neurons
                if connections_type == 'full':
                    for i, layer in enumerate(self.layer):
                        if i == 0:
                            continue
                        for neuron in layer:
                            for neuronin_in_previous_layer in self.layer[i-1]:
                                neuron.connect(neuronin_in_previous_layer)


                #elif:
                else:
                    pass
                
                # set input properties
                for neuron in self.layer[0]:
                    neuron.set_properties(threshold=0.001, refractory_period=0, leakage=100)
                
                #set hidden properties
                for layer in self.layer[1:-1]:
                    for neuron in layer:
                        neuron.set_properties(threshold=25, refractory_period=0, leakage=0)
                        # set random weights for connections - 20 t0 20
                        for conn in neuron.connections:
                            conn['weight'] = random.randint(-20, 20)
                
            def input(self, input:list):
                """
                Set input for sensors.
                """
                # check if input is correct

                # set input for sensors
                for i, neuron in enumerate(self.layer[0]):
                    neuron.input = input[i]
                    neuron.spike = True
            
            def forward(self):
                """
                Forwarding of network.
                """
                for layer in self.layer:
                    for neuron in layer:
                        neuron.forward()
            
            def output(self):
                """
                Get output of network.
                """
                return [neuron.get_output() for neuron in self.layer[-1]]
            
            # TRAINING METHODS
            def backprop(self, error):
                for neuron in self.layer[-1]:
                    neuron.backprop(error=error)
                        
            def cycle_without_teacher(self, error, context, learning_method = 'recursive_learning'):
                if self.signal_type == 'binary':
                    for neuron in self.layer[-1]:
                        if learning_method == 'recursive_learning':
                            neuron.recursive_learning(error=error)

                        elif learning_method == 'reinforcement':
                            neuron.reinforcement(error=error)

                        elif learning_method == 'cooperation':
                            neuron.cooperation(error=error)
                        
                elif self.signal_type == 'numeric':
                    assert True, f"Numeric output is not implemented yet."
                    pass # TODO: generate error signal for numeric output
                
                # NOTE: (NO CONTEXT LEARNING) reset spikes and membrane potentials of all neurons every cycle
                if not context:
                    for layer in self.layer:
                        for neuron in layer:
                            neuron.v_m = 0
                
            def cycle_teacher(self, teacher:list, context, learning_method = 'recursive_learning', error_power = None):
                """
                Train network with teacher.
                were teacher is a list of correct answers for each output neuron in every cycle
                "context" used for associative ( historical context is off/on) learning were every cycle is in/dependent from previous one (clear spikes and membrane potentials of all neurons every cycle if False, else - not clear)
                
                *output of neuron can bee Boolean or Number ( depends on signal_type of neurons )

                """
                # check if teacher is correct
                assert len(teacher) == len(self.layer[-1]), f"Teacher is incorrect. It should be {len(self.layer[-1])} elements."
                # signal type of teacher and nn must be the same
                for s in teacher:
                    assert type(s) == bool if self.signal_type == 'binary' else type(s) == float, f"Teacher is incorrect. It should be {len(self.layer[-1])} elements."
                
                # generate errors signals for each output neuron by comparing teacher and output of neurons
                if error_power == None:
                    error_power = random.randint(0, 50)
                learning_error = 0
                if self.signal_type == 'binary':
                    for i, neuron in enumerate(self.layer[-1]):
                        # if teacher boolean value is same as output of neuron then error is positive number, else - negative, teacher is None (do't now) error is 0
                        if teacher[i] == neuron.get_output():
                            learning_error = error_power # positive error
                        else:
                            learning_error = -error_power # negative error
                        # train
                        if learning_method == 'recursive_learning':
                            neuron.recursive_learning(error=learning_error)

                        elif learning_method == 'reinforcement':
                            neuron.reinforcement(error=learning_error)

                        elif learning_method == 'cooperation':
                            neuron.cooperation(error=learning_error)
                        

                elif self.signal_type == 'numeric':
                    assert True, f"Numeric output is not implemented yet."
                    pass # TODO: generate error signal for numeric output
                
                # NOTE: (NO CONTEXT LEARNING) reset spikes and membrane potentials of all neurons every cycle
                if not context:
                    for layer in self.layer:
                        for neuron in layer:
                            neuron.v_m = 0
                
            def cumulative_learning(self):
                """
                Train network with teacher and long term memory associations (cumulative learning).
                """
                pass
            
            # Testing methods
            
            @staticmethod
            def no_context_teacher_learning():
                brain = Neuron.Simulation.NN(topology=[4,16 ,4])
                # set leakages of hidden layer to 100
                for layer in brain.layer[1:-1]:
                    for neuron in layer:
                            neuron.set_properties(leakage=100)
                            neuron.set_properties(reset_ratio=0)

                # brain.layer[1][0].connections[0]['weight'] = 0
                # brain.layer[2][0].connections[0]['weight'] = 0
                for i in range(50):
                    
                    for epoch in range(i):
                        print('\n\nepoch', epoch+1)
                        brain.input([True, True, False, False])
                        print('v_m', brain.layer[1][0].v_m)
                        print('weight', brain.layer[1][0].connections[0]['weight'])
                        brain.forward()
                        print('forwarding')
                        print('spike', brain.layer[1][0].spike)
                        print('v_m', brain.layer[1][0].v_m)
                        print('output', brain.output())
                        print('stab', brain.layer[1][0].get_s_stab(brain.layer[0][0]))
                        # learning, etalon output [True, False, False, True]
                        brain.cycle_teacher([True, True, True, True], context=False, error_power=7, learning_method='recursive_learning')

                    for epoch in range(i):
                        print('\n\nepoch', epoch+1)
                        brain.input([False, True, True, False])
                        print('v_m', brain.layer[1][0].v_m)
                        print('weight', brain.layer[1][0].connections[0]['weight'])
                        brain.forward()
                        print('forwarding')
                        print('spike', brain.layer[1][0].spike)
                        print('v_m', brain.layer[1][0].v_m)
                        print('output', brain.output())
                        print('stab', brain.layer[1][0].get_s_stab(brain.layer[0][0]))
                        # learning, etalon output [True, False, False, True]
                        brain.cycle_teacher([False, True, False, True], context=False, error_power=7, learning_method='recursive_learning')

                    for epoch in range(i):
                        print('\n\nepoch', epoch+1)
                        brain.input([False, False, True, True])
                        print('v_m', brain.layer[1][0].v_m)
                        print('weight', brain.layer[1][0].connections[0]['weight'])
                        brain.forward()
                        print('forwarding')
                        print('spike', brain.layer[1][0].spike)
                        print('v_m', brain.layer[1][0].v_m)
                        print('output', brain.output())
                        print('stab', brain.layer[1][0].get_s_stab(brain.layer[0][0]))
                        # learning, etalon output [True, False, False, True]
                        brain.cycle_teacher([False, False, False, False], context=False, error_power=7, learning_method='recursive_learning')


                print("\n\n---------------------------------------------------------")
                for _ in range(2):
                    print("---------------------------------------------------------")
                    brain.input([True, True, False, False])
                    brain.forward()
                    print('output', brain.output())
                    # reset all v_m in nn
                    for layer in brain.layer:
                        for neuron in layer:
                            neuron.v_m = 0

                    print("---------------------------------------------------------")
                    brain.input([False, True, True, False])
                    brain.forward()
                    print('output', brain.output())
                    for layer in brain.layer:
                        for neuron in layer:
                            neuron.v_m = 0

                    print("---------------------------------------------------------")
                    brain.input([False, False, True, True,])
                    brain.forward()
                    print('output', brain.output())
                    for layer in brain.layer:
                        for neuron in layer:
                            neuron.v_m = 0
         
        class SnakeEntity:
            """
            Emulates snake entity in primitive environment of classic snake game.
            Realization through incapsulation of 1. brain(AI) - NN class, 2. snake game, and 3th is connector between them.
            """
            class ConnectorSnackSnn:    
                def __init__(self, width, height):
                    # Set the dimensions of the field
                    self.brine = Neuron.Simulation.NN(topology=[77,8, 4])

                    # set leakages to 100 and reset ratio to 0
                    for layer in self.brine.layer[1:-1]:
                        for neuron in layer:
                            neuron.set_properties(leakage=100, reset_ratio=0)

                    self.width = width
                    self.height = height
                    # data to/from the neural network
                    self.go_to = "UP" #STOP
                    self.game_state = {
                        "field": [[0 for _ in range(width)] for _ in range(height)], 
                        "direction": None,
                        "food_direction": None,
                        "food_distance": {"x": None, "y": None}
                    }

                # Entity methods

                def ai_step(self):
                    """
                    Colled by the entity to compute the next move
                    """
                    self.brine.forward()
                    data = self.brine.output()
                    # print(data)
                    if data == [True,0,0,0]:
                        self.go_to = "Up"
                    elif data == [0,True,0,0]:
                        self.go_to = "Right"
                    elif data == [0,0,True,0]:
                        self.go_to = "Down"
                    elif data == [0,0,0,True]:
                        self.go_to = "Left"
                    
                    elif data == [True,True,False,False]:
                        self.go_to = "UpRight"
                    elif data == [False,True,True,False]:
                        self.go_to = "DownRight"
                    elif data == [False,False,True,True]:
                        self.go_to = "DownLeft"
                    elif data == [True,False,False,True]:
                        self.go_to = "UpLeft"
                        
                def train(self, error):
                    """
                    Colled by the entity to train the neural network
                    """
                    # self.brine.cycle_without_teacher(error=error, context=False, learning_method='recursive_learning')
                    self.brine.cycle_without_teacher(error=error, context=False, learning_method='recursive_learning')


                    # print meedle value of all s_stab of last layer

                    meedle_value1 = 0
                    for neuron in self.brine.layer[-2]:
                        for conn in neuron.connections:
                            meedle_value1 += conn['s_stab']

                    meedle_value2 = 0
                    for neuron in self.brine.layer[-1]:
                        for conn in neuron.connections:
                            meedle_value2 += conn['s_stab']

                    print('meedle stab value1', round(meedle_value1/len(self.brine.layer[-3]),2), '\t-----', 'meedle stab value2', round(meedle_value2/len(self.brine.layer[-2]),2))

                def get_move_direction(self):
                    """
                    Colled by the entity to get the direction to move to
                    """
                    if self.go_to != None:
                        go_to = self.go_to
                        self.go_to = None
                        return go_to
                    else:
                        return None
                
                def set_game_state(self, field, direction, food_direction, food_distance):
                    """
                    Colled by the entity to set the game state, which is then used by the neural network
                    """
                    self.game_state["field"] = field
                    self.game_state["direction"] = direction
                    self.game_state["food_direction"] = food_direction
                    self.game_state["food_distance"] = food_distance
                
                    # transfer data to snn
                    data = []

                    # food direction
                    if self.game_state["food_direction"] == "Up":
                        data = [1, 0, 0, 0]
                    elif self.game_state["food_direction"] == "Right":
                        data = [0, 1, 0, 0]
                    elif self.game_state["food_direction"] == "Down":
                        data = [0, 0, 1, 0]
                    elif self.game_state["food_direction"] == "Left":
                        data = [0, 0, 0, 1]
                        
                    elif self.game_state["food_direction"] == "UpRight":
                        data = [1, 1, 0, 0]
                    elif self.game_state["food_direction"] == "DownRight":
                        data = [0, 1, 1, 0]
                    elif self.game_state["food_direction"] == "DownLeft":
                        data = [0, 0, 1, 1]
                    elif self.game_state["food_direction"] == "UpLeft":
                        data = [1, 0, 0, 1]
                    else:
                        data = [0, 0, 0, 0] # STOP
                    
                    # food distance sum (x+y)
                    distance = self.game_state["food_distance"]["x"] + self.game_state["food_distance"]["y"]
                    if distance > (self.width + self.height) * 3/4:
                        data += [0, 0, 0, 1]
                    elif distance > (self.width + self.height) * 1/2:
                        data += [0, 0, 1, 0]
                    elif distance > (self.width + self.height) * 1/4:
                        data += [0, 1, 0, 0]
                    else:
                        data += [1, 0, 0, 0]


                    # direction
                    if self.game_state["direction"] == "Up":
                        data += [1, 0, 0, 0]
                    elif self.game_state["direction"] == "Right":
                        data += [0, 1, 0, 0]
                    elif self.game_state["direction"] == "Down":
                        data += [0, 0, 1, 0]
                    elif self.game_state["direction"] == "Left":
                        data += [0, 0, 0, 1]
                    else:
                        data += [0, 0, 0, 0] # STOP
                    
                    # head in field
                    for row in self.game_state["field"]:
                        for cell in row:
                            if cell == '3':
                                data.append(1)
                            else:
                                data.append(0)
                    
                    # body in field
                    for row in self.game_state["field"]:
                        for cell in row:
                            if cell == '2':
                                data.append(1)
                            else:
                                data.append(0)
                    
                    # if next step collides with boundary
                    boundary_is_next = 0
                    if self.game_state["direction"] == "Up":
                        # check if head ('3') is in top row
                        if '3' in self.game_state["field"][0]:
                            print("UP collision")
                            boundary_is_next = 1
                    elif self.game_state["direction"] == "Right":
                        # check if head ('3') is in right column
                        if '3' in [row[-1] for row in self.game_state["field"]]:
                            print("RIGHT collision")
                            boundary_is_next = 1
                    elif self.game_state["direction"] == "Down":
                        # check if head ('3') is in bottom row
                        if '3' in self.game_state["field"][-1]:
                            print("DOWN collision")
                            boundary_is_next = 1
                    elif self.game_state["direction"] == "Left":
                        # check if head ('3') is in left column
                        if '3' in [row[0] for row in self.game_state["field"]]:
                            print("LEFT collision")
                            boundary_is_next = 1
                            
                    data.append(boundary_is_next)                            
                    self.brine.input(data)
                    
                # Neural network methods
                
                def set_move_direction(self, go_to):
                    """
                    Colled by the neural network to set the direction to move to
                    """
                    self.go_to = go_to

                def get_game_state(self):
                    """
                    Colled by the neural network to get the game state, which is then used to compute the next move
                    """
                    return self.game_state
                
            def __init__(self):
                """
                Snake and environment.
                """
                # Set the dimensions of the game window
                self.width = 160
                self.height = 160

                self.data_width = 700
                self.data_height = 500
                # Define the colors to be used:
                self.BLACK = (0, 0, 0)
                self.WHITE = (255, 255, 255)
                self.GREEN = (0, 255, 0)
                self.RED   = (255, 0, 0)

                # connect the snake to the SNN
                self.connector = self.ConnectorSnackSnn(width=self.width, height=self.height)

                # Initialize Pygame:
                pygame.init()

                # Create the game window
                self.window = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Snake Game")

                # Create the data window
                self.data_window = pygame.display.set_mode((self.data_width, self.data_height))
                pygame.display.set_caption("Data Window")

                # Set up the game variables:
                self.snake_block_size = 10
                self.snake_speed = 15

                self.x_change = 0
                self.y_change = 0

                self.clock = pygame.time.Clock()

                self.font_style = pygame.font.SysFont(None, 30)
                self.score_font = pygame.font.SysFont(None, 50)
                self.game_data = pygame.font.SysFont(None, 20)
                self.game_distance = pygame.font.SysFont(None, 20)
                self.game_map = pygame.font.SysFont(None, 10)

                #print meadl score of last 30 games
                self.last_score = 0
                self.score = 0
                self.record = 0
                self.game_count = 0

            # Define functions for displaying the snake and the score:
            def our_snake(self, snake_block_size, snake_list):
                for x in snake_list:
                    pygame.draw.rect(self.window, self.GREEN, [x[0], x[1], snake_block_size, self.snake_block_size])

            def your_score(self, points):
                # value = score_font.render("Score: " + str(points), True, WHITE)
                # window.blit(value, [0, 0+height])
                self.score += points
                self.game_count += 1
                if points > self.record:
                        self.record = points
                if self.game_count == 50:
                    self.score = round(self.score/50)
                    self.last_score = self.score
                    self.score = 0
                    self.game_count = 0
                value = self.score_font.render("Middle Score by last 50 games: " + str(self.last_score), True, self.WHITE)
                self.window.blit(value, [0, 0+self.height])
                # show record
                value = self.score_font.render("Record: " + str(self.record), True, self.WHITE)
                self.window.blit(value, [0, 30+self.height])
                # show actual score
                value = self.score_font.render("Actual: " + str(points), True, self.WHITE)
                self.window.blit(value, [0, 60+self.height])

            def render_data(self, game_state):
                self.data_window.blit(self.game_data.render("direction:            "  + str(game_state["direction"     ]), True, self.WHITE),[120, 200+self.height])
                self.data_window.blit(self.game_data.render("food_direction:   "      + str(game_state["food_direction"]), True, self.WHITE),[120, 225+self.height])
                
            def render_distance(self, game_state):
                self.data_window.blit(self.game_distance.render("food_distance:    "  + str(game_state["food_distance" ]), True, self.WHITE),[120, 250+self.height])
                
            def render_map(self, game_state):
                field = game_state["field"]
                for i, row in enumerate(field):
                    row_str = ''.join(str(cell) for cell in row)
                    self.data_window.blit(self.game_map.render(row_str, True, self.WHITE), [0, self.height+70 + 10 * i])

            # Implement the game loop:
            def game_loop(self):
                game_over = False
                game_end = False

                # Initial position of the snake
                x1 = self.width / 2
                y1 = self.height / 2

                # Change in position
                x1_change = 0
                y1_change = 0

                # Snake body
                snake_list = []
                length_of_snake = 1

                # Generate initial food position
                foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
                foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0

                # Initialize snake_head
                snake_head = []

                points = 0
                distance_to_food = abs(foodx - x1) + abs(foody - y1)
                while not game_over:
                    while game_end:

                        # Reset game variables
                        game_over = False
                        game_end = False

                        # Initial position of the snake
                        x1 = self.width / 2
                        y1 = self.height / 2

                        # Change in position
                        x1_change = 0
                        y1_change = 0

                        # Snake body
                        snake_list = []
                        length_of_snake = 1
                        points = 0

                        # Generate initial food position
                        foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
                        foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0

                        # Initialize snake_head
                        snake_head = []

                    # Handle connector input events
                    self.connector.ai_step()
                    go_to = self.connector.get_move_direction()
                    if go_to:
                        if go_to == 'Left':
                            x1_change = -self.snake_block_size
                            y1_change = 0
                        elif go_to == 'Right':
                            x1_change = self.snake_block_size
                            y1_change = 0
                        elif go_to == 'Up':
                            y1_change = -self.snake_block_size
                            x1_change = 0
                        elif go_to == 'Down':
                            y1_change = self.snake_block_size
                            x1_change = 0
                        
                        elif go_to == 'UpRight':
                            y1_change = -self.snake_block_size
                            x1_change = self.snake_block_size
                        elif go_to == 'DownRight':
                            y1_change = self.snake_block_size
                            x1_change = self.snake_block_size
                        elif go_to == 'DownLeft':
                            y1_change = self.snake_block_size
                            x1_change = -self.snake_block_size
                        elif go_to == 'UpLeft':
                            y1_change = -self.snake_block_size
                            x1_change = -self.snake_block_size
                            
                    else:
                        # Handle keypresses
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                game_over = True
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_LEFT:
                                    x1_change = -self.snake_block_size
                                    y1_change = 0
                                elif event.key == pygame.K_RIGHT:
                                    x1_change = self.snake_block_size
                                    y1_change = 0
                                elif event.key == pygame.K_UP:
                                    y1_change = -self.snake_block_size
                                    x1_change = 0
                                elif event.key == pygame.K_DOWN:
                                    y1_change = self.snake_block_size
                                    x1_change = 0

                    # Check if the snake hits the boundary
                    if x1 >= self.width or x1 < 0 or y1 >= self.height or y1 < 0:
                        self.connector.train(error=-0.01)
                        game_end = True
                    # Update the snake's position
                    x1 += x1_change
                    y1 += y1_change

                    self.window.fill(self.BLACK)

                    # Draw border for game area
                    pygame.draw.rect(self.window, self.WHITE, pygame.Rect(0, 0, self.width, self.height), 2) # 2 is border thickness
                    
                    pygame.draw.rect(self.window, self.RED, [foodx, foody, self.snake_block_size, self.snake_block_size])
                    snake_head = []
                    snake_head.append(x1)
                    snake_head.append(y1)
                    snake_list.append(snake_head)

                    # Remove the extra segments of the snake if it gets longer
                    if len(snake_list) > length_of_snake:
                        del snake_list[0]

                    # Check if the snake hits itself
                    for x in snake_list[:-1]:
                        if x == snake_head:
                            self.connector.train(error=-5)
                            game_end = True

                    # Update the snake and food display
                    self.our_snake(self.snake_block_size, snake_list)
                    self.your_score(points)
                    # pygame.display.update()

                    # Check if the snake eats the food
                    if x1 == foodx and y1 == foody:
                        foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
                        foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0
                        length_of_snake += 1
                        points += 1
                        self.connector.train(error=20)
                    



                    #check if snake is moving further away from food
                    if distance_to_food < abs(foodx - x1) + abs(foody - y1):
                        self.connector.train(error=-0.01)
                    elif distance_to_food > abs(foodx - x1) + abs(foody - y1):
                        self.connector.train(error=0.001)
                        
                    distance_to_food = abs(foodx - x1) + abs(foody - y1)

                    
                    # Set game state
                    field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
                    field[int(foody / self.snake_block_size)][int(foodx / self.snake_block_size)] = 1  # food

                    for i, (x, y) in enumerate(snake_list):
                        if i == len(snake_list) - 1:  # this is the head of the snake
                            field[int(y / self.snake_block_size)][int(x / self.snake_block_size)] = '3'  # snake head
                        else:
                            field[int(y / self.snake_block_size)][int(x / self.snake_block_size)] = '2'  # snake body
                    direction = {(-self.snake_block_size, 0): 'Left', (self.snake_block_size, 0): 'Right', (0, -self.snake_block_size): 'Up', (0, self.snake_block_size): 'Down'}.get((x1_change, y1_change), None)
                    food_direction = ('Up' if snake_head[1] > foody else 'Down' if snake_head[1] < foody else '') + \
                            ('Left' if snake_head[0] > foodx else 'Right' if snake_head[0] < foodx else '')
                    food_distance = {"x": abs(foodx - x1), "y": abs(foody - y1)}


                    # draw the data
                    self.render_data(self.connector.get_game_state())
                    self.render_distance(self.connector.get_game_state())
                    self.render_map(self.connector.get_game_state())

                    self.clock.tick(self.snake_speed)
                    pygame.display.update()
                    self.connector.set_game_state(field, direction, food_direction, food_distance)

                pygame.quit()
                quit()

            # Start the game
            @staticmethod
            def game():
                snake = Neuron.Simulation.SnakeEntity()
                snake.game_loop()

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

class NN:
    """
    Neural network which will be used as brain of snake entity.
    """
    def __init__(self, topology=[], connections_type ='full', signal_type='binary' ):
        """ Topology of network is a list of numbers of neurons in layers. First element of list is number of sensors, last element is number of output neurons.
            [N-sensors, N-hidden1, N-hidden2, ..., N-output]
        """
        # list comprehension to create layers of neurons
        self.signal_type = signal_type
        self.layer = [[Neuron(layer_dept=depth, signal_type=signal_type) for i in range(layer_size)] for depth, layer_size in enumerate(topology)]
        
        # print topology as table
        print('\n\n')
        print(f'Topology of network: in-->{topology}<--out')
        print('-------------------')
        for i, layer in enumerate(self.layer):
            print(f'Layer {i}:', f'N({len(layer)}) \n', 'n '*len(layer),'\n')
        
        # connect neurons
        if connections_type == 'full':
            for i, layer in enumerate(self.layer):
                if i == 0:
                    continue
                for neuron in layer:
                    for neuronin_in_previous_layer in self.layer[i-1]:
                        neuron.connect(neuronin_in_previous_layer)


        #elif:
        else:
            pass
        
        # set input properties
        for neuron in self.layer[0]:
            neuron.set_properties(threshold=0.001, refractory_period=0, leakage=100)
        
        #set hidden properties
        for layer in self.layer[1:-1]:
            for neuron in layer:
                neuron.set_properties(threshold=25, refractory_period=0, leakage=0)
                # set random weights for connections - 20 t0 20
                for conn in neuron.connections:
                    conn['weight'] = random.randint(-20, 20)
        
    def input(self, input:list):
        """
        Set input for sensors.
        """
        # check if input is correct

        # set input for sensors
        for i, neuron in enumerate(self.layer[0]):
            neuron.input = input[i]
            neuron.spike = True
    
    def forward(self):
        """
        Forwarding of network.
        """
        for layer in self.layer:
            for neuron in layer:
                neuron.forward()
    
    def output(self):
        """
        Get output of network.
        """
        return [neuron.get_output() for neuron in self.layer[-1]]
    
    # TRAINING METHODS
    def backprop(self, error):
        for neuron in self.layer[-1]:
            neuron.backprop(error=error)
                
    def cycle_without_teacher(self, error, context, learning_method = 'recursive_learning'):
        if self.signal_type == 'binary':
            for neuron in self.layer[-1]:
                if learning_method == 'recursive_learning':
                    neuron.recursive_learning(error=error)

                elif learning_method == 'reinforcement':
                    neuron.reinforcement(error=error)

                elif learning_method == 'cooperation':
                    neuron.cooperation(error=error)
                
        elif self.signal_type == 'numeric':
            assert True, f"Numeric output is not implemented yet."
            pass # TODO: generate error signal for numeric output
        
        # NOTE: (NO CONTEXT LEARNING) reset spikes and membrane potentials of all neurons every cycle
        if not context:
            for layer in self.layer:
                for neuron in layer:
                    neuron.v_m = 0
        
    def cycle_teacher(self, teacher:list, context, learning_method = 'recursive_learning', error_power = None):
        """
        Train network with teacher.
        were teacher is a list of correct answers for each output neuron in every cycle
        "context" used for associative ( historical context is off/on) learning were every cycle is in/dependent from previous one (clear spikes and membrane potentials of all neurons every cycle if False, else - not clear)
        
        *output of neuron can bee Boolean or Number ( depends on signal_type of neurons )

        """
        # check if teacher is correct
        assert len(teacher) == len(self.layer[-1]), f"Teacher is incorrect. It should be {len(self.layer[-1])} elements."
        # signal type of teacher and nn must be the same
        for s in teacher:
            assert type(s) == bool if self.signal_type == 'binary' else type(s) == float, f"Teacher is incorrect. It should be {len(self.layer[-1])} elements."
        
        # generate errors signals for each output neuron by comparing teacher and output of neurons
        if error_power == None:
            error_power = random.randint(0, 50)
        learning_error = 0
        if self.signal_type == 'binary':
            for i, neuron in enumerate(self.layer[-1]):
                # if teacher boolean value is same as output of neuron then error is positive number, else - negative, teacher is None (do't now) error is 0
                if teacher[i] == neuron.get_output():
                    learning_error = error_power # positive error
                else:
                    learning_error = -error_power # negative error
                # train
                if learning_method == 'recursive_learning':
                    neuron.recursive_learning(error=learning_error)

                elif learning_method == 'reinforcement':
                    neuron.reinforcement(error=learning_error)

                elif learning_method == 'cooperation':
                    neuron.cooperation(error=learning_error)
                

        elif self.signal_type == 'numeric':
            assert True, f"Numeric output is not implemented yet."
            pass # TODO: generate error signal for numeric output
        
        # NOTE: (NO CONTEXT LEARNING) reset spikes and membrane potentials of all neurons every cycle
        if not context:
            for layer in self.layer:
                for neuron in layer:
                    neuron.v_m = 0
        
    def cumulative_learning(self):
        """
        Train network with teacher and long term memory associations (cumulative learning).
        """
        pass

class Brain:
    def __init__(self, input_size=77, hidden_size=[], output_size=4) -> None:
        self.topology = [input_size,] + hidden_size + [output_size,]
        self.nn = NN(topology=self.topology)

        # set neurons properties
        for layer in self.nn.layer[1:]:
            for neuron in layer:
                neuron.set_properties(threshold=20, refractory_period=0, leakage=1, reset_ratio=0.0, min_max_input=(-100, 100), sensitivity_adjust_rate=0, sensitivity_restore_rate=100, sensitivity=100, sensitivity_normal=100)
                # set random weights for connections - 20 t0 20
                for conn in neuron.connections:
                    conn['weight'] = random.randint(-20, 20)
    
    def input(self, data):
        # det input data to nn sensors
        self.nn.input(data)
    
    def step(self):
        self.nn.forward()
        return self.nn.output()

    def train(self, error):
        # self.nn.cycle_without_teacher(error=error, context=False, learning_method='recursive_learning')
        self.nn.backprop(error=error)

class ConnectorSnackSnn:
    """ brain methods used by the connector

        brain.input(tuple(data)) -> None
        brain.step()             -> data    # data format is [0, 0, 0, 1]
        brain.train(error)       -> None
    """

    def __init__(self, field_width, field_height) -> None:
        # Set the dimensions of the game field
        self.width = field_width
        self.height = field_height
        # data to/from the neural network
        self.brain = Brain(hidden_size=[80,])
        self.go_to = "UP" #STOP
        self.game_state = {
            "field": [[0 for _ in range(self.width)] for _ in range(self.height)], 
            "direction": None,
            "food_direction": None,
            "food_distance": {"x": None, "y": None}
        }
    
    # Entity methods

    def ai_step(self):
        """
        Colling from a snake to compute the next move
        """
        data = self.brain.step()
        print("data", data)
        # print(data)
        if data == [1,0,0,0]:
            self.go_to = "Up"
        elif data == [0,1,0,0]:
            self.go_to = "Right"
        elif data == [0,0,1,0]:
            self.go_to = "Down"
        elif data == [0,0,0,1]:
            self.go_to = "Left"
        
        elif data == [1,1,0,0]:
            self.go_to = "UpRight"
        elif data == [0,1,1,0]:
            self.go_to = "DownRight"
        elif data == [0,0,1,1]:
            self.go_to = "DownLeft"
        elif data == [1,0,0,1]:
            self.go_to = "UpLeft"
        
        else: #NOTE: error to incorrect data
            self.train(error=-0.01)
    
    def train(self, error):
        """
        Colled from a snake to to provide error signal to the neural network
        """
        print("error", error)
        self.brain.train(error=error)

    def get_move_direction(self):
        """
        Colling from a snake to get move direction
        """
        if self.go_to != None:
            go_to = self.go_to
            self.go_to = None
            return go_to
        else:
            return None

    def set_game_state(self, field, direction, food_direction, food_distance):
        """
        Colling from a game to set the state of the game (push data to the network).
        """
        self.game_state["field"] = field
        self.game_state["direction"] = direction
        self.game_state["food_direction"] = food_direction
        self.game_state["food_distance"] = food_distance
    
        # transfer data to snn
        data = []

        # food direction
        if self.game_state["food_direction"] == "Up":
            data = [1, 0, 0, 0]
        elif self.game_state["food_direction"] == "Right":
            data = [0, 1, 0, 0]
        elif self.game_state["food_direction"] == "Down":
            data = [0, 0, 1, 0]
        elif self.game_state["food_direction"] == "Left":
            data = [0, 0, 0, 1]
            
        elif self.game_state["food_direction"] == "UpRight":
            data = [1, 1, 0, 0]
        elif self.game_state["food_direction"] == "DownRight":
            data = [0, 1, 1, 0]
        elif self.game_state["food_direction"] == "DownLeft":
            data = [0, 0, 1, 1]
        elif self.game_state["food_direction"] == "UpLeft":
            data = [1, 0, 0, 1]
        else:
            data = [0, 0, 0, 0] # STOP
        
        # food distance sum (x+y)
        distance = self.game_state["food_distance"]["x"] + self.game_state["food_distance"]["y"]
        if distance > (self.width + self.height) * 3/4:
            data += [0, 0, 0, 1]
        elif distance > (self.width + self.height) * 1/2:
            data += [0, 0, 1, 0]
        elif distance > (self.width + self.height) * 1/4:
            data += [0, 1, 0, 0]
        else:
            data += [1, 0, 0, 0]


        # direction
        if self.game_state["direction"] == "Up":
            data += [1, 0, 0, 0]
        elif self.game_state["direction"] == "Right":
            data += [0, 1, 0, 0]
        elif self.game_state["direction"] == "Down":
            data += [0, 0, 1, 0]
        elif self.game_state["direction"] == "Left":
            data += [0, 0, 0, 1]
        else:
            data += [0, 0, 0, 0] # STOP
        
        # head in field
        for row in self.game_state["field"]:
            for cell in row:
                if cell == '3':
                    data.append(1)
                else:
                    data.append(0)
        
        # body in field
        for row in self.game_state["field"]:
            for cell in row:
                if cell == '2':
                    data.append(1)
                else:
                    data.append(0)
        
        # if next step collides with boundary
        boundary_is_next = 0
        if self.game_state["direction"] == "Up":
            # check if head ('3') is in top row
            if '3' in self.game_state["field"][0]:
                print("UP collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Right":
            # check if head ('3') is in right column
            if '3' in [row[-1] for row in self.game_state["field"]]:
                print("RIGHT collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Down":
            # check if head ('3') is in bottom row
            if '3' in self.game_state["field"][-1]:
                print("DOWN collision")
                boundary_is_next = 1
        elif self.game_state["direction"] == "Left":
            # check if head ('3') is in left column
            if '3' in [row[0] for row in self.game_state["field"]]:
                print("LEFT collision")
                boundary_is_next = 1
                
        data.append(boundary_is_next)        
        
        self.brain.input(tuple(data))

class SnakeEntity: 
    def __init__(self):
        """
        Snake and environment.
        """
        # Set the dimensions of the game window
        self.width = 160
        self.height = 160

        self.data_width = 700
        self.data_height = 500
        # Define the colors to be used:
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED   = (255, 0, 0)

        # connect the snake to the SNN
        self.connector = ConnectorSnackSnn(field_width=self.width, field_height=self.height)

        # Initialize Pygame:
        pygame.init()

        # Create the game window
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")

        # Create the data window
        self.data_window = pygame.display.set_mode((self.data_width, self.data_height))
        pygame.display.set_caption("Data Window")

        # Set up the game variables:
        self.snake_block_size = 10
        self.snake_speed = 15

        self.x_change = 0
        self.y_change = 0

        self.clock = pygame.time.Clock()

        self.font_style = pygame.font.SysFont(None, 30)
        self.score_font = pygame.font.SysFont(None, 50)
        self.game_data = pygame.font.SysFont(None, 20)
        self.game_distance = pygame.font.SysFont(None, 20)
        self.game_map = pygame.font.SysFont(None, 10)

        #print meadl score of last 30 games
        self.last_score = 0
        self.score = 0
        self.record = 0
        self.game_count = 0

    # Define functions for displaying the snake and the score:
    def our_snake(self, snake_block_size, snake_list):
        for x in snake_list:
            pygame.draw.rect(self.window, self.GREEN, [x[0], x[1], snake_block_size, self.snake_block_size])

    def your_score(self, points):
        # value = score_font.render("Score: " + str(points), True, WHITE)
        # window.blit(value, [0, 0+height])
        self.score += points
        self.game_count += 1
        if points > self.record:
                self.record = points
        if self.game_count == 50:
            self.score = round(self.score/50)
            self.last_score = self.score
            self.score = 0
            self.game_count = 0
        value = self.score_font.render("Middle Score by last 50 games: " + str(self.last_score), True, self.WHITE)
        self.window.blit(value, [0, 0+self.height])
        # show record
        value = self.score_font.render("Record: " + str(self.record), True, self.WHITE)
        self.window.blit(value, [0, 30+self.height])
        # show actual score
        value = self.score_font.render("Actual: " + str(points), True, self.WHITE)
        self.window.blit(value, [0, 60+self.height])

    def render_data(self, game_state):
        self.data_window.blit(self.game_data.render("direction:            "  + str(game_state["direction"     ]), True, self.WHITE),[120, 200+self.height])
        self.data_window.blit(self.game_data.render("food_direction:   "      + str(game_state["food_direction"]), True, self.WHITE),[120, 225+self.height])
        
    def render_distance(self, game_state):
        self.data_window.blit(self.game_distance.render("food_distance:    "  + str(game_state["food_distance" ]), True, self.WHITE),[120, 250+self.height])
        
    def render_map(self, game_state):
        field = game_state["field"]
        for i, row in enumerate(field):
            row_str = ''.join(str(cell) for cell in row)
            self.data_window.blit(self.game_map.render(row_str, True, self.WHITE), [0, self.height+70 + 10 * i])

    # Implement the game loop:
    def game_loop(self):
        game_over = False
        game_end = False

        # Initial position of the snake
        x1 = self.width / 2
        y1 = self.height / 2

        # Change in position
        x1_change = 0
        y1_change = 0

        # Snake body
        snake_list = []
        length_of_snake = 1

        # Generate initial food position
        foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
        foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0

        # Initialize snake_head
        snake_head = []

        points = 0
        distance_to_food = abs(foodx - x1) + abs(foody - y1)
        while not game_over:
            while game_end:

                # Reset game variables
                game_over = False
                game_end = False

                # Initial position of the snake
                x1 = self.width / 2
                y1 = self.height / 2

                # Change in position
                x1_change = 0
                y1_change = 0

                # Snake body
                snake_list = []
                length_of_snake = 1
                points = 0

                # Generate initial food position
                foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
                foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0

                # Initialize snake_head
                snake_head = []

            # Handle connector input events
            self.connector.ai_step()
            go_to = self.connector.get_move_direction()
            if go_to:
                if go_to == 'Left':
                    x1_change = -self.snake_block_size
                    y1_change = 0
                elif go_to == 'Right':
                    x1_change = self.snake_block_size
                    y1_change = 0
                elif go_to == 'Up':
                    y1_change = -self.snake_block_size
                    x1_change = 0
                elif go_to == 'Down':
                    y1_change = self.snake_block_size
                    x1_change = 0
                
                elif go_to == 'UpRight':
                    y1_change = -self.snake_block_size
                    x1_change = self.snake_block_size
                elif go_to == 'DownRight':
                    y1_change = self.snake_block_size
                    x1_change = self.snake_block_size
                elif go_to == 'DownLeft':
                    y1_change = self.snake_block_size
                    x1_change = -self.snake_block_size
                elif go_to == 'UpLeft':
                    y1_change = -self.snake_block_size
                    x1_change = -self.snake_block_size
                    
            else:
                # Handle keypresses
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            x1_change = -self.snake_block_size
                            y1_change = 0
                        elif event.key == pygame.K_RIGHT:
                            x1_change = self.snake_block_size
                            y1_change = 0
                        elif event.key == pygame.K_UP:
                            y1_change = -self.snake_block_size
                            x1_change = 0
                        elif event.key == pygame.K_DOWN:
                            y1_change = self.snake_block_size
                            x1_change = 0

            # Check if the snake hits the boundary
            if x1 >= self.width or x1 < 0 or y1 >= self.height or y1 < 0:
                self.connector.train(error=-0.01)
                game_end = True
            # Update the snake's position
            x1 += x1_change
            y1 += y1_change

            self.window.fill(self.BLACK)

            # Draw border for game area
            pygame.draw.rect(self.window, self.WHITE, pygame.Rect(0, 0, self.width, self.height), 2) # 2 is border thickness
            
            pygame.draw.rect(self.window, self.RED, [foodx, foody, self.snake_block_size, self.snake_block_size])
            snake_head = []
            snake_head.append(x1)
            snake_head.append(y1)
            snake_list.append(snake_head)

            # Remove the extra segments of the snake if it gets longer
            if len(snake_list) > length_of_snake:
                del snake_list[0]

            # Check if the snake hits itself
            for x in snake_list[:-1]:
                if x == snake_head:
                    self.connector.train(error=-5)
                    game_end = True

            # Update the snake and food display
            self.our_snake(self.snake_block_size, snake_list)
            self.your_score(points)
            # pygame.display.update()

            # Check if the snake eats the food
            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, self.width - self.snake_block_size) / 10.0) * 10.0
                foody = round(random.randrange(0, self.height - self.snake_block_size) / 10.0) * 10.0
                length_of_snake += 1
                points += 1
                self.connector.train(error=20)
            



            #check if snake is moving further away from food
            if distance_to_food < abs(foodx - x1) + abs(foody - y1):
                self.connector.train(error=-0.01)
            elif distance_to_food > abs(foodx - x1) + abs(foody - y1):
                self.connector.train(error=0.001)
                
            distance_to_food = abs(foodx - x1) + abs(foody - y1)

            
            # Set game state
            field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
            field[int(foody / self.snake_block_size)][int(foodx / self.snake_block_size)] = 1  # food

            for i, (x, y) in enumerate(snake_list):
                if i == len(snake_list) - 1:  # this is the head of the snake
                    field[int(y / self.snake_block_size)][int(x / self.snake_block_size)] = '3'  # snake head
                else:
                    field[int(y / self.snake_block_size)][int(x / self.snake_block_size)] = '2'  # snake body
            direction = {(-self.snake_block_size, 0): 'Left', (self.snake_block_size, 0): 'Right', (0, -self.snake_block_size): 'Up', (0, self.snake_block_size): 'Down'}.get((x1_change, y1_change), None)
            food_direction = ('Up' if snake_head[1] > foody else 'Down' if snake_head[1] < foody else '') + \
                    ('Left' if snake_head[0] > foodx else 'Right' if snake_head[0] < foodx else '')
            food_distance = {"x": abs(foodx - x1), "y": abs(foody - y1)}


            # draw the data
            # self.render_data(self.connector.get_game_state())
            # self.render_distance(self.connector.get_game_state())
            # self.render_map(self.connector.get_game_state())

            self.clock.tick(self.snake_speed)
            pygame.display.update()
            self.connector.set_game_state(field, direction, food_direction, food_distance)

        pygame.quit()
        quit()

if __name__ == "__main__":
    # Run tests
    # Neuron.Simulation.NN.no_context_teacher_learning()
    Neuron.Test.run_all_tests()
    # Neuron.Simulation.SnakeEntity.game()
    
    # Run Snake game
    snake = SnakeEntity()
    snake.game_loop()