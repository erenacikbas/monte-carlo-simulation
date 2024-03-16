from PyQt6.QtWidgets import QTextBrowser, QLabel, QVBoxLayout, QFrame, QApplication
from PyQt6.QtGui import QTextCursor, QFont
from core.utils.helpers import open_mail, callback
from PyQt6.QtCore import Qt  # Add this line to import Qt


def populate_about_tab(self, tab):
    """
    Populate the 'About' tab with content including a clickable link for Flaticon credit.
    """
    # Add a title label at the beginning of the tab content
    tab_title = self.lang.get("about_title", "About")
    about_description = self.lang.get("about_description", "")
    flaticon_credit = self.lang.get("flaticon_credit",
                                    "Icons made by [Flaticon](https://www.flaticon.com/authors/dave-gandy)")

    title_label = QLabel(tab_title)
    title_font = QFont()
    title_font.setBold(True)
    title_label.setFont(title_font)
    tab_layout = QVBoxLayout(tab)
    tab_layout.addWidget(title_label)

    # Use QTextBrowser for dynamic about description loading with clickable links
    about_text = QTextBrowser()
    about_text.setReadOnly(True)
    about_text.setOpenExternalLinks(False)  # Handle links manually if needed
    about_text.setHtml(
        about_description + "<br><br><a href='mailto:contact@erenacikbas.com'>contact@erenacikbas.com</a>")
    # Connect the anchorClicked signal to your custom slot or lambda
    about_text.anchorClicked.connect(lambda link: open_mail("mailto:contact@erenacikbas.com"))
    tab_layout.addWidget(about_text)

    # Flaticon credit label
    credit_label = QLabel(flaticon_credit)
    credit_label.setTextInteractionFlags(
    credit_label.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse)
    credit_label.linkActivated.connect(lambda url: callback("https://www.flaticon.com/authors/dave-gandy"))
    tab_layout.addWidget(credit_label)
