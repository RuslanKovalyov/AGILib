import sys
import os
# Add the parent directory to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from snn.membranes import Membrane


class MembraneTest:
    def test_step(self):
        print("\n----------Testing Membrane----------")

        # Test 1: Membrane at rest state, no input given
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=0.1)
        
        membrane.step(input_value=0, refractory=False)
        assert membrane.v_m == 0, "\n\n***\tTest 1 failed: v_m should be at rest state (0)"
        assert membrane.spike is False, "\n\n***\tTest 1 failed: There shouldn't be a spike"
        print("\n\tTest 1: Passed!")

        # Test 2: Membrane receives input but not enough to reach threshold
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=10)
        
        membrane.step(input_value=10, refractory=False)
        assert membrane.v_m > 0 and membrane.v_m < 20, "\n\n***\tTest 2 failed: v_m should increase but not reach the threshold"
        assert membrane.v_m == 9 , "\n\n***\tTest 2 failed: v_m should be leaked and reset to 9"
        assert membrane.spike is False, "\n\n***\tTest 2 failed: There shouldn't be a spike"
        print("\n\tTest 2: Passed!")
        
        # Test 3: Membrane receives enough input to reach threshold and generate a spike
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=0.1)
        
        membrane.step(input_value=20, refractory=False)
        assert membrane.v_m == 2.0, "\n\n***\tTest 3 failed: v_m should be reset to 2.0 after a spike"
        assert membrane.spike is True, "\n\n***\tTest 3 failed: There should be a spike"
        print("\n\tTest 3: Passed!")

        # Test 4: Membrane in refractory period should not generate a spike
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.5, leakage=0.1)
        
        membrane.step(input_value=20, refractory=True)
        assert membrane.v_m == 10, "\n\n***\tTest 4 failed: v_m should remain at reset level during refractory period based on reset_ratio"
        assert membrane.spike is False, "\n\n***\tTest 4 failed: There shouldn't be a spike during refractory period"
        print("\n\tTest 4: Passed!")

        # Test 5: Series of inputs, should generate a spikes on the 3rd input and reset to 2
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=10)

        membrane.step(input_value=10, refractory=False)
        assert membrane.v_m == 9, "\n\n***\tTest 5 failed: v_m should be reset to 9"
        assert membrane.spike is False, "\n\n***\tTest 5 failed: There shouldn't be a spike"
        membrane.step(input_value=1, refractory=False)
        assert membrane.v_m == 9, "\n\n***\tTest 5 failed: v_m should be reset to 9"
        membrane.step(input_value=11, refractory=False)
        assert membrane.spike is True, "\n\n***\tTest 5 failed: There should be a spike"
        assert membrane.v_m == 2, "\n\n***\tTest 5 failed: v_m should be reset to 2"
        print('\n\tTest 5: Passed!')

        # Test 6: Single negative input, should not generate a spike (inhibitory effect on a neuron)
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=20)

        membrane.step(input_value=-10, refractory=False)
        assert membrane.v_m == -8, "\n\n***\tTest 6 failed: v_m should be reset to -8 (leakage 20%)"
        assert membrane.spike is False, "\n\n***\tTest 6 failed: There shouldn't be a spike"
        print('\n\tTest 6: Passed!')

        # Test 7: Series of negative inputs and one positive input equal to threshold not enough to generate a spike
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=20)
        
        membrane.step(input_value=-10, refractory=False)
        assert membrane.v_m == -8, "\n\n***\tTest 7 failed: v_m should be reset to -8 (leakage 20%)"
        assert membrane.spike is False, "\n\n***\tTest 7 failed: There shouldn't be a spike"
        membrane.step(input_value=-2, refractory=False)
        assert membrane.v_m == -8, "\n\n***\tTest 7 failed: v_m should be reset to -8 (leakage 20%)"
        membrane.step(input_value=25, refractory=False)
        assert membrane.spike is False, "\n\n***\tTest 7 failed: There shouldn't be a spike"
        assert membrane.v_m == 13.6, "\n\n***\tTest 7 failed: v_m should be reset to 13.6 (leakage 20%)"
        print('\n\tTest 7: Passed!')

        
        print("\n-----All membrane tests passed!-----\n")

# Run the test
MembraneTest().test_step()
