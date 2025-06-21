import random
import numpy as np

# Simple Neural Netowrk Implementation
class Perception:
    def __init__(self):
        self.synaptic_weights = 2 * np.random.random((3,1))-1
        print("Initial synaptic weights:")
        print(self.synaptic_weights)

    def sigmoid(self,x):
        return 1/(1+np.exp(-x))
    
    def sigmoid_derivative(self,x):
        activation = self.sigmoid(x)
        return activation * (1 - activation)
    def think(self,inputs):
        inputs = inputs.astype(float)
        outputs = self.sigmoid(np.dot(inputs,self.synaptic_weights))
        return outputs
    def train(self,inputs,targets,iterations):
        for _ in range(iterations):
            output = self.think(inputs)

            error = targets - output
            Wd = np.dot(inputs.T,error * self.sigmoid_derivative(output))
            self.synaptic_weights += Wd
if __name__ == "__main__":
    nn = Perception()

    # Training dataset: 4 examples with 3 inputs each (including bias)
    inputs = np.array([
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [0, 1, 1]
    ])
    
    targets = np.array([[0], [1], [1], [0]])

    nn.train(inputs, targets, 10000)

    print("Output after training:")
    print(nn.think(np.array([1, 0, 0])))        