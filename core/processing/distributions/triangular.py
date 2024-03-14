# Triangular Distribution

import numpy as np

def get_parameter_distributions(n_simulations):
    """
    Retrieve parameter distributions for simulations.

    :param n_simulations: The number of simulations to generate distributions for.
    :return: A dictionary containing parameter distributions.
    """
    return {
        'area': np.random.triangular(900, 1000, 1100, n_simulations),
        'thickness': np.random.triangular(40, 50, 60, n_simulations),
        'porosity': np.random.triangular(0.25, 0.3, 0.35, n_simulations),
        'water_sat': np.random.triangular(0.15, 0.2, 0.25, n_simulations),
        'fvf': np.random.triangular(1.0, 1.1, 1.2, n_simulations),
    }