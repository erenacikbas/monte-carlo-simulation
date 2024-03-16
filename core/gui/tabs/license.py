from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QScrollArea


def populate_license_tab(self, tab):
    # Assuming the LICENSE_TEXT contains your license information
    tab_title = self.lang.get("license", "License")
    title_label = QLabel(tab_title)
    title_font = QFont()
    title_font.setBold(True)
    title_label.setFont(title_font)

    tab_layout = QVBoxLayout(tab)
    tab_layout.addWidget(title_label)

    # License content
    license_content = QTextEdit()
    license_content.setReadOnly(True)
    license_content.setPlainText(self.lang.get("license_content", ""))
    tab_layout.addWidget(license_content)

    # Scrollbar for the license content Text widget, if needed
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(license_content)
    tab_layout.addWidget(scroll_area)
