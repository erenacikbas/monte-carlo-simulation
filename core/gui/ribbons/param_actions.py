import os
from PyQt6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt


def create_action_ribbon(self, parent):
    static_dir = os.getenv("STATIC_DIR", ".")

    # Use QToolBar for a traditional ribbon-like appearance
    action_ribbon = QToolBar()
    action_ribbon.setIconSize(QSize(16, 16))  # Smaller icons
    action_ribbon.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    action_ribbon.setMovable(False)  # Optional: make the toolbar fixed

    # Define actions with icons
    save_action = QAction(QIcon(os.path.join(static_dir, 'icons', 'save.png')), "Save", action_ribbon)
    save_action.triggered.connect(lambda: self.save_changes())
    action_ribbon.addAction(save_action)
    self.save_button = action_ribbon.widgetForAction(save_action)  # Store for later use
    self.save_button.setEnabled(False)  # Initially disabled

    refresh_action = QAction(QIcon(os.path.join(static_dir, 'icons', 'refresh.png')), "Refresh", action_ribbon)
    refresh_action.triggered.connect(lambda: self.refresh_parameters())
    action_ribbon.addAction(refresh_action)

    delete_action = QAction(QIcon(os.path.join(static_dir, 'icons', 'delete.png')), "Delete", action_ribbon)
    delete_action.triggered.connect(lambda: self.delete_parameters())
    action_ribbon.addAction(delete_action)

    # Ensure the parent has a layout before adding the action_ribbon
    if not parent.layout():
        # If the parent has no layout, create a QVBoxLayout and set it to the parent
        layout = QVBoxLayout(parent)
        parent.setLayout(layout)

    parent.layout().addWidget(action_ribbon)
