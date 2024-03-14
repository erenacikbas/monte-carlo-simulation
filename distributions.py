# Author: Eren Tuna Açıkbaş 2024

# Numpy is a library for numerical computing
import numpy as np


def get_parameter_distributions(n_simulations):
    """
    Retrieve parameter distributions for simulations.

    :param n_simulations: The number of simulations to generate distributions for.
    :return: A dictionary containing parameter distributions.
    """
    return {
        'area': np.random.normal(1000, 200, n_simulations),
        'thickness': np.random.normal(50, 10, n_simulations),
        'porosity': np.random.normal(0.3, 0.05, n_simulations),
        'water_sat': np.random.normal(0.2, 0.03, n_simulations),
        'fvf': np.random.normal(1.1, 0.1, n_simulations),
    }