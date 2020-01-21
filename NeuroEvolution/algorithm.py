import numpy as np
from typing import Union, Tuple, List


class Model:
    def __init__(
            self,
            input_shape: Union[int, Tuple[int]],
            hidden_layers: List[int],
            output_shape: Union[int, Tuple[int]],
            activation=lambda x: max(0, x),
            output_activation=lambda x: (1.0 / (1.0 + np.exp(-x))),
    ):
        """Generate a model with feed forward capabilities
        
        Arguments:
            input_shape {Union[int, Tuple[int]]} -- shape of expected input
            hidden_layers {List[int]} -- dimensions of hidden layers, if any
            output_shape {Union[int, Tuple[int]]} -- shape of output
        
        Keyword Arguments:
            activation {function} -- activation function for hidden layers 
                                     (default: {lambda x:max(0, x)})
            output_activation {function} -- activation function for output layer
                                 (default: {lambda x:(1.0 / (1.0 + np.exp(-x)))})
        """
        self.output_activation = output_activation
        self.activation = activation
        self.input_shape = input_shape
        self.output_shape = output_shape

        self.weights: list = []
        self.biases: list = []

        previous_layer_size = np.prod(self.input_shape)
        for layer_dimension in hidden_layers + [int(np.prod(self.output_shape))]:
            self.weights.append(
                np.random.normal(size=(layer_dimension, previous_layer_size))
            )
            self.biases.append(np.random.normal(size=(layer_dimension, 1)))

    def feed_forward(self, observation: List[float]) -> List[float]:
        last_layer_output = np.array(observation).reshape(self.input_shape)
        for layer_weights, layer_biases in zip(self.weights, self.biases):
            last_layer_output = last_layer_output * layer_weights + layer_biases
        last_layer_output = np.array(last_layer_output).reshape(self.output_shape)
        return last_layer_output


class NeuroEvolution:

    # TODO: add mutation method
    # TODO: add crossover method
    def __init__(
            self,
            population_size: int,
            input_shape: Union[int, Tuple[int]],
            hidden_layers: List[int],
            output_shape: Union[int, Tuple[int]],
    ):
        self.population_size = population_size
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.population = [
            self.generate_model(input_shape, hidden_layers, output_shape)
            for _ in range(population_size)
        ]

    def get_actions(self, observations: list):
        """Get the actions for each agent according to each observation
        
        Arguments:
            observations {list} -- list of gym observations
        """
        actions = []
        for agent, observation in zip(self.population, observations):
            actions.append(agent.feed_forward(observation))

        return actions

    @staticmethod
    def generate_model(
            input_shape: Union[int, Tuple[int]],
            hidden_layers: List[int],
            output_shape: Union[int, Tuple[int]],
    ) -> Model:
        return Model(input_shape, hidden_layers, output_shape)


if __name__ == "__main__":
    ne = NeuroEvolution(10, 5, [2, 3], 4)