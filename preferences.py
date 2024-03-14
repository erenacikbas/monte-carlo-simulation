# Author: Eren Tuna Açıkbaş 2024

# json is a library for working with JSON data
import json
import os


def update_language_preference(new_language_code):
    """
    :param new_language_code: The new language code to update the language preference to.
    :return: None

    This method updates the language preference in the configuration file. It takes the new language code as a parameter and modifies the 'language' field under the 'userPreferences' section
    * in the configuration file specified by 'config.json'. If the configuration file doesn't exist, it starts with an empty configuration. If the configuration file is not valid JSON, an
    * error message is printed and the method returns without making any changes. The updated configuration is then written back to the file.
    """
    config_file_path = 'config.json'
    # Load the existing configuration
    try:
        with open(config_file_path, 'r', encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        # If the config file doesn't exist, start with an empty configuration
        config = {}
    except json.JSONDecodeError:
        # Handle case where the file is not valid JSON
        print("Error: config.json is not valid JSON.")
        return

    # Update the language field under userPreferences
    user_preferences = config.get('userPreferences', {})
    user_preferences['language'] = new_language_code
    config['userPreferences'] = user_preferences

    # Write the updated configuration back to the file
    with open(config_file_path, 'w', encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def load_preference():
    """
    This method loads the preference from the config file.

    :return: the language preference if it exists, otherwise None
    """
    # Use the environment variable to build the path to config.json
    config_dir = os.getenv('CONFIG_DIR', '.')  # Defaults to current directory if not set
    config_path = os.path.join(config_dir, 'config.json')

    try:
        with open("config.json", "r", encoding="utf-8") as file:
            try:
                config = json.load(file)
                # Correctly access nested dictionaries
                user_preferences = config.get("userPreferences", {})
                language = user_preferences.get("language", None)
                return None if language == "" else language
            except json.JSONDecodeError:
                # This handles the case where the file is empty or not valid JSON
                return None
    except FileNotFoundError:
        # This handles the case where the config file does not exist
        return None
