# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.stats import norm, lognorm, uniform, triang, gaussian_kde


class MonteCarloSimulator:
    """
    The MonteCarloSimulator class is used to run Monte Carlo simulations using a DistributionPlotter instance.

    Attributes:
    - distribution_plotter (DistributionPlotter): The DistributionPlotter instance used for running the simulation.

    Methods:
    - __init__(self, distribution_plotter):
        Initialize the MonteCarloSimulator with a DistributionPlotter instance.

        Parameters:
            distribution_plotter (DistributionPlotter): The DistributionPlotter instance used for running the simulation.

    - run_simulation(self, iterations=1000):
        Run the Monte Carlo simulation using the DistributionPlotter instance.

        Parameters:
            iterations (int): Number of iterations to run the simulation (default = 1000).

        Returns:
            List[str]: A list of paths to the generated plot images.
    """
    def __init__(self, distribution_plotter):
        """
        Initialize the Monte Carlo Simulator with a DistributionPlotter instance.
        """
        self.distribution_plotter = distribution_plotter

    def run_simulation(self, iterations=1000):
        results = self.distribution_plotter.run_monte_carlo_simulation(iterations)

        ooip_results = 7758 * np.array(results['area']) * np.array(results['thickness']) * np.array(
            results['porosity']) * (1 - np.array(results['water_saturation'])) / np.array(results['fvf'])

        # Calculate the KDE for OOIP results to estimate the PDF
        ooip_density = gaussian_kde(ooip_results)
        ooip_vals = np.linspace(min(ooip_results), max(ooip_results), 1000)
        ooip_pdf = ooip_density(ooip_vals)

        # Calculate the CDF using the cumulative integral of the PDF
        ooip_cdf = np.cumsum(ooip_pdf)
        ooip_cdf = ooip_cdf / ooip_cdf[-1]  # Normalize to make the last value 1

        # Plotting OOIP PDF
        fig_pdf = Figure(figsize=(5, 4), dpi=100)
        plot_pdf = fig_pdf.add_subplot(1, 1, 1)
        plot_pdf.plot(ooip_vals, ooip_pdf, color='blue')
        plot_pdf.set_title("OOIP Distribution (PDF)")
        plot_pdf.set_xlabel("OOIP (bbl)")
        plot_pdf.set_ylabel("Density")

        # Plotting OOIP CDF
        fig_cdf = Figure(figsize=(5, 4), dpi=100)
        plot_cdf = fig_cdf.add_subplot(1, 1, 1)
        plot_cdf.plot(ooip_vals, ooip_cdf, color='red')
        plot_cdf.set_title("OOIP Distribution (CDF)")
        plot_cdf.set_xlabel("OOIP (bbl)")
        plot_cdf.set_ylabel("Cumulative Probability")

        # Optionally, display the plots if running in an interactive environment (commented out here)
        # plt.figure(figsize=(5, 4))
        # plt.plot(ooip_vals, ooip_pdf, color='blue', label='PDF')
        # plt.plot(ooip_vals, ooip_cdf, color='red', linestyle='--', label='CDF')
        # plt.title("OOIP Distributions")
        # plt.xlabel("OOIP (bbl)")
        # plt.ylabel("Density / Cumulative Probability")
        # plt.legend()
        # plt.show()

        return fig_pdf, fig_cdf