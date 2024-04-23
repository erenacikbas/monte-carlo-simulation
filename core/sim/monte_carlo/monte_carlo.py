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

        # Original Oil in Place (OOIP) and Recovery Oil in Place (ROIP) Calculations
        ooip_results = 7758 * np.array(results['Area']) * np.array(results['Thickness']) * np.array(
            results['Porosity']) * (1 - np.array(results['Water Saturation'])) / np.array(results['FVF'])
        roip_results = ooip_results * 0.2  # Applying 20% recovery factor

        # Convert results to MMbbl for plotting and analysis
        ooip_results_mm = ooip_results / 1e6
        roip_results_mm = roip_results / 1e6

        # KDE and CDF for OOIP
        ooip_density = gaussian_kde(ooip_results_mm)
        ooip_vals_mm = np.linspace(min(ooip_results_mm), max(ooip_results_mm), 500)
        ooip_pdf = ooip_density(ooip_vals_mm)
        ooip_cdf = np.cumsum(ooip_pdf) / np.sum(ooip_pdf)

        # KDE and CDF for ROIP
        roip_density = gaussian_kde(roip_results_mm)
        roip_vals_mm = np.linspace(min(roip_results_mm), max(roip_results_mm), 500)
        roip_pdf = roip_density(roip_vals_mm)
        roip_cdf = np.cumsum(roip_pdf) / np.sum(roip_pdf)

        # Create separate figures for each plot
        # OOIP PDF
        fig_ooip_pdf = Figure(figsize=(5, 4), dpi=100)
        ax_ooip_pdf = fig_ooip_pdf.add_subplot(111)
        ax_ooip_pdf.plot(ooip_vals_mm, ooip_pdf, color='blue')
        ax_ooip_pdf.set_title("OOIP Distribution (PDF)", fontsize=12, fontweight='bold')
        ax_ooip_pdf.set_xlabel("OOIP (MMbbl)")
        ax_ooip_pdf.set_ylabel("Density")

        # OOIP CDF
        # Calculate P10, P50, P90 in MMbbl
        fig_ooip_cdf = Figure(figsize=(5, 4), dpi=100)
        ax_ooip_cdf = fig_ooip_cdf.add_subplot(111, xlim=(0, max(ooip_vals_mm)), ylim=(0, 1.01))
        ax_ooip_cdf.plot(ooip_vals_mm, ooip_cdf, color='red')
        p10_value_mm = np.percentile(ooip_results_mm,
                                     90)  # Note: For consistency with oil industry conventions, using 90 for P10
        p50_value_mm = np.percentile(ooip_results_mm, 50)
        p90_value_mm = np.percentile(ooip_results_mm, 10)  # Note: And using 10 for P90

        # Mark P10, P50, P90 points on the plot and draw lines to the intersection with the CDF curve
        percentile_values_mm = [p10_value_mm, p50_value_mm, p90_value_mm]
        percentile_labels = ['P10', 'P50', 'P90']
        for value_mm, label in zip(percentile_values_mm, percentile_labels):
            y_value = np.interp(value_mm, ooip_vals_mm, ooip_cdf)
            ax_ooip_cdf.plot([value_mm, value_mm], [0, y_value], color='black', linestyle='--',
                             label=f'{label}: {value_mm:.2f} MMbbl')
            ax_ooip_cdf.scatter(value_mm, y_value, color='black', zorder=5)  # Add scatter point at the intersection
            ax_ooip_cdf.plot([0, value_mm], [y_value, y_value], color='black', linestyle='--')

        ax_ooip_cdf.set_title("OOIP Distribution (CDF)", fontsize=12, fontweight='bold')
        ax_ooip_cdf.set_xlabel("OOIP (MMbbl)")
        ax_ooip_cdf.set_ylabel("Cumulative Probability")
        ax_ooip_cdf.legend()

        # ROIP PDF
        fig_roip_pdf = Figure(figsize=(5, 4), dpi=100)
        ax_roip_pdf = fig_roip_pdf.add_subplot(111)
        ax_roip_pdf.plot(roip_vals_mm, roip_pdf, color='green')
        ax_roip_pdf.set_title("ROIP Distribution (PDF)", fontsize=12, fontweight='bold')
        ax_roip_pdf.set_xlabel("ROIP (MMbbl)")
        ax_roip_pdf.set_ylabel("Density")

        # ROIP CDF
        fig_roip_cdf = Figure(figsize=(5, 4), dpi=100)
        ax_roip_cdf = fig_roip_cdf.add_subplot(111, xlim=(0, max(roip_vals_mm)), ylim=(0, 1.01))
        ax_roip_cdf.plot(roip_vals_mm, roip_cdf, color='orange')
        p10_value_mm = np.percentile(roip_results_mm,
                                     90)  # Note: For consistency with oil industry conventions, using 90 for P10
        p50_value_mm = np.percentile(roip_results_mm, 50)
        p90_value_mm = np.percentile(roip_results_mm, 10)  # Note: And using 10 for P90

        # Mark P10, P50, P90 points on the plot and draw lines to the intersection with the CDF curve
        percentile_values_mm = [p10_value_mm, p50_value_mm, p90_value_mm]
        percentile_labels = ['P10', 'P50', 'P90']
        for value_mm, label in zip(percentile_values_mm, percentile_labels):
            y_value = np.interp(value_mm, roip_vals_mm, roip_cdf)
            x_value = np.interp(value_mm, roip_vals_mm, roip_pdf)
            ax_roip_cdf.plot([value_mm, value_mm], [0, y_value], color='black', linestyle='--',
                             label=f'{label}: {value_mm:.2f} MMbbl')
            ax_roip_cdf.scatter(value_mm, y_value, color='black', zorder=5)  # Add scatter point at the intersection
            ax_roip_cdf.plot([0, value_mm], [y_value, y_value], color='black', linestyle='--')
        ax_roip_cdf.set_title("ROIP Distribution (CDF)", fontsize=12, fontweight='bold')
        ax_roip_cdf.set_xlabel("ROIP (MMbbl)")
        ax_roip_cdf.set_ylabel("Cumulative Probability")
        ax_roip_cdf.legend()

        # Return the figures separately
        return fig_ooip_pdf, fig_ooip_cdf, fig_roip_pdf, fig_roip_cdf

