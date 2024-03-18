import json
import os

from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QGroupBox, QHBoxLayout
)
from PyQt6.QtCore import Qt

from core.utils.helpers import request_restart
from core.utils.lang import load_language


# Function to save settings
def save_settings(self):
    try:
        selected_lang_name = self.language_var.currentText()
        lang_code = self.lang_code_map[selected_lang_name]
        print("Selected Language Code:", lang_code)
        if lang_code:
            self.config["userPreferences"]["language"] = lang_code
            self.config["userPreferences"]["theme"] = self.theme_var.text().strip()
            self.config["userPreferences"]["fieldUnits"] = self.field_units_var.currentText()

            config_path = os.path.join(os.getenv('CONFIG_DIR', '.'), "config.json")

            print("Saving settings to:", config_path)

            with open(config_path, "w", encoding="utf-8") as config_file:
                json.dump(self.config, config_file, indent=4)

            QMessageBox.information(None, "Settings Saved", "Your settings have been saved successfully.")
            request_restart()

        else:
            QMessageBox.critical(None, "Error", "Selected language not found.")

    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to save settings: {str(e)}")


# Class for Settings Tab
class SettingsTab:
    def __init__(self, context, tab):
        self.context = context
        self.config = self.context.config
        self.language_options = [("English (US)", "en_us"), ("Turkish", "tr")]
        self.language_names = [option[0] for option in self.language_options]
        self.lang_code_map = {option[0]: option[1] for option in self.language_options}
        self.lang_map = {v: k for k, v in self.lang_code_map.items()}
        self.field_units_var = None
        self.lang_code = self.config.get("userPreferences", {}).get("language", "en_us")
        self.default_area_var = None
        self.language_var = None
        self.precision_var = None
        self.theme_var = None
        self.lang = load_language(self.lang_code)
        # Populate the settings tab
        self.populate_settings_tab(tab)

    def populate_settings_tab(self, tab):
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(10, 10, 10, 10)  # Provide padding around the layout

        # Language Settings Group
        lang_group_box = QGroupBox(self.lang.get("language_settings", "Language Settings"))
        lang_group_layout = QVBoxLayout(lang_group_box)
        self.setup_language_settings(lang_group_layout)
        tab_layout.addWidget(lang_group_box)
        tab_layout.addSpacing(10)  # Add some space between groups

        # Appearance Settings Group
        appearance_group_box = QGroupBox(self.lang.get("appearance_settings", "Appearance and Units"))
        appearance_group_layout = QVBoxLayout(appearance_group_box)
        self.setup_appearance_settings(appearance_group_layout)
        tab_layout.addWidget(appearance_group_box)
        tab_layout.addSpacing(10)  # Add some space between groups

        # Save Settings Button with its own layout for proper alignment
        save_button_layout = QHBoxLayout()
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        save_settings_button = QPushButton(self.lang.get("settings_save", "Save Settings"))
        save_settings_button.clicked.connect(lambda: save_settings(self))  # Connect save_settings method here
        save_button_layout.addWidget(save_settings_button)

        save_button_layout.addStretch()  # Push the button to the left
        tab_layout.addLayout(save_button_layout)

        tab_layout.addStretch()  # Add a stretchable space only at the end (bottom)

    def setup_language_settings(self, layout):
        lang_label = QLabel(self.lang.get("settings_lang_selection", "Select Language:"))
        layout.addWidget(lang_label)
        self.language_var = QComboBox()
        self.language_var.addItems(self.language_names)
        self.language_var.setCurrentIndex(self.language_var.findText(self.lang_map[self.lang_code]))
        layout.addWidget(self.language_var)

    def setup_appearance_settings(self, layout):
        # Theme Setting
        theme_label = QLabel(self.lang.get("settings_theme_selection", "Theme:"))
        layout.addWidget(theme_label)
        self.theme_var = QLineEdit(self.config["userPreferences"].get("theme", ""))
        layout.addWidget(self.theme_var)

        # Field Units Setting
        field_units_label = QLabel(self.lang.get("settings_field_unit_selection", "Field Units:"))
        layout.addWidget(field_units_label)
        self.field_units_var = QComboBox()
        self.field_units_var.addItems(["Oilfield", "Metric"])
        self.field_units_var.setCurrentText(self.config["userPreferences"].get("fieldUnits", "Oilfield"))
        layout.addWidget(self.field_units_var)
