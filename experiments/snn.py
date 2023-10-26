import numpy as np

class SpikingNeuralNetwork:
    def __init__(self, topology, threshold=1.0):
        self.layers = len(topology)
        self.weights = []
        self.threshold = threshold
        for i in range(self.layers - 1):
            weight_matrix = np.random.randn(topology[i+1], topology[i])
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
            self.weights[i] += delta_w
            error = np.dot(self.weights[i].T, error)

# Example Usage
topology = [4, 8, 8]
snn = SpikingNeuralNetwork(topology)

input_data = np.array([True, True, True, False])
target_data = np.array([True, False, True, False, True, True, True, False])

input_data2 = np.array([True, False, True, True])
target_data2 = np.array([False, True, False, False, True, True, False, False])

epochs = 20
learning_rate = 0.5

for _ in range(epochs):
    if learning_rate > 0.001:
        learning_rate = round(learning_rate * 0.99, 3) # make rate highi in start and then decrease it to effectively train the network
    print(learning_rate)
    snn.train(input_data, target_data, learning_rate)
    snn.train(input_data2, target_data2, learning_rate)

# Test the trained network
output = snn.forward(input_data)
output2 = snn.forward(input_data2)
print(output.astype(bool))
print(output2.astype(bool))
