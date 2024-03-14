# Author: Eren Tuna Açıkbaş 2024

# Matplotlib is a plotting library
import matplotlib.pyplot as plt


def plot_histogram(volumes):
    """
    Plot histogram of reservoir volumes.

    :param volumes: A list of reservoir volumes.
    :type volumes: list
    :return: None
    :rtype: None
    """
    plt.hist(volumes, bins=50, color='blue', alpha=0.7)
    plt.xlabel('Reservoir Volume (STB)')
    plt.ylabel('Frequency')
    plt.title('Monte Carlo Simulation of Reservoir Volume')
    plt.show()
