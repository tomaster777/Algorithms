"""
Contains all logical operations to that are needed to transform the data
"""
from typing import List

import numpy as np
import gym
from gym import spaces

from structs import (
    BaseNodes,
    ConnectionInnovation,
    ConnectionProperties,
    Environments,
    NodeInnovation,
    NodeProperties,
)


def feed_forward(
    inputs: np.ndarray,
    connections: List[ConnectionInnovation],
    connection_data: List[ConnectionProperties],
    node_data: List[NodeProperties],
    base_nodes: BaseNodes,
) -> np.ndarray:
    """Calculate the output of a network using recursion

    Arguments:
        inputs {np.ndarray} -- network inputs
        connections {List[ConnectionInnovation]} -- connections between nodes
        connection_data {ConnectionProperties} -- connection weights and biases
        node_data {NodeProperties} -- node biases
        base_nodes {BaseNodes} -- input and output nodes

    Returns:
        np.ndarray -- network output
    """
    return [
        _get_node_output(
            node_index, inputs, connections, connection_data, node_data, base_nodes, []
        )
        for node_index in base_nodes.output_nodes
    ]


def _get_node_output(
    node_index: int,
    inputs: np.ndarray,
    connections: List[ConnectionInnovation],
    connection_data: ConnectionProperties,
    node_data: NodeProperties,
    base_nodes: BaseNodes,
    ignore_connections: List[ConnectionInnovation],
) -> float:
    """helper function to get output of a single node using recursion

    Arguments:
        node_index {int} -- index of node to get output of
        inputs {np.ndarray} -- network inputs
        connections {List[ConnectionInnovation]} -- connections between nodes
        connection_data {ConnectionProperties} -- connection weights and biases
        node_data {NodeProperties} -- node biases
        base_nodes {BaseNodes} -- input and output nodes
        ignore_connections {List[ConnectionInnovation]} -- connections previously
                                                           calculated

    Returns:
        float -- output of node
    """
    # input nodes are just placeholders for the network input
    if node_index in base_nodes.input_nodes:
        return inputs[node_index]

    # since input nodes don't have properties, the node_properties_index is offset by
    # the input node amount
    node_properties_index = node_index - len(base_nodes.input_nodes)
    return node_data.activations[node_properties_index](  # activation function of node
        np.sum(  # weighted sum of the outputs of all nodes outputing into node
            [
                _get_node_output(
                    connection.src,
                    inputs,
                    connections,
                    connection_data,
                    node_data,
                    base_nodes,
                    ignore_connections + [connection],  # mark connection as to-ignore
                )
                * connection_weight  # weight the output
                for connection, connection_weight, connection_enabled in zip(
                    connections, connection_data.weights, connection_data.enabled
                )
                if (
                    connection.dst == node_index  # get connections outputing into node
                    and connection
                    not in ignore_connections  # ignore accounted for connections
                    and connection_enabled  # ignore disabled connections
                )
            ]
        )
        + node_data.biases[node_properties_index]  # add node bias
    )


def transform_network_output(network_output: List[float]) -> spaces.Discrete:
    return np.argmax(network_output)


def evaluate_networks(
    environments: Environments,
    connections: List[ConnectionInnovation],
    connection_data: List[ConnectionProperties],
    node_data: List[NodeProperties],
    base_nodes: BaseNodes,
    max_steps: int,
    episodes: int,
    render: bool = False,
) -> List[float]:
    all_rewards = []
    for (
        environment,
        network_connections,
        network_connection_data,
        network_node_data,
    ) in zip(environments.environments, connections, connection_data, node_data):
        network_rewards = []
        for e in range(episodes):
            print(e)
            # reset environment
            episode_reward = _run_episode(
                environment,
                max_steps,
                network_connections,
                network_connection_data,
                network_node_data,
                base_nodes,
                render,
            )

            # log reward
            network_rewards.append(episode_reward)
        all_rewards.append(np.average(network_rewards))
    return all_rewards


def _run_episode(
    environment: gym.Env,
    max_steps: int,
    connections: List[ConnectionInnovation],
    connection_data: List[ConnectionProperties],
    node_data: List[NodeProperties],
    base_nodes: BaseNodes,
    render: bool = False,
) -> float:
    """helper function that runs an episode and returns the episode rewards

    Arguments:
        environment {gym.Env} -- gym environment
        max_steps {int} -- limit of steps to take in episode
        connections {List[ConnectionInnovation]} -- network connections
        connection_data {List[ConnectionProperties]} -- network connection data
        node_data {List[NodeProperties]} -- network node data
        base_nodes {BaseNodes} -- network input and output nodes

    Returns:
        float -- network episode reward
    """

    # reset environment
    episode_reward = 0
    observation = environment.reset()

    # play through simulation
    for _ in range(max_steps):
        if render:
            environment.render()
        network_output = feed_forward(
            observation, connections, connection_data, node_data, base_nodes,
        )
        action = transform_network_output(network_output)
        observation, reward, done, _ = environment.step(action)

        episode_reward += reward

        if done:
            break
    environment.close()
    return episode_reward