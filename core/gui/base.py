import json
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget, QFrame, QHBoxLayout, \
    QPushButton

from core.gui.dialogs.language import LanguageDialog
from core.gui.tabs.about import populate_about_tab
from core.gui.tabs.license import populate_license_tab
from core.gui.tabs.parameters import ParametersTab
from core.gui.tabs.settings import SettingsTab
from core.gui.tabs.simulations import SimulationsTab
from core.utils.lang import load_language
from core.utils.helpers import load_config
from PyQt6.QtCore import Qt
from core.db.database import create_tables


def button_clicked():
    print("Button clicked!")


class MainApplication(QMainWindow):
    def __init__(self, app_name, app_version):
        super().__init__()
        self.app_name = app_name
        self.app_version = app_version
        self.config = load_config()  # Load configuration from file
        self.lang_code = self.config.get("userPreferences", {}).get("language", "en_us")
        self.lang = load_language(self.lang_code)
        self.setWindowTitle(app_name)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.tab_widget = None  # Attribute to store a reference to the tab widge
        self.simulation_tab = None
        self.create_tabs()
        self.create_footer()
        self.show()
        self.resize_app()

        # Connect tab widget's currentChanged signal to the refresh method

    def resize_app(self):
        # Retrieve the size of the screen
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.5)  # 50% of the screen width, converted to int
        height = int(screen.height() * 0.8)  # 80% of the screen height, converted to int

        # Calculate the center point for the application window
        left = int((screen.width() - width) / 2)  # Converted to int
        top = int((screen.height() - height) / 2)  # Converted to int

        # Set the window geometry with integer values
        self.setGeometry(left, top, width, height)

    def create_tabs(self):
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Parameters Tab
        parameters_tab = QWidget()
        self.tab_widget.addTab(parameters_tab, self.lang.get("parameters", "Configuration"))
        ParametersTab(parameters_tab, self.config, self.lang)

        # Simulation Tab
        self.simulation_tab = QWidget()
        # Keep a reference to the SimulationsTab instance
        # Assuming 'simulation_tab_widget' is the QWidget or QTabWidget you want to use as the container
        self.simulations_tab_instance = SimulationsTab(context=self, tab=self.simulation_tab)
        self.tab_widget.addTab(self.simulation_tab, self.lang.get("simulations", "Simulations"))

        # Plot Tab
        # plot_tab = QWidget()
        # self.tab_widget.addTab(plot_tab, self.lang.get("results", "Results"))

        # Settings Tab
        settings_tab = QWidget()
        self.tab_widget.addTab(settings_tab, self.lang.get("settings", "Settings"))
        settings_tab = SettingsTab(self, settings_tab)

        # About Tab
        about_tab = QWidget()
        self.tab_widget.addTab(about_tab, self.lang.get("about", "About"))
        populate_about_tab(self, about_tab)

        # License Tab
        license_tab = QWidget()
        self.tab_widget.addTab(license_tab, self.lang.get("license", "License"))
        populate_license_tab(self, license_tab)

        # Connect tab widget's currentChanged signal to the refresh method
        self.tab_widget.currentChanged.connect(self.refresh_on_simulation_tab_selected)

    def refresh_on_simulation_tab_selected(self, index):
        print("Tab changed to index:", index)
        # Check if the SimulationsTab is the currently selected tab
        if self.tab_widget.widget(index) == self.simulation_tab:
            # If so, refresh the enabled parameter in the SimulationsTab
            self.simulations_tab_instance.refresh_parameters()

    def create_footer(self):
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)  # Changed to QHBoxLayout
        self.layout.addWidget(footer_frame)

        # Application Version (Align left)
        version_label = QLabel(self.app_version)
        version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        footer_layout.addWidget(version_label)

        footer_layout.addStretch(1)  # Add stretch to push the license to the center

        # License Information (Centered)
        license_text = self.lang.get("license_info", "© 2024 Only Wells - MIT License")
        license_label = QLabel(license_text)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(license_label)

        footer_layout.addStretch(1)  # Add another stretch to ensure the license label stays centered


def main_gui(lang_code="en_us"):
    create_tables()
    config_dir = os.environ['CONFIG_DIR']
    config_path = os.path.join(config_dir, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            app_name = config.get("application", {}).get("name", "")
            app_version = config.get("application", {}).get("version", "")
    except (FileNotFoundError, json.JSONDecodeError):
        app_name = "Monte Carlo Reservoir Simulation"
        app_version = "v0.0.1"

    app = QApplication(sys.argv)
    main_app = MainApplication(app_name, app_version)
    sys.exit(app.exec())


def ask_language_gui(language_options):
    app = QApplication(sys.argv)
    language_dialog = LanguageDialog(language_options)
    language_dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_gui()