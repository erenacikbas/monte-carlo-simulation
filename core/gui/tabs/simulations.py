from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QLabel


def populate_simulation_tab(self, tab):
    """
    Add a title label at the beginning of the tab content.

    :param self:
    :param tab: The tab to populate with content.
    :return: None
    """
    # Add a title label at the beginning of the tab content
    tab_title = self.lang.get("sim", "Simulation")
    title_label = QLabel(tab_title)
    title_font = QFont()
    title_font.setBold(True)
    title_label.setFont(title_font)

    tab_layout = QVBoxLayout(tab)
    tab_layout.addWidget(title_label)

    description_label = QLabel(self.lang.get("simulation_description", "Simulation settings"))
    tab_layout.addWidget(description_label)
    tab_layout.addStretch(1)  # Add stretch to push the content upwards
