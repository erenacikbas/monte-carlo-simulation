import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm, uniform, triang, beta


class DistributionPlotter:
    def __init__(self, parameters):
        """
        Initialize the DistributionPlotter with parameters for each characteristic.
        """
        self.parameters = parameters

    def plot_simulation_pdf(self, simulation_results, parameter_name):
        """
        Plot the probability density function (PDF) for simulation results of a given parameter.
        """
        data = np.array(simulation_results[parameter_name])
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=50, density=True, alpha=0.6, color='g', edgecolor='black')

        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        distribution, params = self.parameters[parameter_name]
        if distribution == 'normal':
            p = norm.pdf(x, np.mean(data), np.std(data))
        elif distribution == 'log-normal':
            scale = np.exp(params[0])
            p = lognorm.pdf(x, params[1], scale=scale)
        elif distribution == 'uniform':
            p = uniform.pdf(x, min(data), max(data) - min(data))
        elif distribution == 'triangular':
            c, loc, scale = params
            p = triang.pdf(x, c, loc=loc, scale=scale)
        elif distribution == 'beta':
            a, b, loc, scale = params
            p = beta.pdf(x, a, b, loc, scale)

        plt.plot(x, p, 'k', linewidth=2)
        title = f'Fit results: {parameter_name.capitalize()}'
        plt.title(title)
        plt.xlabel('Value')
        plt.ylabel('Density')
        plt.show()

    def plot_simulation_cdf(self, simulation_results, parameter_name):
        """
        Plot the cumulative distribution function (CDF) for simulation results of a given parameter.
        """
        data = np.array(simulation_results[parameter_name])
        data_sorted = np.sort(data)

        # Calculate CDF values
        cdf = np.arange(len(data_sorted)) / float(len(data_sorted) - 1)

        plt.figure(figsize=(10, 6))
        plt.plot(data_sorted, cdf, marker='.', linestyle='none')
        plt.title(f'Cumulative Distribution Function (CDF) of {parameter_name.capitalize()}')
        plt.xlabel(parameter_name.capitalize())
        plt.ylabel('CDF')
        plt.show()

    def run_monte_carlo_simulation(self, iterations=1000):
        """
        Run the Monte Carlo simulation using the specified distributions for a defined number of iterations.
        """
        results = {param: [] for param in self.parameters}

        for _ in range(iterations):
            for param, (distribution, distribution_params) in self.parameters.items():
                if distribution == 'uniform':
                    value = uniform.rvs(*distribution_params)
                elif distribution == 'triangular':
                    c, loc, scale = distribution_params
                    value = triang.rvs(c, loc=loc, scale=scale)
                elif distribution == 'normal':
                    value = norm.rvs(*distribution_params)
                elif distribution == 'log-normal':
                    scale = np.exp(distribution_params[0])
                    value = lognorm.rvs(distribution_params[1], scale=scale)
                elif distribution == 'beta':
                    a, b, loc, scale = distribution_params
                    value = beta.rvs(a, b, loc, scale)
                else:
                    continue  # Skip unsupported distributions

                results[param].append(value)

        return results
