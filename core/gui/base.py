# Author: Eren Tuna Açıkbaş 2024
import json
import os
import tkinter as tk
from tkinter import ttk

from core.gui.tabs.about import populate_about_tab
from core.gui.tabs.license import populate_license_tab
from core.gui.tabs.parameters import populate_parameters_tab
from core.gui.tabs.settings import SettingsTab
from core.gui.tabs.simulations import populate_simulation_tab
from core.utils.lang import load_language
from preferences import update_language_preference
from core.utils.helpers import load_config
from core.db.database import create_tables


def configure_window(window, title):
    """
    Configure the window size and title.

    :param window: The window object to be configured.
    :param title: (Optional) The title to set for the window. Default is an empty string.
    :return: None

    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = screen_width // 2
    window_height = int(screen_height * 0.7)  # 60% of the screen height

    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)

    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    window.title(title)


def main_gui(lang_code="en_us"):
    """
    Starts the main graphical user interface.

    :return: None
    """
    create_tables()

    root = tk.Tk()
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
            app_name = config.get("application", {}).get("name", "")
            app_version = config.get("application", {}).get("version", "")
    except (FileNotFoundError, json.JSONDecodeError):
        app_name = ""
        app_version = ""
    # Initialize Main Application with root and language code from preferences
    MainApplication(root, app_name=app_name, app_version=app_version)
    root.mainloop()


def ask_language_gui():
    """
    Ask Language GUI

    This method creates a graphical user interface (GUI) to ask the user to select a language from a dropdown menu.

    :return: None
    """
    root = tk.Tk()
    configure_window(root, title="Select Language")
    language_var = tk.StringVar(value="English (US)")
    languages = [("English (US)", "en_us"), ("Turkish", "tr")]
    lang_code_map = dict(languages)

    label = ttk.Label(root, text="Please select a language:")
    label.pack(pady=10)

    dropdown = ttk.Combobox(root, textvariable=language_var, values=[lang[0] for lang in languages], state="readonly")
    dropdown.pack(pady=5)

    def on_confirm():
        selected_lang = language_var.get()
        language_code = lang_code_map[selected_lang]
        update_language_preference(language_code)
        root.destroy()

    confirm_button = ttk.Button(root, text="Confirm", command=on_confirm)
    confirm_button.pack(pady=20)
    root.mainloop()


class MainApplication:
    """
    Initializes a new instance of the MainApplication class.

    :param root: The root Tk object for the application.
    :type root: Tk
    :param lang_code: The language code to use for localization, defaults to "en_us".
    :type lang_code: str
    """

    def __init__(self, root, app_name, app_version):
        """
        Initialize the class object.

        :param root: The tkinter root window.
        :param lang_code: The language code used for localization.
        :param app_name: The name of the application.

        :return: None
        """
        # Initialize instance variables

        self.pending_changes = []
        self.config_table = None
        self.config_listbox = None
        self.app_version = app_version
        self.config = load_config()  # Load configuration from file
        self.lang_code = self.config.get("userPreferences", {}).get("language", "en_us")
        self.lang = load_language(self.lang_code)
        self.root = root
        self.static_dir = os.path.join(os.path.dirname(__file__), '../../', 'static')
        self.parameter_vars = {}  # Initialize parameter_vars here
        configure_window(self.root, title=app_name)
        # self.create_header()
        self.create_footer()
        self.create_tabs()

    def create_tabs(self):
        """
        Creates the tabs and adds them to a ttk.Notebook widget.

        :return: None
        """
        tab_control = ttk.Notebook(self.root)

        # Simulation Tab
        simulation_tab = ttk.Frame(tab_control)
        tab_control.add(simulation_tab, text=self.lang.get("simulations", "Simulations"))

        # Plot Tab
        plot_tab = ttk.Frame(tab_control)
        tab_control.add(plot_tab, text=self.lang.get("results", "Results"))

        # Configuration Tab
        parameters_tab = ttk.Frame(tab_control)
        tab_control.add(parameters_tab, text=self.lang.get("parameters", "Configuration"))

        # Settings Tab
        settings_tab = ttk.Frame(tab_control)
        SettingsTab(settings_tab, self.config)
        tab_control.add(settings_tab, text=self.lang.get("settings", "Settings"))

        # About Tab
        about_tab = ttk.Frame(tab_control)
        tab_control.add(about_tab, text=self.lang.get("about", "About"))
        populate_about_tab(self, about_tab)

        # License Tab
        license_tab = ttk.Frame(tab_control)
        tab_control.add(license_tab, text=self.lang.get("license", "License"))
        populate_license_tab(self, license_tab)

        # Simulation Tab
        populate_simulation_tab(self, simulation_tab)

        # Parameters Tab
        populate_parameters_tab(self, parameters_tab)

        tab_control.pack(expand=1, fill="both")

    def create_header(self):
        """
        Create header with welcome message and app information.

        :return: None
        """
        # Example of creating a header with welcome message and app information
        header_text = self.lang.get("welcome_message", "Welcome to the Monte Carlo Simulation Application!")
        header = ttk.Label(self.root, text=header_text, font=('Helvetica', 12))
        header.pack(side='top', fill='x', padx=10, pady=5)

    def create_footer(self):
        """
        Create the footer for the application.

        :return: None
        """
        # Language selection and license information in the footer
        footer = ttk.Frame(self.root)
        footer.pack(side='bottom', fill='x')

        # Language Dropdown
        # language_var = tk.StringVar(value=self.lang_code)
        # languages_dropdown = ttk.Combobox(footer, textvariable=language_var, state="readonly",
        #                                  values=list(get_available_languages_with_names().values()))
        # languages_dropdown.pack(side='left', padx=10, pady=5)
        # languages_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_language_change(language_var))

        # Application Version
        ttk.Label(footer, text=self.app_version).pack(side='left', padx=(10, 0), pady=5)

        # License Information
        license_text = self.lang.get("license_info", "© 2024 Eren Tuna Açıkbaş - MIT License")
        ttk.Label(footer, text=license_text).pack(side='bottom', pady=5)
