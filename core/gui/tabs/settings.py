import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Required for showing message dialogs
from core.utils.helpers import request_restart
from core.utils.lang import load_language


class SettingsTab:
    def __init__(self, tab, config):
        self.config = config
        self.number_of_simulations_var = None
        self.language_options = [("English (US)", "en_us"), ("Turkish", "tr")]
        self.language_names = [option[0] for option in self.language_options]
        self.lang_code_map = {code: name for name, code in self.language_options}
        self.field_units_var = tk.StringVar(value=self.config.get("userPreferences", {}).get("fieldUnits", "Oilfield"))
        self.lang_code = self.config.get("userPreferences", {}).get("language", "en_us")
        self.default_area_var = tk.StringVar(value=self.config.get("simulationSettings", {}).get("defaultArea", 100))
        self.language_var = tk.StringVar(value=self.lang_code_map.get(self.lang_code, "English (US)"))
        self.precision_var = tk.StringVar(value=self.config.get("simulationSettings", {}).get("precision", 2))
        self.theme_var = None
        self.lang = load_language(self.lang_code)

        # Populate the settings tab
        self.populate_settings_tab(tab)

    def populate_settings_tab(self, tab):
        """
        Populates the settings tab with options for language, theme, field units, and default sim parameters.
        """
        # Title for the settings section
        ttk.Label(tab, text=self.lang.get("settings", "Settings"), font=('Helvetica', 12, 'bold')).pack(side='top', fill='x', pady=10)

        # Language Selection
        ttk.Label(tab, text=self.lang.get("settings_lang_selection", "Select Language:")).pack(pady=5)
        languages_dropdown = ttk.Combobox(tab, textvariable=self.language_var, values=self.language_names,
                                          state="readonly")
        languages_dropdown.pack(pady=5)

        # Theme Setting
        ttk.Label(tab, text=self.lang.get("settings_theme_selection", "Theme:")).pack(pady=5)
        self.theme_var = tk.StringVar(value=self.config["userPreferences"]["theme"])
        theme_options = ["light", "dark"]
        theme_dropdown = ttk.Combobox(tab, textvariable=self.theme_var, values=theme_options, state="readonly")
        theme_dropdown.pack()

        # Field Units Setting
        ttk.Label(tab, text=self.lang.get("settings_field_unit_selection", "Field Units:")).pack(pady=5)
        field_units_options = ["Oilfield", "Metric"]
        field_units_dropdown = ttk.Combobox(tab, textvariable=self.field_units_var, values=field_units_options,
                                            state="readonly")
        field_units_dropdown.pack()

        # Default Area Setting
        ttk.Label(tab, text=self.lang.get("settings_default_area_selection", "Default Area (sq km or sq miles):")).pack(pady=5)
        default_area_entry = ttk.Entry(tab, textvariable=self.default_area_var)
        default_area_entry.pack()

        # Precision Setting
        ttk.Label(tab, text=self.lang.get("precision", "Precision:")).pack(pady=5)
        precision_entry = ttk.Entry(tab, textvariable=self.precision_var)
        precision_entry.pack()

        # Save Settings Button
        save_settings_button = ttk.Button(tab, text=self.lang.get("settings_save", "Save Settings"),
                                          command=self.save_settings)  # Fixed command reference
        save_settings_button.pack(pady=20)

    def save_settings(self):
        """
        Saves the modified settings back to the config.json file.
        """

        # Update config with the new settings
        selected_lang_name = self.language_var.get()
        lang_code = next((code for name, code in self.language_options if name == selected_lang_name), None)

        if not lang_code:
            messagebox.showerror("Error", "Selected language not found.")
            return
        print(lang_code)

        self.config["userPreferences"]["language"] = lang_code
        self.config["userPreferences"]["theme"] = self.theme_var.get()
        self.config["userPreferences"]["fieldUnits"] = self.field_units_var.get()
        self.config["simulationSettings"]["defaultArea"] = float(self.default_area_var.get())

        config_dir = os.getenv('CONFIG_DIR', '.')
        config_path = os.path.join(config_dir, "config.json")
        with open(config_path, "w") as config_file:
            json.dump(self.config, config_file, indent=4)

        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully. Reloading application...")
        request_restart()  # Ensure this function is properly defined elsewhere in your application
