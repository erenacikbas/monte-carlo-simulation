from PyQt6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, QErrorMessage, QAbstractItemView,
    QGridLayout
)
from core.db.database import activate_parameter, delete_parameter, insert_parameters, list_parameters, \
    update_parameter_by_id
from core.gui.ribbons.param_actions import create_action_ribbon
from PyQt6.QtCore import Qt

from core.gui.widgets.centered_tree_item import CenteredTreeWidgetItem


class ParametersTab:
    def __init__(self, tab, config, lang):
        self.lang = lang
        self.config = config
        self.save_button = None
        self.pending_changes = []
        self.parameter_vars = {}
        self.parameters_table = None
        self.create_button = QPushButton(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.create_button.clicked.connect(self.create_or_update_parameter)
        self.current_id = None  # Initialize the current ID
        self.create_or_update_button = QPushButton(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.create_or_update_button.clicked.connect(self.create_or_update_parameter)
        self.original_values = {}  # Initialize original_values here

        self.populate_parameters_tab(tab)

    def update_save_button_state(self):
        if self.pending_changes:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def load_parameter_details(self, item, column):
        self.current_id = int(item.text(0))
        details = [item.text(i) for i in range(self.parameters_table.columnCount())]
        for i, key in enumerate(self.parameter_vars.keys()):
            self.parameter_vars[key].setText(details[i])
            self.original_values[key] = details[i]
        for i, (key, entry) in enumerate(self.parameter_vars.items()):
            entry.setText(details[i])
            self.original_values[key] = details[i]  # Store the original value

        self.create_or_update_button.setText(self.lang.get("update_parameter", "Update Parameter"))
        self.create_or_update_button.setEnabled(True)

    def refresh_parameters(self):
        """This method reloads parameters from the database and updates the TreeWidget."""
        # Clear the current selection and ID
        self.parameters_table.clearSelection()
        self.current_id = None
        # Reset the button to 'Create New Parameter'
        self.update_button_text()
        self.load_parameters()
        self.reset_form_and_id()  # Reset form and clear `current_id`

    def delete_parameters(self):
        selected_item = self.parameters_table.currentItem()
        if selected_item:
            config_id = int(selected_item.text(0))
            self.pending_changes.append(('delete', config_id))
            parent = selected_item.parent()
            if parent:
                parent.removeChild(selected_item)
            else:
                self.parameters_table.takeTopLevelItem(self.parameters_table.indexOfTopLevelItem(selected_item))

            # After modifying pending_changes, update the Save button state
            self.update_save_button_state()

    def activate_parameters(self):
        """This method activates the selected parameters."""
        selected_item = self.parameters_table.currentItem()
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
        self.load_parameters()  # Load and display the parameters

        # New Parameter Form Section
        form_frame = QFrame(tab)
        form_layout = QVBoxLayout(form_frame)
        self.create_parameter_form(form_layout)
        main_layout.addWidget(form_frame)

        # Enable Button
        self.enable_button = QPushButton(self.lang.get("enable_parameter", "Enable"))
        self.enable_button.clicked.connect(self.enable_selected_parameter)
        self.enable_button.setEnabled(False)  # Initially disabled until a parameter is selected
        main_layout.addWidget(self.enable_button)

        # Create or Update Parameter Button
        self.create_or_update_button = QPushButton(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.create_or_update_button.clicked.connect(self.create_or_update_parameter)
        main_layout.addWidget(self.create_or_update_button)  # Add the button to the main layout

    def enable_selected_parameter(self):
        if not self.current_id:
            print("No parameter selected.")
            return

        try:
            activate_parameter(self.current_id)  # Use your existing backend function
            self.refresh_parameters()  # Refresh the list to show the change
            self.enable_button.setEnabled(False)  # Re-enable the button
        except Exception as e:
            print(f"Error activating parameter: {e}")

    def load_selected_parameter(self):
        selected_item = self.parameters_table.currentItem()
        if selected_item:
            # Extract parameter details from the selected item
            # Assuming the details are in the correct order
            details = [selected_item.text(i) for i in range(self.parameters_table.columnCount())]
            # Populate the form fields
            # This assumes you have a dictionary of QLineEdit widgets in self.parameter_vars
            for i, key in enumerate(self.parameter_vars.keys()):
                self.parameter_vars[key].setText(details[i])
            # Change button text to indicate loading is possible instead of creation
            self.load_param_button.setText(self.lang.get("load_parameter", "Load Parameter"))

    def create_parameter_form(self, parent_layout):
        # Define your parameters here. Assume "Id" is for display only and should not be editable.
        parameters = {
            "Id": "Unique ID for the parameter configuration",
            "Name": "Unique name for the parameter configuration",
            "Iterations": "Number of sim iterations",
            "Area": "Area covered by the sim",
            "Thickness": "Thickness of the material",
            "Porosity": "Porosity of the material",
            "Water Saturation": "Water saturation in the material",
            "FVF": "Formation Volume Factor"
        }

        # Initialize the grid layout for form fields
        grid_layout = QGridLayout()

        row = 0
        for parameter, description in parameters.items():
            label = QLabel(f"{parameter}:")
            grid_layout.addWidget(label, row, 0)  # Add the label to the grid layout

            if parameter == "Id":
                # For the "Id" field, use a QLineEdit but set it as read-only
                value_display = QLineEdit()
                value_display.setReadOnly(True)
                value_display.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")  # Optional styling to indicate non-editability
            else:
                # For all other parameters, use a regular QLineEdit
                value_display = QLineEdit()

            self.parameter_vars[parameter] = value_display  # Store the QLineEdit (or QLabel) for later use
            grid_layout.addWidget(value_display, row, 1)  # Add the QLineEdit to the grid layout

            # Optionally, add a description label below each input for clarity
            desc_label = QLabel(f"Description: {description}")
            desc_label.setStyleSheet("QLabel { font-size: 8pt; color: gray; }")
            grid_layout.addWidget(desc_label, row + 1, 0, 1, 2)  # Span the description label across both columns

            row += 2  # Increment the row. Skip an extra row for the description.

        # Add the complete grid layout to the parent layout of the form
        parent_layout.addLayout(grid_layout)

    def setup_parameter_table(self, parent):
        # Initialize the table as before but add it directly to the main layout
        self.apply_button = QPushButton(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.parameters_table = QTreeWidget()
        self.parameters_table.setIndentation(0)  # This sets the indentation to 0 pixels
        self.parameters_table.setHeaderLabels(
            ['Id', 'Name', 'Iterations', 'Area', 'Thickness', 'Porosity', 'Water Saturation', 'Formation Volume Factor',
             'Created At',
             'Updated At',
             'Enabled'])
        self.parameters_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.parameters_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.parameters_table.setAlternatingRowColors(True)
        self.parameters_table.itemDoubleClicked.connect(self.load_parameter_details)
        self.parameters_table.itemDoubleClicked.connect(self.update_button_text)

        # Add the table directly to the parent's layout, which is now 'main_layout'
        parent.layout().addWidget(self.parameters_table)

    def reset_form_and_id(self):
        self.current_id = None
        for key in self.parameter_vars:
            self.parameter_vars[key].setText("")
        self.create_or_update_button.setText(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.create_or_update_button.setEnabled(True)

    def load_parameter_details(self, item, column):
        # Assuming the first column contains the unique ID
        self.current_id = int(item.text(0))
        self.parameter_vars["Id"].setText(str(self.current_id))  # Works for both QLabel and QLineEdit
        # Assuming the 'enabled' status is in the last column
        is_enabled = item.text(self.parameters_table.columnCount() - 1)

        # Populate the form fields with details
        details = [item.text(i) for i in range(self.parameters_table.columnCount())]
        for i, key in enumerate(self.parameter_vars.keys()):
            self.parameter_vars[key].setText(details[i])

        # Change the text of the button to "Update"
        self.create_or_update_button.setText(self.lang.get("update_parameter", "Update Parameter"))
        self.create_or_update_button.setEnabled(True)

        # Enable or disable the "Enable" button based on the 'enabled' status of the parameter
        if is_enabled == '1' or is_enabled.lower() == 'yes':  # Adjust the condition based on your data
            self.enable_button.setEnabled(False)
        else:
            self.enable_button.setEnabled(True)

    def create_or_update_parameter(self):
        # Check if it's a create or update action based on the button text
        if self.create_or_update_button.text() == self.lang.get("create_new_parameter", "Create New Parameter"):
            print("I'm here")
            self.apply_parameters()
        else:
            self.update_parameter()

    def update_parameter(self):
        if not self.current_id:
            print("No parameter selected for update.")
            return

        new_values = {}
        for key, var in self.parameter_vars.items():
            current_value = var.text().strip()  # Ensure text is trimmed
            original_value = str(self.original_values.get(key, "")).strip()  # Convert to string and trim
            if original_value != current_value:
                new_values[key] = current_value

        if not new_values:
            print("No changes detected.")
            return

        try:
            update_parameter_by_id(self.current_id, new_values)
            self.refresh_parameters()
        except Exception as e:
            print(f"Error updating parameter: {e}")

    def reset_form(self):
        for var in self.parameter_vars.values():
            var.setText("")

    def reset_creation_form(self):
        # Clear form fields
        for key in self.parameter_vars:
            self.parameter_vars[key].setText("")
        # Reset button text and disable it
        self.create_or_update_button.setText(self.lang.get("create_new_parameter", "Create New Parameter"))
        # Optionally disable the button until a new selection is made or a new creation starts
        self.create_or_update_button.setEnabled(False)
        # Clear current ID to indicate no selection
        self.current_id = None

    def update_button_text(self):
        selected_item = self.parameters_table.currentItem()
        if selected_item:
            # Change to "Update Parameter" if an item is selected
            self.create_or_update_button.setText(self.lang.get("update_parameter", "Update Parameter"))
            self.create_or_update_button.setEnabled(True)
        else:
            # Revert to "Create New Parameter" if no selection
            self.create_or_update_button.setText(self.lang.get("create_new_parameter", "Create New Parameter"))
            self.create_or_update_button.setEnabled(False)  # Optionally disable if no selection

    def apply_parameters(self):
        if not all(self.parameter_vars[var].text().strip() for var in self.parameter_vars):
            error_dialog = QErrorMessage()
            error_dialog.showMessage("All fields are required.")
            return

        parameters = tuple(self.parameter_vars[var].text().strip() for var in self.parameter_vars)
        print("New parameters:", parameters)  # Add this line to check if parameters are correctly retrieved
        insert_parameters(parameters)
        self.load_parameters()  # Refresh the list to include the new parameters

    def load_parameters(self):
        self.parameters_table.clear()
        parameters = list_parameters()
        print(parameters)
        for config in parameters:
            # Assuming 'config' is a tuple like:
            # (id, name, enabled, iterations, area, thickness, porosity, water_saturation, fvf, created_at, updated_at)
            # Adjust the tuple indices according to your actual data structure
            display_values = config[:-1] + ('Yes' if config[-1] else 'No',)
            item = CenteredTreeWidgetItem(list(map(str, display_values)))
            self.parameters_table.addTopLevelItem(item)

        self.adjust_column_widths()  # Adjust column widths after loading

        # Connect signals to dynamically adjust column widths
        self.parameters_table.itemExpanded.connect(self.adjust_column_widths)
        self.parameters_table.itemCollapsed.connect(self.adjust_column_widths)

    def adjust_column_widths(self):
        max_width = 200  # Set your desired maximum width for any column
        for column in range(self.parameters_table.columnCount()):
            self.parameters_table.resizeColumnToContents(column)
            if self.parameters_table.columnWidth(column) > max_width:
                self.parameters_table.setColumnWidth(column, max_width)
