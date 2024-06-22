from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, QErrorMessage, QAbstractItemView,
    QGridLayout, QGroupBox, QHBoxLayout
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

        # Initialize UI state
        self.initializeUI()

    def initializeUI(self):
        # Initially hide the ID field
        if "Id" in self.parameter_vars:
            self.parameter_vars["Id"].setVisible(False)

    def update_save_button_state(self):
        if self.pending_changes:
            self.save_button.setEnabled(True)
        else:
            self.save_button.setEnabled(False)

    def load_parameter_details(self, item, column):
        # When loading details for updating, make ID visible but read-only
        self.current_id = int(item.text(0))
        if "Id" in self.parameter_vars:
            self.parameter_vars["Id"].setVisible(True)
            self.parameter_vars["Id"].setReadOnly(True)
            self.parameter_vars["Id"].setStyleSheet("background-color: #e0e0e0;")
            self.parameter_vars["Id"].setText(str(self.current_id))

        # Clear previous values
        for key in self.parameter_vars.keys():
            self.parameter_vars[key].setText("")

        # Load new values from selected item
        for i, key in enumerate(
                ["Id", "Name", "Iterations", "Volume", "Net To Gross Ratio", "Porosity", "Water Saturation", "FVF"]):
            value = item.text(i) if i < item.columnCount() else ""
            if key in self.parameter_vars:
                self.parameter_vars[key].setText(value)
                self.original_values[key] = value

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
        # Parameters with descriptions
        parameter_descriptions = {
            "Id": "This reference will be auto-generated",
            "Name": "Unique name for the parameter configuration",
            "Iterations": "Number of simulation iterations",
            "Volume": "Volume covered by the simulation",
            "Net To Gross Ratio": "Net Pay to Gross thickness ratio",
            "Porosity": "Porosity of the material",
            "Water Saturation": "Water saturation in the material",
            "FVF": "Formation Volume Factor"
        }

        if "Id" in self.parameter_vars:
            self.parameter_vars["Id"].setReadOnly(True)  # Make ID field read-only

        # Convert the parameter_descriptions dict into a list of tuples for easier grouping
        parameters_list = list(parameter_descriptions.items())

        # Create rows with two parameters each
        for i in range(0, len(parameters_list), 2):
            # Create a horizontal layout for each row
            row_layout = QHBoxLayout()

            if "Id" in self.parameter_vars:
                self.parameter_vars["Id"].setReadOnly(True)  # Make ID field read-only

            # Initialize a variable to keep track of the number of group boxes added to the row
            groupBoxCount = 0

            # Process two parameters at a time, creating a group box for each
            for j in range(2):
                if i + j < len(parameters_list):
                    parameter, description = parameters_list[i + j]
                    parameter_group_box = self.create_parameter_group_box(parameter, description)
                    row_layout.addWidget(parameter_group_box, 1)  # Add group box with a stretch factor of 1
                    groupBoxCount += 1

            # Ensure that if only one group box is added, it still occupies half the width
            if groupBoxCount == 1:
                row_layout.addStretch(1)  # Add a stretchable space with the same factor to balance the layout

            # Add the row layout to the parent layout
            parent_layout.addLayout(row_layout)

    def create_parameter_group_box(self, parameter, description):
        # Create a group box for the parameter
        parameter_group_box = QGroupBox(f"{parameter}")
        parameter_group_box.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # Larger font for titles

        parameter_group_layout = QGridLayout(parameter_group_box)

        # Parameter Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)  # Enable word wrap for longer descriptions
        desc_label.setFont(QFont("Arial", 10))  # Smaller font for descriptions
        desc_label.setStyleSheet("color: #686868;")  # Greyed out appearance
        parameter_group_layout.addWidget(desc_label, 0, 0, 1, 2)  # Span two columns for description

        if parameter in ["FVF"]:
            # Fields for min and max values
            min_edit = QLineEdit()
            min_edit.setPlaceholderText("Min")
            max_edit = QLineEdit()
            max_edit.setPlaceholderText("Max")
            parameter_group_layout.addWidget(min_edit, 1, 0)
            parameter_group_layout.addWidget(max_edit, 1, 1)
            self.parameter_vars[f"{parameter}_Min"] = min_edit
            self.parameter_vars[f"{parameter}_Max"] = max_edit

        elif parameter in ["Porosity", "Water Saturation"]:
            # Fields for mean and std deviation
            mean_edit = QLineEdit()
            mean_edit.setPlaceholderText("Mean")
            std_dev_edit = QLineEdit()
            std_dev_edit.setPlaceholderText("Std Dev")
            parameter_group_layout.addWidget(mean_edit, 1, 0)
            parameter_group_layout.addWidget(std_dev_edit, 1, 1)
            self.parameter_vars[f"{parameter}_Mean"] = mean_edit
            self.parameter_vars[f"{parameter}_Std_dev"] = std_dev_edit

        elif parameter in ["Area", "Thickness"]:
            # Fields for min, mode, and max values
            min_edit = QLineEdit()
            min_edit.setPlaceholderText("Min")
            mode_edit = QLineEdit()
            mode_edit.setPlaceholderText("Mode")
            max_edit = QLineEdit()
            max_edit.setPlaceholderText("Max")
            parameter_group_layout.addWidget(min_edit, 1, 0)
            parameter_group_layout.addWidget(mode_edit, 1, 1)
            parameter_group_layout.addWidget(max_edit, 1, 2)
            self.parameter_vars[f"{parameter}_Min"] = min_edit
            self.parameter_vars[f"{parameter}_Mode"] = mode_edit
            self.parameter_vars[f"{parameter}_Max"] = max_edit

        else:
            # Single field for Name and Iterations
            value_edit = QLineEdit()
            value_edit.setPlaceholderText(description)
            parameter_group_layout.addWidget(value_edit, 1, 0, 1, 2)  # Span two columns for single fields
            self.parameter_vars[parameter] = value_edit

        return parameter_group_box

    def create_distribution_input_section(self, grid_layout, parameter_name, start_row):
        # Section label
        section_label = QLabel(f"{parameter_name} Distribution")
        section_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grid_layout.addWidget(section_label, start_row, 0, 1, 2)  # Span 2 columns

        # Distribution types
        dist_types = ["Normal", "Log-normal", "Triangular", "Uniform"]

        # For each distribution type, add a row of inputs
        for i, dist_type in enumerate(dist_types, start=1):
            # Distribution type label
            row = start_row + i
            type_label = QLabel(f"{dist_type}:")
            grid_layout.addWidget(type_label, row, 0)

            # Add input fields for distribution parameters
            param_names = self.get_param_names_for_distribution(dist_type)
            for j, param_name in enumerate(param_names, start=1):
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(param_name)
                grid_layout.addWidget(line_edit, row, j)
                self.parameter_vars[f"{parameter_name}_{dist_type}_{param_name}"] = line_edit

    def get_param_names_for_distribution(self, dist_type):
        # Returns the names of parameters based on distribution type
        if dist_type == "Normal" or dist_type == "Log-normal":
            return ["Mean", "Std Dev"]
        elif dist_type == "Triangular":
            return ["Min", "Mode", "Max"]
        elif dist_type == "Uniform":
            return ["Min", "Max"]
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")

    def setup_parameter_table(self, parent):
        # Initialize the table as before but add it directly to the main layout
        self.apply_button = QPushButton(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.parameters_table = QTreeWidget()
        self.parameters_table.setIndentation(0)  # This sets the indentation to 0 pixels
        self.parameters_table.setHeaderLabels([
            'ID', 'Name', 'Iterations', 'Enabled', 'Created At', 'Updated At'
            # 'Parameter Name', 'Distribution Type',
            # 'Mean', 'Std Dev', 'Min', 'Max', 'Mode', 'Created At', 'Updated At'
        ])
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
            if key == "Id":
                self.parameter_vars[key].setVisible(False)  # Hide the ID field
            else:
                self.parameter_vars[key].setVisible(True)  # Show all other fields
        self.create_or_update_button.setText(self.lang.get("create_new_parameter", "Create New Parameter"))
        self.create_or_update_button.setEnabled(True)

    def load_parameter_details(self, item, column):
        self.current_id = int(item.text(0))
        for key in self.parameter_vars:
            if key == "Id":
                self.parameter_vars[key].setText(str(self.current_id))
                self.parameter_vars[key].setVisible(True)  # Make the ID field visible and read-only
                self.parameter_vars[key].setReadOnly(True)
                self.parameter_vars[key].setStyleSheet("QLineEdit { background-color: #e0e0e0; color: #a0a0a0; }")
            else:
                self.parameter_vars[key].setText("")  # Clear the text for other fields or set them as needed

        self.create_or_update_button.setText(self.lang.get("update_parameter", "Update Parameter"))
        self.create_or_update_button.setEnabled(True)

    def create_or_update_parameter(self):
        # Check if it's a create or update action based on the button text
        if self.create_or_update_button.text() == self.lang.get("create_new_parameter", "Create New Parameter"):
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

    def collect_and_validate_input(self):
        # Collect basic parameter data
        name = self.parameter_vars["Name"].text().strip()
        iterations = self.parameter_vars["Iterations"].text().strip()

        distributions_for_parameters = {
            "Area": ["Uniform"],
            "Thickness": ["Triangular"],
            "Porosity": ["Normal"],
            "Water Saturation": ["Normal"],
            "FVF": ["Uniform"]
        }

        # Validate basic parameter data
        if not name or not iterations.isdigit():
            QErrorMessage().showMessage("Name and Iterations are required, and Iterations must be numeric.")
            return None

        print("parameter_vars", self.parameter_vars)

        # Initialize parameter object with basic data and empty distributions list
        parameter_data = {
            "Name": name,
            "Iterations": int(iterations),
            "Distributions": []
        }

        # Example: Collect and validate distribution data for 'Area'
        # area_data = self.collect_distribution_data("Area")
        for parameter_name, distribution_types in distributions_for_parameters.items():
            if f"{parameter_name}_Min" or f"{parameter_name}_Std_dev" or f"{parameter_name}_Mode" in self.parameter_vars:
                for dist_type in distribution_types:
                    print(f"Processing distribution type: {dist_type}")
                    data = self.collect_distribution_data(parameter_name, dist_type)
                    print("Data:", data)
                    if data:
                        print("Adding distribution data:", data)
                        parameter_data["Distributions"].append(data)
                    else:
                        QErrorMessage().showMessage(f"Invalid distribution data for {parameter_name} ({dist_type}).")
                        return None
        # if area_data:
        #     parameter_data["distributions"].append(area_data)
        #     # Add parameter name
        #     parameter_data["distributions"][0]["parameter_name"] = "Area"
        #     # Add distribution type
        #     parameter_data["distributions"][0]["distribution_type"] = "Uniform"
        # else:
        #     QErrorMessage().showMessage("Invalid distribution data for Area.")
        #     return None
        #
        # thickness_data = self.collect_distribution_data("Thickness")
        # if thickness_data:
        #     parameter_data["distributions"].append(thickness_data)
        # else:
        #     QErrorMessage().showMessage("Invalid distribution data for Thickness.")
        #     return None
        #
        # porosity_data = self.collect_distribution_data("Porosity")
        # if porosity_data:
        #     parameter_data["distributions"].append(porosity_data)
        # else:
        #     QErrorMessage().showMessage("Invalid distribution data for Porosity.")
        #     return None
        #
        # water_saturation_data = self.collect_distribution_data("Water Saturation")
        # if water_saturation_data:
        #     parameter_data["distributions"].append(water_saturation_data)
        # else:
        #     QErrorMessage().showMessage("Invalid distribution data for Water Saturation.")
        #     return None
        #
        # fvf_data = self.collect_distribution_data("FVF")
        # if fvf_data:
        #     parameter_data["distributions"].append(fvf_data)
        # else:
        #     QErrorMessage().showMessage("Invalid distribution data for FVF.")
        #     return None

        # Repeat the above for other distributions as needed

        return parameter_data

    def collect_distribution_data(self, parameter_name, distribution_type):
        # Initialize all variables to None at the start
        min_value = None
        max_value = None
        std_value = None
        mean_value = None
        mode_value = None

        # Conditional assignments based on distribution type
        if distribution_type == "Flexible" or distribution_type == "Uniform":
            min_value = self.parameter_vars[f"{parameter_name}_Min"].text().strip()
            max_value = self.parameter_vars[f"{parameter_name}_Max"].text().strip()
        elif distribution_type == "Normal" or distribution_type == "Log-normal":
            mean_value = self.parameter_vars[f"{parameter_name}_Mean"].text().strip()
            std_value = self.parameter_vars[f"{parameter_name}_Std_dev"].text().strip()
        elif distribution_type == "Triangular":
            min_value = self.parameter_vars[f"{parameter_name}_Min"].text().strip()
            mode_value = self.parameter_vars[f"{parameter_name}_Mode"].text().strip()
            max_value = self.parameter_vars[f"{parameter_name}_Max"].text().strip()

        # Return a dictionary with the collected values, using conditional expressions to include relevant ones
        return {
            "Parameter_name": parameter_name,
            "Distribution_type": distribution_type,
            "Min_value": min_value,
            "Max_value": max_value,
            "Std_dev": std_value,
            "Mean": mean_value,
            "Mode": mode_value
        }

    def apply_parameters(self):
        parameter_data = self.collect_and_validate_input()
        if parameter_data is None:
            return  # Early exit if validation fails

        if self.current_id is None:
            # New parameter insertion
            insert_parameters(parameter_data)
        else:
            # Update existing parameter
            parameter_data['id'] = self.current_id  # Ensure the ID is included for updates
            update_parameter_by_id(parameter_data)

        self.load_parameters()  # Refresh UI

    def load_parameters(self):
        self.parameters_table.clear()
        parameters = list_parameters()
        for param in parameters:
            # Assuming param structure: id, name, iterations, enabled, created_at, updated_at, distributions
            display_values = [
                str(param[0]),  # ID
                param[1],  # Name
                str(param[2]),  # Iterations
                "Yes" if param[3] else "No",  # Enabled
                param[4],  # "Created At"
                param[5]  # "Updated At"
            ]
            item = CenteredTreeWidgetItem(display_values)
            self.parameters_table.addTopLevelItem(item)
        self.adjust_column_widths()

    def adjust_column_widths(self):
        max_width = 200  # Set your desired maximum width for any column
        for column in range(self.parameters_table.columnCount()):
            # self.parameters_table.resizeColumnToContents(column)
            if self.parameters_table.columnWidth(column) > max_width:
                self.parameters_table.setColumnWidth(column, max_width)
