from PyQt6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QHeaderView, QLineEdit, QPushButton, QErrorMessage,
    QTreeWidgetItemIterator, QAbstractItemView, QGridLayout
)
from core.db.database import activate_parameter, delete_parameter, insert_parameters, list_parameters
from core.gui.ribbons.param_actions import create_action_ribbon
from PyQt6.QtCore import Qt


class ParametersTab:
    def __init__(self, tab, config, lang):
        self.lang = lang
        self.config = config
        self.save_button = None
        self.pending_changes = []
        self.parameter_vars = {}
        self.config_table = None
        self.populate_parameters_tab(tab)

    def update_save_button_state(self):
        if self.pending_changes:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def refresh_parameters(self):
        """This method reloads parameters from the database and updates the TreeWidget."""
        self.load_parameters()

    def delete_parameters(self):
        selected_item = self.config_table.currentItem()
        if selected_item:
            config_id = int(selected_item.text(0))
            self.pending_changes.append(('delete', config_id))
            parent = selected_item.parent()
            if parent:
                parent.removeChild(selected_item)
            else:
                self.config_table.takeTopLevelItem(self.config_table.indexOfTopLevelItem(selected_item))

            # After modifying pending_changes, update the Save button state
            self.update_save_button_state()

    def activate_parameters(self):
        """This method activates the selected parameters."""
        selected_item = self.config_table.currentItem()
        if selected_item:
            selected_id = int(selected_item.text(0))  # Assuming the ID is in the first column
            activate_parameter(selected_id)  # Replace with your actual function to activate parameters
            print(f"Activated parameters ID: {selected_id}")
            self.load_parameters()  # Reload parameters to reflect changes

    def save_changes(self):
        print("Saving changes...")
        for action, config_id in self.pending_changes:
            if action == 'delete':
                delete_parameter(config_id)
            # Add handling for other actions ('add', 'update') as needed
        # Clear pending changes after committing
        self.pending_changes.clear()
        # Reload or update UI as necessary
        self.load_parameters()

    def populate_parameters_tab(self, tab):
        # Main layout for the entire tab
        main_layout = QVBoxLayout(tab)

        # Action Ribbon Section
        # Assuming create_action_ribbon properly adds itself to 'action_ribbon_frame'
        action_ribbon_frame = QFrame(tab)
        create_action_ribbon(self, action_ribbon_frame)
        main_layout.addWidget(action_ribbon_frame)

        # Configuration Listing Section
        self.setup_parameter_table(tab)
        # Note: setup_parameter_table should add the table directly to 'main_layout' now

        # New Parameter Form Section
        form_frame = QFrame(tab)
        form_layout = QVBoxLayout(form_frame)
        self.create_parameter_form(form_layout)

        # Apply New Configuration Button
        apply_button = QPushButton(self.lang.get("create_new_parameter", "Apply New Parameter"))
        apply_button.clicked.connect(self.apply_parameters)
        form_layout.addWidget(apply_button)

        main_layout.addWidget(form_frame)

    def create_parameter_form(self, parent_layout):
        parameters = {
            "Name": "Unique name for the parameter configuration",
            "Iterations": "Number of sim iterations",
            "Area": "Area covered by the sim",
            "Thickness": "Thickness of the material",
            "Porosity": "Porosity of the material",
            "Water Saturation": "Water saturation in the material",
            "FVF": "Formation Volume Factor"
        }

        grid_layout = QGridLayout()  # Use a QGridLayout

        row = 0
        for parameter, description in parameters.items():
            label = QLabel(f"{parameter}:")
            entry = QLineEdit()
            desc_label = QLabel(f"Description: {description}")  # Description label
            desc_label.setStyleSheet("QLabel { font-size: 8pt; color: gray; }")  # Smaller font size and gray color

            # Add widgets to the grid layout
            grid_layout.addWidget(label, row, 0)  # Parameter label in the first column
            grid_layout.addWidget(entry, row, 1)  # Entry field in the second column
            grid_layout.addWidget(desc_label, row + 1, 0, 1, 2)  # Description label spans both columns

            self.parameter_vars[parameter] = entry
            row += 2  # Increase row by 2 to make space for the next parameter

        parent_layout.addLayout(grid_layout)  # Add the grid layout to the parent layout

    def setup_parameter_table(self, parent):
        # Initialize the table as before but add it directly to the main layout
        self.config_table = QTreeWidget()
        self.config_table.setHeaderLabels(
            ['Name', 'Iterations', 'Area', 'Thickness', 'Porosity', 'Water Saturation', 'Created At', 'Updated At',
             'Enabled'])
        self.config_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.config_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.config_table.setAlternatingRowColors(True)

        # Add the table directly to the parent's layout, which is now 'main_layout'
        parent.layout().addWidget(self.config_table)

    def apply_parameters(self):
        if not all(self.parameter_vars[var].text().strip() for var in self.parameter_vars):
            error_dialog = QErrorMessage()
            error_dialog.showMessage("All fields are required.")
            return

        parameters = tuple(self.parameter_vars[var].text().strip() for var in self.parameter_vars)
        insert_parameters(parameters)
        self.load_parameters()  # Refresh the list to include the new parameters

    def load_parameters(self):
        self.config_table.clear()
        parameters = list_parameters()
        for config in parameters:
            # Assuming 'config' is a tuple like:
            # (id, name, enabled, iterations, area, thickness, porosity, water_saturation, fvf, created_at, updated_at)
            # Adjust the tuple indices according to your actual data structure
            display_values = config[:-1] + ('Yes' if config[-1] else 'No',)
            item = QTreeWidgetItem(map(str, display_values))
            if config[-1]:  # If the configuration is enabled, use the 'Enabled' tag
                item.setBackground(0, Qt.green)
            self.config_table.addTopLevelItem(item)
