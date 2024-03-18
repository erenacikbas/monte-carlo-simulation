from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal

from preferences import update_language_preference


def accept_language_external(self, lang_code_map):
    selected_language = self.language_combo_box.currentText()
    update_language_preference(lang_code_map[selected_language])
    self.accept()  # Close the dialog


class LanguageDialog(QDialog):
    accepted_language = pyqtSignal(str)  # Define a signal to emit the selected language

    def __init__(self, lang_names, lang_code_map):
        super().__init__()
        self.setWindowTitle("Select Language")

        layout = QVBoxLayout(self)

        label = QLabel("Please select a language:")
        layout.addWidget(label)

        self.language_combo_box = QComboBox()
        self.language_combo_box.addItems(lang_names)
        layout.addWidget(self.language_combo_box)

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(
            lambda: accept_language_external(self, lang_code_map))  # Connect the button to an external method
        layout.addWidget(confirm_button)
