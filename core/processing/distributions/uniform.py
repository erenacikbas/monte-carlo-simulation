# Uniform Distribution
import numpy as np


def generate_uniform_distribution(low, high, size):
    """
    Generate a uniform distribution.

    Parameters:
    - low: float. The lower boundary of the output interval. All values generated will be greater than or equal to low.
    - high: float. The upper boundary of the output interval. All values generated will be less than high.
    - size: int. The number of samples to generate.

    Returns:
    - samples: ndarray. An array of samples from the uniform distribution.
    """
    samples = np.random.uniform(low, high, size)
    return samples
