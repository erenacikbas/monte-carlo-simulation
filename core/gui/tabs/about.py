from tkinter import ttk
import tkinter as tk

from core.utils.helpers import open_mail, callback


def populate_about_tab(self, tab):
    """
    Populate the 'About' tab with content including a clickable link for Flaticon credit.
    """
    # Add a title label at the beginning of the tab content
    tab_title = self.lang.get("about_title", "About")
    about_description = self.lang.get("about_description", "")
    flaticon_credit = self.lang.get("flaticon_credit",
                                    "Icons made by [Flaticon](https://www.flaticon.com/authors/dave-gandy)")

    ttk.Label(tab, text=tab_title, font=('Helvetica', 12, 'bold')).pack(side='top', fill='x', pady=(10, 0),
                                                                        padx=(10, 0))

    # Dynamic about description loading
    about_text = tk.Text(tab, wrap="word", height=15)
    about_text.insert('1.0', about_description)
    about_text.insert('end', "contact@erenacikbas.com", "mail")
    about_text.tag_config("mail", foreground="blue", underline=1)
    about_text.tag_bind("mail", "<Button-1>", lambda e: open_mail("mailto:contact@erenacikbas.com"))
    about_text.config(state="disabled", cursor="arrow")
    about_text.pack(padx=10, expand=True, fill="both")

    # Flaticon credit label
    credit_label = ttk.Label(tab, text=flaticon_credit, foreground="blue", cursor="hand2")
    credit_label.pack(pady=5)
    credit_label.bind("<Button-1>", lambda e: callback("https://www.flaticon.com/authors/dave-gandy"))