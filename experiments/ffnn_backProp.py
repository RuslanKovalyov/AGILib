import numpy as np
import time
class NeuralNetwork:
    def __init__(self, topology):
        self.layers = len(topology)
        self.weights = []
        self.biases = []
        self.outputs = []
        
        for i in range(self.layers - 1):
            weight_matrix = np.random.randn(topology[i+1], topology[i])
            bias_vector = np.random.randn(topology[i+1], 1)
            self.weights.append(weight_matrix)
            self.biases.append(bias_vector)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)
        
    def forward(self, input_data):
        self.outputs = []
        current_data = np.reshape(input_data, (len(input_data), 1))
        self.outputs.append(current_data)
        
        for i in range(self.layers - 1):
            current_data = self.sigmoid(
                np.dot(self.weights[i], current_data) + self.biases[i]
            )
            self.outputs.append(current_data)
        return current_data

    def train(self, input_data, target, learning_rate, epochs=1):
        # Perform forward pass
        self.forward(input_data)

        # Calculate error and backward propagate
        deltas = []
        error = target.reshape(-1, 1) - self.outputs[-1]
        delta = error * self.sigmoid_derivative(self.outputs[-1])
        deltas.append(delta)
        
        for i in range(self.layers - 2, 0, -1):
            delta = np.dot(self.weights[i].T, delta) * self.sigmoid_derivative(self.outputs[i])
            deltas.append(delta)
            
        deltas.reverse()

        # Update weights and biases depending on epoch (fast learning at first, then slower)
        for i in range(len(self.weights)):
            self.weights[i] += learning_rate * np.dot(deltas[i], self.outputs[i].T) * (epochs / 100)
            self.biases[i] += learning_rate * deltas[i] * (epochs / 10000)

# Example Usage
topology = [4, 8, 8]
nn = NeuralNetwork(topology)

# Sample training data
input_data = np.array([1, 0.5, 0.25, 0.125])
target_data = np.array([0.005, 0.01, 0.05, 0.09, 0.1, 0.5, 0.9, 1])

input_data2 = np.array([0.5, 0.75, 0.95, 0.033])
target_data2 = np.array([0.99, 0.9, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001])

epochs = 100_000
learning_rate = 0.05

# time to train the network
training_time = time.time()

for e in range(epochs):
    nn.train(input_data, target_data, learning_rate, epochs=e+1)
    nn.train(input_data2, target_data2, learning_rate, epochs=e+1)

training_time = time.time() - training_time
# print the training time of one cycle
print('Training time of one cycle:', training_time / 2, 'seconds\n')

# Test the trained network
output1 = nn.forward(input_data)
output2 = nn.forward(input_data2)
# print rounded output to 3 decimal places
print('output 1:\n', np.round(output1, 3), '\n')
print('output 2:\n', np.round(output2, 3), '\n')

# print the weights and biases
print('Weights:', nn.weights)
print('Biases:', nn.biases)