from tkinter import ttk
import tkinter as tk


def populate_license_tab(self, tab):
    # Assuming the LICENSE_TEXT contains your license information
    tab_title = self.lang.get("license", "License")
    ttk.Label(tab, text=tab_title, font=('Helvetica', 12, 'bold')).pack(side='top', fill='x', pady=(10, 0),
                                                                        padx=(10, 0))

    # License content
    license_content = tk.Text(tab, wrap='word', height=15)  # Adjust height as needed
    license_content.insert('1.0', self.lang.get("license_content", ""))
    license_content.config(state='disabled')  # Make the text read-only
    license_content.pack(padx=10, pady=10, fill='both', expand=True)

    # Scrollbar for the license content Text widget, if needed
    scrollbar = ttk.Scrollbar(tab, orient='vertical', command=license_content.yview)
    scrollbar.pack(side='right', fill='y')
    license_content['yscrollcommand'] = scrollbar.set