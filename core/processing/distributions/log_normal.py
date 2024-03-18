# Log-normal Distribution
import numpy as np


def generate_lognormal_distribution(mu, sigma, size):
    """
    Generate a log-normal distribution.

    Parameters:
    - mu: float. The mean of the underlying normal distribution.
    - sigma: float. The standard deviation of the underlying normal distribution.
    - size: int. The number of samples to generate.

    Returns:
    - samples: ndarray. An array of samples from the log-normal distribution.
    """
    samples = np.random.lognormal(mu, sigma, size)
    return samples
