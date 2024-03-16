from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton


class LanguageDialog(QDialog):
    def __init__(self, language_options):
        super().__init__()
        self.setWindowTitle("Select Language")

        layout = QVBoxLayout(self)

        label = QLabel("Please select a language:")
        layout.addWidget(label)

        self.language_combo_box = QComboBox()
        self.language_combo_box.addItems(language_options)
        layout.addWidget(self.language_combo_box)

        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.accept_language)
        layout.addWidget(confirm_button)

    def accept_language(self):
        selected_language = self.language_combo_box.currentText()
        self.accepted.emit(selected_language)
