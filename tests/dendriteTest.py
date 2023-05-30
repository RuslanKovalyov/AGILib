import sys
import os
# Add the parent directory to sys.path
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from snn.dendrites import Dendrite

class DendriteTest:
    def test_step(self):
        print("\n----------Testing Dendrite----------")

        # Test 1: Dendrite with no input mediator
        dendrite = Dendrite(weight=10)
        dendrite.input_mediator = ""  # can be skipped, but included for clarity

        result = dendrite.step()
        assert result == 0, "\n\n***\tTest 1 failed: output should be 0 with no input mediator"
        print("\n\tTest 1: Passed!")

        # Test 2: Dendrite with input mediator
        dendrite = Dendrite(weight=10)
        dendrite.input_mediator = "dopamine"

        result = dendrite.step()
        assert result == 10, "\n\n***\tTest 2 failed: output should equal the dendrite's weight"
        print("\n\tTest 2: Passed!")

        # Test 3: Dendrite weight update
        dendrite = Dendrite(weight=10)
        dendrite.set_weight(20)
        dendrite.input_mediator = "dopamine"

        result = dendrite.step()
        assert result == 20, "\n\n***\tTest 3 failed: output should equal the updated dendrite's weight"
        print("\n\tTest 3: Passed!")

        # Test 4: Input mediator cleared after step
        dendrite = Dendrite(weight=10)
        dendrite.input_mediator = "dopamine"
        dendrite.step()

        assert dendrite.input_mediator == "", "\n\n***\tTest 4 failed: input mediator should be cleared after step"
        print("\n\tTest 4: Passed!")

        # Test 5: Dendrite with negative weight and input mediator
        dendrite = Dendrite(weight=-10)
        dendrite.input_mediator = "dopamine"

        result = dendrite.step()
        assert result == -10, "\n\n***\tTest 5 failed: output should equal the negative dendrite's weight"
        print("\n\tTest 5: Passed!")

        # Test 6: Dendrite weight update to negative
        dendrite = Dendrite(weight=10)
        dendrite.set_weight(-20)
        dendrite.input_mediator = "dopamine"

        result = dendrite.step()
        assert result == -20, "\n\n***\tTest 6 failed: output should equal the updated negative dendrite's weight"
        print("\n\tTest 6: Passed!")

        print("\n-----All dendrite tests passed!-----\n")


# Run the test
DendriteTest().test_step()
