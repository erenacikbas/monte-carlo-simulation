# Triangular Distribution

import numpy as np


def generate_triangular_distribution(left, mode, right, size):
    """
    Generate a triangular distribution.

    Parameters:
    - left: float. The minimum value of the distribution.
    - mode: float. The peak value of the distribution.
    - right: float. The maximum value of the distribution.
    - size: int. The number of samples to generate.

    Returns:
    - samples: ndarray. An array of samples from the triangular distribution.
    """
    samples = np.random.triangular(left, mode, right, size)
    return samples
