import numpy as np

class SpikingNeuralNetwork:
    def __init__(self, topology, threshold=1.0):
        self.layers = len(topology)
        self.weights = []
        self.threshold = threshold
        for i in range(self.layers - 1):
            # Initialize weights in a smaller range (-0.5 to 0.5)
            weight_matrix = np.random.uniform(-0.5, 0.5, size=(topology[i+1], topology[i]))
            self.weights.append(weight_matrix)

    def forward(self, input_data):
        spikes = np.where(input_data, 1.0, 0.0)
        self.spikes_store = [spikes]
        for i in range(self.layers - 1):
            potentials = np.dot(self.weights[i], spikes)
            spikes = (potentials > self.threshold).astype(float)
            self.spikes_store.append(spikes)
        return spikes

    def train(self, input_data, target_data, learning_rate=0.1):
        output_spikes = self.forward(input_data)
        target_spikes = np.where(target_data, 1.0, 0.0)
        error = target_spikes - output_spikes

        for i in range(len(self.weights) - 1, -1, -1):
            spikes_input = self.spikes_store[i]
            delta_w = learning_rate * np.outer(error, spikes_input)
            
            # Modulate learning rate for deeper layers
            if i > 0:
                delta_w *= 0.5
            
            self.weights[i] += delta_w
            error = np.dot(self.weights[i].T, error)

# Example Usage
topology = [4, 800, 80, 8]
snn = SpikingNeuralNetwork(topology)

input_data = np.array([True, True, True, False])
target_data = np.array([True, False, True, False, True, True, True, False])

input_data2 = np.array([True, False, True, True])
target_data2 = np.array([False, True, False, False, True, True, False, False])

input_data3 = np.array([False, False, False, True])
target_data3 = np.array([True, True, True, False, False, True, False, True])

epochs = 20
learning_rate = 0.05

for _ in range(epochs):
    if learning_rate > 0.001:
        learning_rate = round(learning_rate * 0.999, 5) # make rate highi in start and then decrease it to effectively train the network
    print(learning_rate)
    snn.train(input_data, target_data, learning_rate)
    snn.train(input_data2, target_data2, learning_rate)
    snn.train(input_data3, target_data3, learning_rate)

# Test the trained network
output = snn.forward(input_data)
output2 = snn.forward(input_data2)
output3 = snn.forward(input_data3)
print(output.astype(bool))
print(output2.astype(bool))
print(output3.astype(bool))

