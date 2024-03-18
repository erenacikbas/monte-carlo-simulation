# Author: Eren Tuna Açıkbaş 2024
# Title: Monte Carlo Simulation with Python
# Description: This is a simple Monte Carlo sim with Python.
from PyQt6.QtWidgets import QDialog

from core.gui.base import ask_language_gui, main_gui
from preferences import load_preference, update_language_preference
from dotenv import load_dotenv
import os


def main():
    # Load the environment variables from the .env file

    # this will get the directory where the script is located
    # Get the directory of the current script
    app_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(app_dir, os.pardir))
    print(f"Root directory: {root_dir}")

    # Path to your .env file
    os.environ['CONFIG_DIR'] = root_dir
    os.environ['LANG_DIR'] = os.path.join(root_dir, 'core', 'lang')
    os.environ['STATIC_DIR'] = os.path.join(root_dir, 'static')

    # Attempt to load the saved language preference
    language_code = load_preference()
    language_options = [("English (US)", "en_us"), ("Turkish", "tr")]
    lang_names = [option[0] for option in language_options]
    lang_code_map = {option[0]: option[1] for option in language_options}

    # If no preference is found, ask the user to select a language.
    # This updates the language preference based on user selection.
    if language_code is None:
        result = ask_language_gui(lang_names, lang_code_map)
        if result == QDialog.accepted:  # If language selection dialog was accepted
            language_code = load_preference()  # Attempt to reload the preference after selection
        else:
            print("Language selection dialog was closed without selecting a language.")
            return  # Exit the main function

    if language_code is None:
        print("Error: No language preference found. Defaulting to English.")
        # If the user closes the language selection window without selecting a language, default to English
        language_code = "en_us"
        update_language_preference(language_code)

    main_gui(language_code)


if __name__ == "__main__":
    main()
