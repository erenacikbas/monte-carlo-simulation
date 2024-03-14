import json
import os
import sys
import webbrowser

RESTART_EXIT_CODE = 42  # Must match the watchdog script


def request_restart():
    sys.exit(RESTART_EXIT_CODE)


def callback(url):
    """
    Open a web browser pointing to the specified URL.

    :param url: URL to be opened in the web browser.
    """
    import webbrowser
    webbrowser.open_new(url)


def open_mail(link):
    webbrowser.open(link)


def load_config():
    """Loads the configuration from config.json into self.config."""
    # Use the environment variable to build the path to config.json
    config_dir = os.getenv('CONFIG_DIR', '.')  # Defaults to current directory if not set
    config_path = os.path.join(config_dir, 'config.json')
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}")
        return {}  # Use an empty dict if the config file doesn't exist or has errors
