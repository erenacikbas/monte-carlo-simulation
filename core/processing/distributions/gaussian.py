# Gaussian Distribution

import numpy as np


def generate_normal_distribution(mu, sigma, size):
    """
    Generate a normal (Gaussian) distribution.

    Parameters:
    - mu: float. The mean of the distribution.
    - sigma: float. The standard deviation of the distribution.
    - size: int. The number of samples to generate.

    Returns:
    - samples: ndarray. An array of samples from the normal distribution.
    """
    samples = np.random.normal(mu, sigma, size)
    return samples
