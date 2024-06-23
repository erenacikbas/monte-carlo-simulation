import numpy as np
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QGroupBox, QHBoxLayout, QSpinBox, QTabWidget, QWidget,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde

from core.db.database import get_enabled_parameter, get_enabled_parameter_and_distributions
from core.sim.monte_carlo.monte_carlo import MonteCarloSimulator
from core.processing.processing import DistributionPlotter


class SimulationsTab:
    def __init__(self, context, tab):
        self.parameter_var = QComboBox()
        self.enabled_parameter = ""
        self.context = context
        self.config = self.context.config
        self.lang = self.context.lang
        self.populate_enabled_parameter()
        # Populate the simulations tab
        self.populate_simulations_tab(tab)
        self.bins = 50
        # Iterations
        self.iterations = 0

        # Initialize tab_widget here for use in run_simulation
        self.tab_widget = QTabWidget()
        tab.layout().addWidget(self.tab_widget)  # Ensure the tab_widget is added to the layout

        # Get the enabled parameter and its distributions
        enabled_parameter, distributions = get_enabled_parameter_and_distributions()

        # Map the distributions to the expected format for self.params
        #if enabled_parameter:
        #    self.params = self.map_distributions_to_params(distributions)

        # Example parameters setup for DistributionPlotter
        # self.params = {
        #     'area': ('uniform', (0, 1000000)),
        #     'thickness': ('normal', (27.6, 8.29)),
        #     'porosity': ('normal', (0.16, 0.0254)),
        #     'water_saturation': ('uniform', (0, 1)),
        #     'fvf': ('normal', (1.0, 0.1))
        # }

    def populate_enabled_parameter(self):
        self.enabled_parameter = get_enabled_parameter()  # Get the enabled parameter from the database
        print(self.enabled_parameter)
        if len(self.enabled_parameter)>0 is not None:
            self.iterations = self.enabled_parameter[2]  # Assuming [2] is the iterations column
            print("Iterations: ", self.iterations)

    def refresh_parameters(self):
        self.parameter_var.clear()
        self.populate_enabled_parameter()
        if self.enabled_parameter:
            self.parameter_var.addItem(self.enabled_parameter[1])  # Assuming [1] is the name

    def populate_simulations_tab(self, tab):
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)  # Provide padding around the layout

        # Parameter Selection Group
        parameter_group_box = QGroupBox(self.lang.get("parameter_selection", "Parameter Selection"))
        parameter_group_layout = QVBoxLayout(parameter_group_box)
        self.setup_parameter_selection(parameter_group_layout)
        tab_layout.addWidget(parameter_group_box)
        tab_layout.addSpacing(10)  # Add some space between groups

        # Run Simulation Button with its own layout for proper alignment
        run_simulation_button = QPushButton(self.lang.get("run_simulation", "Run Simulation"))
        run_simulation_button.clicked.connect(self.run_simulation)  # Connect run_simulation method here
        tab_layout.addWidget(run_simulation_button)
        run_simulation_button.setStyleSheet("width: 100%")

    def setup_parameter_selection(self, layout):
        parameter_label = QLabel(self.lang.get("select_parameter", "Selected Parameter:"))
        parameter_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(parameter_label)

        self.parameter_var = QComboBox()
        # Ensure self.enabled_parameter is iterable
        enabled_parameters = self.enabled_parameter if self.enabled_parameter else []
        if enabled_parameters:
            self.parameter_var.addItem(enabled_parameters[1])

        layout.addWidget(self.parameter_var)

    def fetch_and_map_distributions(self):
        # Get the enabled parameter and its distributions
        enabled_parameter, distributions = get_enabled_parameter_and_distributions()

        # Check if an enabled parameter was found and has distributions
        if enabled_parameter and distributions:
            self.params = self.map_distributions_to_params(distributions)
            print(self.params)
        else:
            self.params = {}  # Fallback if no enabled parameter or distributions

    def map_distributions_to_params(self, distributions):
        print("Distributions: ", distributions)
        params = {}
        for dist in distributions:
            param_name = dist[0]  # Assuming the third column in the database is the parameter_name
            dist_type = dist[1].lower()  # Assuming the fourth column in the database is the distribution_type
            mean = dist[2]
            std_dev = dist[3]
            min_val = dist[4]
            max_val = dist[5]
            mode_val = dist[6]  # This may not be used for all distributions

            if dist_type == 'normal':
                params[param_name] = ('normal', (mean, std_dev))
            elif dist_type == 'log-normal':
                # If your log-normal is parameterized differently, adjust the following line accordingly
                params[param_name] = ('log-normal', (np.log(mean), std_dev))
            elif dist_type == 'uniform':
                # Uniform distribution in scipy.stats takes loc and scale parameters
                # loc is the lower bound, and scale is the width of the distribution
                params[param_name] = ('uniform', (min_val, max_val - min_val))
            elif dist_type == 'triangular':
                # For triangular distribution, c is the mode expressed as a fraction of the total range
                c = (mode_val - min_val) / (max_val - min_val)
                params[param_name] = ('triangular', (c, min_val, max_val - min_val))
            elif dist_type == 'beta':
                # Ensure your mean and std_dev are for data scaled to [0, 1]
                alpha = mean * ((mean * (1 - mean) / std_dev ** 2) - 1)
                beta = (1 - mean) * ((mean * (1 - mean) / std_dev ** 2) - 1)
                params[param_name] = ('beta', (alpha, beta, 0, 1))

            # ... handle other distribution types if any ...
        return params

    def run_simulation(self):
        self.fetch_and_map_distributions()
        distribution_plotter = DistributionPlotter(self.params)
        simulation_results = distribution_plotter.run_monte_carlo_simulation(iterations=self.iterations)

        self.tab_widget.clear()  # Clear existing content

        # Setup containers and layouts for PDF and CDF plots within scroll areas
        pdf_scroll_area = QScrollArea()
        cdf_scroll_area = QScrollArea()
        pdf_container = QWidget()
        cdf_container = QWidget()
        pdf_grid_layout = QGridLayout()
        cdf_grid_layout = QGridLayout()
        pdf_container.setLayout(pdf_grid_layout)
        cdf_container.setLayout(cdf_grid_layout)
        pdf_scroll_area.setWidget(pdf_container)
        pdf_scroll_area.setWidgetResizable(True)
        cdf_scroll_area.setWidget(cdf_container)
        cdf_scroll_area.setWidgetResizable(True)

        # Determine the grid placement
        row, col = 0, 0
        max_plots_per_row = 2

        for parameter_name, data in simulation_results.items():
            # Generate and plot PDF for the current parameter
            fig_pdf = self.plot_parameter_pdf(data, parameter_name)
            canvas_pdf = FigureCanvas(fig_pdf)
            pdf_grid_layout.addWidget(canvas_pdf, row, col)

            # Generate and plot CDF for the current parameter
            fig_cdf = self.plot_parameter_cdf(data, parameter_name)
            canvas_cdf = FigureCanvas(fig_cdf)
            cdf_grid_layout.addWidget(canvas_cdf, row, col)

            # Update grid position
            col += 1
            if col >= max_plots_per_row:
                col = 0
                row += 1

        # Add scroll areas (containing the PDF and CDF plots) to the main tab widget
        self.tab_widget.addTab(pdf_scroll_area, "PDF Plots")
        self.tab_widget.addTab(cdf_scroll_area, "CDF Plots")

        # Generate OOIP values from simulation results and plot OOIP PDF and CDF
        monte_carlo_simulator = MonteCarloSimulator(distribution_plotter)
        ooip_pdf_fig, ooip_cdf_fig, roip_pdf_fig, roip_cdf_fig = monte_carlo_simulator.run_simulation(iterations=self.iterations)

        canvas_pdf = FigureCanvas(ooip_pdf_fig)
        tab_pdf = QWidget()
        layout_pdf = QVBoxLayout(tab_pdf)
        layout_pdf.addWidget(canvas_pdf)
        self.tab_widget.addTab(tab_pdf, "OOIP PDF")

        # Create and add a canvas for the CDF figure
        canvas_cdf = FigureCanvas(ooip_cdf_fig)
        tab_cdf = QWidget()
        layout_cdf = QVBoxLayout(tab_cdf)
        layout_cdf.addWidget(canvas_cdf)
        self.tab_widget.addTab(tab_cdf, "OOIP CDF")

        canvas_pdf = FigureCanvas(roip_pdf_fig)
        tab_pdf = QWidget()
        layout_pdf = QVBoxLayout(tab_pdf)
        layout_pdf.addWidget(canvas_pdf)
        self.tab_widget.addTab(tab_pdf, "ROIP PDF")

        # Create and add a canvas for the CDF figure
        canvas_cdf = FigureCanvas(roip_cdf_fig)
        tab_cdf = QWidget()
        layout_cdf = QVBoxLayout(tab_cdf)
        layout_cdf.addWidget(canvas_cdf)
        self.tab_widget.addTab(tab_cdf, "ROIP CDF")

        # Inside your run_simulation method, adjust the savefig calls like so:
        ooip_pdf_fig.savefig(f"results/ooip_pdf_{self.iterations}.png", dpi=300, format='png')  # High resolution
        ooip_cdf_fig.savefig(f"results/ooip_{self.iterations}.png", dpi=300, format='png')  # High resolution
        roip_pdf_fig.savefig(f"results/roip_{self.iterations}.png", dpi=300, format='png')  # High resolution
        roip_cdf_fig.savefig(f"results/roip_cdf_{self.iterations}.png", dpi=300, format='png')  # High resolution

        # Alternatively, for vector graphics which are resolution-independent, you can use SVG
        ooip_pdf_fig.savefig(f"results/ooip_pdf_{self.iterations}.svg", format='svg')  # Vector graphic
        ooip_cdf_fig.savefig(f"results/ooip_cdf_{self.iterations}.svg", format='svg')  # Vector graphic
        roip_pdf_fig.savefig(f"results/roip_pdf_{self.iterations}.svg", format='svg')  # Vector graphic
        roip_cdf_fig.savefig(f"results/roip_cdf_{self.iterations}.svg", format='svg')  # Vector graphic

    def plot_parameter_pdf(self, data, parameter_name):
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        # Adjust subplot parameters for better layout
        fig.subplots_adjust(left=.2, right=0.95, top=0.85, bottom=0.25)

        # Generate histogram data
        counts, bins, patches = ax.hist(data, bins=self.bins, density=True, alpha=0.6, label='Histogram', color='g', edgecolor='black')

        # Alternatively, you can add a KDE line plot
        kde = gaussian_kde(data)
        kde_x = np.linspace(bins[0], bins[-1], self.bins)
        kde_y = kde(kde_x)
        ax.plot(kde_x, kde_y, c='darkorange', label='KDE')

        ax.set_title(f"{parameter_name.capitalize()} PDF", fontsize=8)
        ax.set_xlabel('Value', fontsize=8)
        ax.set_ylabel('Probability Density', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.legend(fontsize=8)
        fig.savefig(f"results/{parameter_name}_pdf_{self.iterations}.png", dpi=300, format='svg')
        return fig

    def plot_parameter_cdf(self, data, parameter_name):
        # Calculate and plot CDF
        data_sorted = np.sort(data)
        cdf = np.arange(len(data)) / (len(data) - 1)
        fig_cdf = Figure(figsize=(6, 5), dpi=100)
        ax_cdf = fig_cdf.add_subplot(111)
        fig_cdf.subplots_adjust(left=.2, right=0.95, top=0.85, bottom=0.25)
        ax_cdf.plot(data_sorted, cdf, marker='.', linestyle='', label='CDF')
        ax_cdf.set_title(f"{parameter_name.capitalize()} CDF", fontsize=8)
        ax_cdf.set_xlabel(parameter_name.capitalize(), fontsize=8)
        ax_cdf.set_ylabel('Cumulative Probability', fontsize=8)
        ax_cdf.tick_params(axis='both', which='major', labelsize=8)
        ax_cdf.legend()
        fig_cdf.savefig(f"results/{parameter_name}_cdf_{self.iterations}.png", dpi=300, format='svg')
        return fig_cdf
