from tkinter import ttk


def populate_simulation_tab(self, tab):
    """
    Add a title label at the beginning of the tab content.

    :param self:
    :param tab: The tab to populate with content.
    :return: None
    """
    # Add a title label at the beginning of the tab content
    tab_title = self.lang.get("sim", "Simulation")
    ttk.Label(tab, text=tab_title, font=('Helvetica', 12, 'bold')).pack(side='top', fill='x', pady=(10, 0),
                                                                        padx=(10, 0))
    ttk.Label(tab, text=self.lang.get("simulation_description", "Simulation settings")).pack(pady=20)