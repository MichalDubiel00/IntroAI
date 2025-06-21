import numpy as np

class Perceptron:
    def __init__(self):
        self.synaptic_weights = 2 * np.random.random((3,1)) - 1
        print("Initial synaptic weights:")
        print(self.synaptic_weights)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, sigmoid_output):
        # derivative of sigmoid given the sigmoid output
        return sigmoid_output * (1 - sigmoid_output)

    def think(self, inputs):
        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs, self.synaptic_weights))
        return output

    def train(self, inputs, targets, iterations):
        for _ in range(iterations):
            output = self.think(inputs)
            error = targets - output
            adjustment = np.dot(inputs.T, error * self.sigmoid_derivative(output))
            self.synaptic_weights += adjustment

if __name__ == "__main__":
    nn = Perceptron()

    inputs = np.array([
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [0, 1, 1]
    ])

    targets = np.array([[0], [1], [1], [0]])

    nn.train(inputs, targets, 10000)

    print("Training complete.\n")

    # Ask user for inputs I1, I2, I3
    print("Enter values for input signals (I1, I2, I3) separated by spaces (0 or 1):")
    user_input = input().split()

    
    user_inputs = np.array([float(x) for x in user_input])
    output = nn.think(user_inputs)
    print(f"Perceptron output (belief) for input {user_inputs} is: {output[0]:.4f}")
  