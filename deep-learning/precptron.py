import numpy as np


class Perceptron:
    def __init__(self, input_size, learning_rate=0.01):
        self.weights = np.zeros(input_size)
        self.bias = 0.0
        self.learning_rate = learning_rate

    def activation(self, x):
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        linear_output = np.dot(inputs, self.weights) + self.bias

        return self.activation(linear_output)

    def train(self, training_inputs, labels, epochs=10):
        for epoch in range(epochs):
            for inputs, label in zip(training_inputs, labels):
                prediction = self.predict(inputs)

                error = label - prediction

                self.weights += self.learning_rate * error * inputs
                self.bias += self.learning_rate * error


training_inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
labels = np.array([0, 0, 0, 1])

perceptron = Perceptron(input_size=2)

perceptron.train(training_inputs, labels, epochs=10)

test_inputs = np.array([0, 0])
print(f"Prediction for {test_inputs}: {perceptron.predict(test_inputs)}")

test_inputs = np.array([0, 1])
print(f"Prediction for {test_inputs}: {perceptron.predict(test_inputs)}")

test_inputs = np.array([1, 0])
print(f"Prediction for {test_inputs}: {perceptron.predict(test_inputs)}")

test_inputs = np.array([1, 1])
print(f"Prediction for {test_inputs}: {perceptron.predict(test_inputs)}")
