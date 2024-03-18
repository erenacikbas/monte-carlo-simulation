from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt


class CenteredTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, values):
        super().__init__(values)
        for i in range(len(values)):
            self.setTextAlignment(i, Qt.AlignmentFlag.AlignCenter)
            if values[-1] == "Yes":
                self.setBackground(i, QBrush(Qt.GlobalColor.green))
