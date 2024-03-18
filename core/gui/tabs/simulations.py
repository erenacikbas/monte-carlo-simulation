import numpy as np
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QGroupBox, QHBoxLayout, QSpinBox, QTabWidget, QWidget,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.db.database import get_enabled_parameter
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

        # Initialize tab_widget here for use in run_simulation
        self.tab_widget = QTabWidget()
        tab.layout().addWidget(self.tab_widget)  # Ensure the tab_widget is added to the layout

        # Example parameters setup for DistributionPlotter
        self.params = {
            'area': ('uniform', (0, 100)),
            'thickness': ('log-normal', (2.0, 0.5)),
            'porosity': ('normal', (0.16, 0.0254)),
            'water_saturation': ('uniform', (0, 1)),
            'fvf': ('normal', (1.0, 0.1))
        }

    def populate_enabled_parameter(self):
        self.enabled_parameter = get_enabled_parameter()  # Get the enabled parameter from the database

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

    def run_simulation(self):
        distribution_plotter = DistributionPlotter(self.params)
        simulation_results = distribution_plotter.run_monte_carlo_simulation(iterations=1000)

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
        ooip_pdf_fig, ooip_cdf_fig = monte_carlo_simulator.run_simulation(iterations=1000)

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

    def plot_parameter_pdf(self, data, parameter_name):
        # Calculate and plot PDF
        fig_pdf = Figure(figsize=(5, 4), dpi=100)
        ax_pdf = fig_pdf.add_subplot(111)
        ax_pdf.hist(data, bins=50, density=True, alpha=0.6, label='Histogram')
        ax_pdf.set_title(f"{parameter_name.capitalize()} PDF")
        ax_pdf.set_xlabel(parameter_name.capitalize())
        ax_pdf.set_ylabel('Probability Density')
        ax_pdf.legend()
        return fig_pdf

    def plot_parameter_cdf(self, data, parameter_name):
        # Calculate and plot CDF
        data_sorted = np.sort(data)
        cdf = np.arange(len(data)) / (len(data) - 1)
        fig_cdf = Figure(figsize=(5, 4), dpi=100)
        ax_cdf = fig_cdf.add_subplot(111)
        ax_cdf.plot(data_sorted, cdf, marker='.', linestyle='none', label='CDF')
        ax_cdf.set_title(f"{parameter_name.capitalize()} CDF")
        ax_cdf.set_xlabel(parameter_name.capitalize())
        ax_cdf.set_ylabel('Cumulative Probability')
        ax_cdf.legend()
        return fig_cdf
