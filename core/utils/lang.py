import json
import os


def load_language(lang="en_us"):
    """
    Load Language

    Loads a JSON file for the specified language.

    :param lang: The language code for the JSON file to be loaded. Default is "en_us".
    :return: The loaded JSON data.
    """
    lang_dir = os.getenv('LANG_DIR', '.')  # Defaults to current directory if not set
    lang_path = os.path.join(lang_dir, f"{lang}.json")
    with open(lang_path, "r", encoding="utf-8") as file:  # Specify UTF-8 encoding
        return json.load(file)


def get_available_languages_with_names(lang_dir="lang"):
    lang_code = "en_us"
    languages = {}
    try:
        files = os.listdir(lang_dir)
        for file in files:
            if file.endswith('.json'):
                lang_code = os.path.splitext(file)[0]
                file_path = os.path.join(lang_dir, file)
                with open(file_path, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    languages[lang_code] = data.get("language_name", lang_code)  # Use the code as fallback
    except FileNotFoundError:
        print("Languages directory not found.")
    return languages
