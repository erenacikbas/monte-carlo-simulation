from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QGroupBox, QHBoxLayout, QSpinBox
)
from PyQt6.QtCore import Qt

from core.db.database import list_parameters, get_enabled_parameter


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

        # Iterations Setting
        iterations_group_box = QGroupBox(self.lang.get("iterations_configuration", "Iterations Configuration"))
        iterations_group_layout = QVBoxLayout(iterations_group_box)
        self.setup_iterations_configuration(iterations_group_layout)
        tab_layout.addWidget(iterations_group_box)
        tab_layout.addSpacing(10)  # Add some space between groups

        # Run Simulation Button with its own layout for proper alignment
        run_button_layout = QHBoxLayout()
        run_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        run_simulation_button = QPushButton(self.lang.get("run_simulation", "Run Simulation"))
        run_simulation_button.clicked.connect(self.run_simulation)  # Connect run_simulation method here
        run_button_layout.addWidget(run_simulation_button)

        run_button_layout.addStretch()  # Push the button to the left
        tab_layout.addLayout(run_button_layout)

        tab_layout.addStretch()  # Add a stretchable space only at the end (bottom)

    def setup_parameter_selection(self, layout):
        parameter_label = QLabel(self.lang.get("select_parameter", "Selected Parameter:"))
        parameter_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(parameter_label)

        self.parameter_var = QComboBox()
        # If there's an enabled parameter, add it to the dropdown and select it
        if self.enabled_parameter:
            self.parameter_var.addItem(self.enabled_parameter[1])  # Assuming [1] is the name
            # Displaying enabled parameter's fields
            for field_index, field_name in enumerate(
                    ["Name", "Iterations", "Area", "Thickness", "Porosity", "Water Saturation", "FVF"], start=1):
                # Assuming these field names map directly to indices in self.enabled_parameter, adjust if necessary
                # Skipping ID at index 0, adjust if your data structure is different
                if field_index < len(self.enabled_parameter) - 1:  # Exclude the enabled flag from display
                    field_value = self.enabled_parameter[field_index]
                    field_label = QLabel(f"{field_name}: {field_value}")
                    layout.addWidget(field_label)
        else:
            self.parameter_var.addItems([param[1] for param in self.enabled_parameter])
        layout.addWidget(self.parameter_var)

    def setup_iterations_configuration(self, layout):
        iterations_label = QLabel(self.lang.get("iterations_count", "Iterations Count:"))
        layout.addWidget(iterations_label)
        self.iterations_var = QSpinBox()
        self.iterations_var.setMinimum(1)  # Set minimum value for iterations
        self.iterations_var.setMaximum(1000000)  # Set maximum value for iterations
        layout.addWidget(self.iterations_var)

    def run_simulation(self):
        selected_parameter = self.parameter_var.currentText()
        selected_iterations = self.iterations_var.value()
        # Here you can perform the simulation with the selected parameter and number of iterations
        QMessageBox.information(None, "Simulation Started",
                                f"Simulation started for parameter: {selected_parameter}, "
                                f"with {selected_iterations} iterations.")
