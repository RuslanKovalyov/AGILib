import sys
import os
# Add the parent directory to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from snn.neuronus import Membrane


class MembraneTest:
    def test_step(self):

        # Test 1: Membrane at rest state, no input given
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=0.1)
        
        membrane.step(input_value=0, refractory=False)
        assert membrane.v_m == 0, "\nTest 1 failed: v_m should be at rest state (0)"
        assert membrane.spike is False, "\nTest 1 failed: There shouldn't be a spike"
        print("\nTest 1: Passed!")

        # Test 2: Membrane receives input but not enough to reach threshold
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=10)
        
        membrane.step(input_value=10, refractory=False)
        assert membrane.v_m > 0 and membrane.v_m < 20, "\nTest 2 failed: v_m should increase but not reach the threshold"
        assert membrane.v_m == 9 , "\nTest 2 failed: v_m should be leaked and reset to 9"
        assert membrane.spike is False, "\nTest 2 failed: There shouldn't be a spike"
        print("\nTest 2: Passed!")
        
        # Test 3: Membrane receives enough input to reach threshold and generate a spike
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=0.1)
        
        membrane.step(input_value=20, refractory=False)
        assert membrane.v_m == 2.0, "\nTest 3 failed: v_m should be reset to 2.0 after a spike"
        assert membrane.spike is True, "\nTest 3 failed: There should be a spike"
        print("\nTest 3: Passed!")

        # Test 4: Membrane in refractory period should not generate a spike
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.5, leakage=0.1)
        
        membrane.step(input_value=20, refractory=True)
        assert membrane.v_m == 10, "\nTest 4 failed: v_m should remain at reset level during refractory period based on reset_ratio"
        assert membrane.spike is False, "\nTest 4 failed: There shouldn't be a spike during refractory period"
        print("\nTest 4: Passed!")

        # Test 5: Series of inputs, should generate a spikes on the 3rd input and reset to 2
        membrane = Membrane(rest=0, threshold=20, reset_ratio=0.1, leakage=10)

        membrane.step(input_value=10, refractory=False)
        assert membrane.v_m == 9, "\nTest 5 failed: v_m should be reset to 9"
        assert membrane.spike is False, "\nTest 5 failed: There shouldn't be a spike"
        print(membrane.v_m)
        membrane.step(input_value=1, refractory=False)
        assert membrane.v_m == 9, "\nTest 5 failed: v_m should be reset to 9"
        membrane.step(input_value=11, refractory=False)
        assert membrane.spike is True, "\nTest 5 failed: There should be a spike"
        assert membrane.v_m == 2, "\nTest 5 failed: v_m should be reset to 2"
        print('\nTest 5: Passed!')
        print(membrane.v_m)


        print("\n--All tests passed!--")

# Run the test
MembraneTest().test_step()
