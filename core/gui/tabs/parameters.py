from tkinter import ttk, messagebox
import tkinter as tk
from core.db.database import activate_parameter, delete_parameter, insert_parameters, list_parameters, enable_parameter
from core.gui.ribbons.param_actions import create_action_ribbon
import tkinter.font as tkfont


class ParametersTab:
    def __init__(self, tab, config, lang):
        self.save_button = None
        self.pending_changes = []
        self.parameter_vars = {}
        self.config_table = None
        self.populate_parameters_tab(tab)

    def update_save_button_state(self):
        if self.pending_changes:
            self.save_button['state'] = 'normal'
        else:
            self.save_button['state'] = 'disabled'

    def refresh_parameters(self):
        """This method reloads parameters from the database and updates the Treeview."""
        self.load_parameters()

    def delete_parameters(self):
        selected = self.config_table.selection()
        if selected:
            config_id = self.config_table.item(selected, 'values')[0]
            self.pending_changes.append(('delete', config_id))
            self.config_table.delete(selected)

            # After modifying pending_changes, update the Save button state
            self.update_save_button_state()

    def activate_parameters(self):
        """This method activates the selected parameters."""
        selected = self.config_table.selection()
        if selected:
            selected_id = self.config_table.item(selected[0], 'values')[0]  # Assuming the ID is in the first column
            activate_parameter(selected_id)  # Replace with your actual function to activate a parameters
            print(f"Activated parameters ID: {selected_id}")
            self.load_parameters()  # Reload parameters to reflect changes

    def save_changes(self):
        for action, config_id in self.pending_changes:
            if action == 'delete':
                delete_parameter(config_id)
            # Add handling for other actions ('add', 'update') as needed
        # Clear pending changes after committing
        self.pending_changes.clear()
        # Reload or update UI as necessary
        self.load_parameters()

    def populate_parameters_tab(self, tab):
        # Configuration Listing Section
        create_action_ribbon(self, tab)
        tab_title = self.lang.get("parameters", "Parameters")
        # Treeview setup for parameters
        setup_parameter_table(self, tab)
        load_parameters(self)  # Load parameters into the Treeview

        # New Parameter Form Section
        form_frame = ttk.LabelFrame(tab, text="Create New Parameter", padding=(10, 10))
        form_frame.pack(fill='x', padx=10, pady=5)
        create_parameter_form(self, form_frame)

        # Apply New Configuration Button
        apply_button = ttk.Button(tab, text=self.lang.get("create_new_parameter", "Apply New Parameter"),
                                  command=apply_parameters)
        apply_button.pack(pady=5)

    def create_parameter_form(self, parent):
        # Parameters with descriptions
        parameters = {
            "Name": "Unique name for the parameter configuration",
            "Iterations": "Number of sim iterations",
            "Area": "Area covered by the sim",
            "Thickness": "Thickness of the material",
            "Porosity": "Porosity of the material",
            "Water Saturation": "Water saturation in the material",
            "FVF": "Formation Volume Factor"
        }

        # Create a frame to center the fields within the parent
        center_frame = ttk.Frame(parent)
        center_frame.pack(side='top', fill='x', expand=True)

        for i, (parameter, description) in enumerate(parameters.items()):
            # Parameter Label
            label = ttk.Label(center_frame, text=f"{parameter}:")
            label.grid(row=i, column=0, sticky='e', )

            # Entry Field
            entry_var = tk.StringVar()
            entry = ttk.Entry(center_frame, textvariable=entry_var, width=20)
            entry.grid(row=i, column=1, padx=2, pady=2)

            self.parameter_vars[parameter] = entry_var

            # Description
            desc_label = ttk.Label(center_frame, text=f"({description})", font=("TkDefaultFont", 8))
            desc_label.grid(row=i, column=2, sticky='w', padx=2)

        # Configure the center_frame column weights
        center_frame.columnconfigure(0, weight=1)
        center_frame.columnconfigure(1, weight=2)
        center_frame.columnconfigure(2, weight=3)

        # This ensures the fields are centered by expanding the side columns more than the center
        parent.columnconfigure(0, weight=1)
        parent.pack(fill='x', expand=True)

    def setup_parameter_table(self, parent):
        # Frame to hold the Treeview and Scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)

        # Vertical Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Horizontal Scrollbar
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # TreeView setup
        columns = ('name', 'iterations', 'area', 'thickness', 'porosity', 'water_saturation', 'created_at',
                   'updated_at', 'enabled')
        self.config_table = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=vsb.set,
                                         xscrollcommand=hsb.set, selectmode='browse')

        # Setup column headings and columns alignment
        for col in columns:
            self.config_table.heading(col, text=col.replace('_', ' ').title(), anchor='center')
            self.config_table.column(col, anchor="center", stretch=True)

        self.config_table.pack(side='left', fill='both', expand=True)

        # Configure scrollbars to control the Treeview
        vsb.config(command=self.config_table.yview)
        hsb.config(command=self.config_table.xview)

        # Define a tag for enabled parameters with a specific background color
        self.config_table.tag_configure('Enabled', background='#C7FCC9')

    def apply_parameters(self):
        # Check if all fields have values
        if not all(self.parameter_vars[var].get().strip() for var in self.parameter_vars):
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        # Proceed if validation passes
        parameters = tuple(self.parameter_vars[var].get().strip() for var in self.parameter_vars)
        # Your code to insert or update the parameters goes here
        insert_parameters(parameters)
        self.load_parameters()  # Refresh the list to include the new parameters

    def adjust_column_widths_to_content(self):
        for column in self.config_table["columns"]:
            self.config_table.column(column, width=tkfont.Font().measure(column.title()))
            for row in self.config_table.get_children():
                cell_value = self.config_table.set(row, column)
                cell_width = tkfont.Font().measure(cell_value)
                if self.config_table.column(column)["width"] < cell_width:
                    self.config_table.column(column, width=cell_width)

    def load_parameters(self):
        # Clear current entries
        for item in self.config_table.get_children():
            self.config_table.delete(item)

        # Fetch parameters and insert into the table
        for config in list_parameters():
            # Assuming 'config' is a tuple like:
            # (id, name, enabled, iterations, area, thickness, porosity, water_saturation, fvf, created_at, updated_at)
            # Adjust the tuple indices according to your actual data structure

            # Format the 'enabled' column value for display
            enabled_text = 'Yes' if config[-1] else 'No'

            # Prepare values for insertion. This example assumes 'enabled' is at index 2.
            # Replace 'config[2]' with 'enabled_text' and include all other relevant fields.
            display_values = config[:-1] + (enabled_text,)

            if config[-1]:  # If the configuration is enabled, use the 'Enabled' tag
                self.config_table.insert('', tk.END, values=display_values, tags=('Enabled',))
            else:
                self.config_table.insert('', tk.END, values=display_values)

    def enable_selected_parameter(self):
        selection = self.config_listbox.curselection()
        if selection:
            selected_text = self.config_listbox.get(selection[0])
            selected_id = self.extract_id_from_selection(selected_text)  # Implement this method to parse the ID
            enable_parameter(selected_id)
            self.load_parameters()
