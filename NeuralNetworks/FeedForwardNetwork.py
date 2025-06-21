import time
import numpy as np
import matplotlib.pyplot as plt

class NeuralNetwork():

    #initialize the neural network
    #Xavier (Glorot) initialization formula
    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate):
        self.input_nodes = inputnodes
        self.hidden_nodes = hiddennodes
        self.output_nodes = outputnodes
        self.learning_rate = learningrate
        
        limit = np.sqrt(6 / (self.input_nodes + self.hidden_nodes))
        self.weights_input_hidden = np.random.uniform(-limit, limit, 
                                                     (self.hidden_nodes, self.input_nodes))
        
        h_limit = np.sqrt(6 / (self.hidden_nodes + self.output_nodes))
        self.weights_hidden_output  =  np.random.uniform(-h_limit,h_limit,(self.output_nodes,self.hidden_nodes))

        self.bias_hidden = np.random.randn(self.hidden_nodes, 1) * 0.01
        self.bias_output = np.random.randn(self.output_nodes, 1) * 0.01

    #sigmoid function
    def sigmoid(self,x):
        return 1/(1+np.exp(-x))
    
    def sigmoid_derivative(self,x):
        return self.sigmoid(x) * (1 - self.sigmoid(x))
    
    #train the neural network
    def train(self, inputs_list, targets_list, iterations):
        inputs = np.array(inputs_list, ndmin=2).T 
        targets = np.array(targets_list, ndmin=2).T

        for _ in range(iterations):
            # Forward pass
            hidden_inputs = np.dot(self.weights_input_hidden, inputs) + self.bias_hidden
            hidden_outputs = self.sigmoid(hidden_inputs)

            final_inputs = np.dot(self.weights_hidden_output, hidden_outputs) + self.bias_output
            final_outputs = self.sigmoid(final_inputs)

            # Output error and gradient
            output_errors = targets - final_outputs
            output_grad = output_errors * self.sigmoid_derivative(final_outputs)
            
            # Hidden layer error and gradient
            hidden_errors = np.dot(self.weights_hidden_output.T, output_errors)
            hidden_grad = hidden_errors * self.sigmoid_derivative(hidden_outputs)

            # Update weights
            self.weights_hidden_output += self.learning_rate * np.dot(output_grad, hidden_outputs.T)
            self.weights_input_hidden += self.learning_rate * np.dot(hidden_grad, inputs.T)

            self.bias_output += self.learning_rate * output_grad
            self.bias_hidden += self.learning_rate * hidden_grad

    def think(self, inputs_list):
        inputs = np.array(inputs_list, ndmin=2).T
        hidden_inputs = np.dot(self.weights_input_hidden, inputs) + self.bias_hidden
        hidden_outputs = self.sigmoid(hidden_inputs)
        final_inputs = np.dot(self.weights_hidden_output, hidden_outputs) + self.bias_output
        final_outputs = self.sigmoid(final_inputs)
        return final_outputs
        
def load_data(filename):
    with open(filename, 'r') as f:
        return f.readlines()

def normalize_input(raw_values):
    # raw_values: list or array of pixel strings
    # convert strings to floats and scale [0,255] to [0.01, 0.99]
    inputs = np.asarray(raw_values, dtype=float) 
    inputs = inputs / 255.0 * 0.98 + 0.01  # scale 0-255 -> 0.01-0.99
    return inputs

def create_target(label, num_outputs=10):
    targets = np.ones(num_outputs) * 0.01
    targets[int(label)] = 0.99
    return targets

if __name__ == "__main__":
    input_nodes = 784
    hidden_nodes = 200
    output_nodes = 10
    learning_rate = 0.01

    # Load data
    training_data_list = load_data("mnist_train_full.csv")
    test_data_list = load_data("custom_test.csv")

    # Initialize network
    n = NeuralNetwork(input_nodes, hidden_nodes, output_nodes, learning_rate)

    start_time = time.time()

    # Train on all training data (each line in CSV)
    for record in training_data_list:
        all_values = record.strip().split(',')
        label = all_values[0]
        inputs = normalize_input(all_values[1:])
        targets = create_target(label, output_nodes)
        n.train(inputs, targets, iterations=1)

    training_time = time.time() - start_time
    print(f"\nTraining completed in {training_time:.2f} seconds")

    # Test the network and collect wrong guesses
    scorecard = []
    wrong_guesses = []

    for i, record in enumerate(test_data_list):
        all_values = record.strip().split(',')
        correct_label = int(all_values[0])
        inputs = normalize_input(all_values[1:])

        outputs = n.think(inputs)
        predicted_label = np.argmax(outputs)

        if predicted_label == correct_label:
            scorecard.append(1)
        else:
            scorecard.append(0)
            wrong_guesses.append({
                'index': i,
                'image': np.asarray(all_values[1:], dtype=float).reshape((28,28)),
                'correct': correct_label,
                'predicted': predicted_label,
                'outputs': outputs.flatten()
            })

    scorecard_array = np.array(scorecard)
    print(f"Performance: {scorecard_array.sum() / scorecard_array.size * 100:.2f}% correct")
    
    # Display wrong guesses
    if wrong_guesses:
        print(f"\nNumber of wrong guesses: {len(wrong_guesses)}")
        for guess in wrong_guesses:
            plt.figure(figsize=(8, 4))
            
            # Show the image
            plt.subplot(1, 2, 1)
            plt.imshow(guess['image'], cmap='Greys', interpolation='None')
            plt.title(f"Actual: {guess['correct']}, Predicted: {guess['predicted']}")
            
            # Show the output neuron activations
            plt.subplot(1, 2, 2)
            plt.bar(range(10), guess['outputs'], color='blue')
            plt.xticks(range(10))
            plt.title("Output neuron activations")
            plt.ylim(0, 1)
            
            plt.tight_layout()
            plt.show()
    else:
        print("No wrong guesses!")

