import os
from tkinter import ttk
from PIL import Image, ImageTk


def create_action_ribbon(self, parent):
    action_ribbon = ttk.Frame(parent, padding="2 2 2 2", relief="groove", borderwidth=1)
    action_ribbon.pack(side='top', fill='x', padx=5, pady=2)

    save_icon = ImageTk.PhotoImage(
        Image.open(os.path.join(self.static_dir, 'icons', 'save.png')).resize((16, 16), Image.Resampling.LANCZOS))
    refresh_icon = ImageTk.PhotoImage(
        Image.open(os.path.join(self.static_dir, 'icons', 'refresh.png')).resize((16, 16),
                                                                                 Image.Resampling.LANCZOS))
    delete_icon = ImageTk.PhotoImage(
        Image.open(os.path.join(self.static_dir, 'icons', 'delete.png')).resize((16, 16), Image.Resampling.LANCZOS))

    # Define buttons
    self.save_button = ttk.Button(action_ribbon, image=save_icon, command=lambda: self.save_changes())
    self.save_button.image = save_icon
    self.save_button.pack(side='left', padx=2, pady=2)
    self.save_button['state'] = 'disabled'  # Ensure this line doesn't cause the error

    refresh_button = ttk.Button(action_ribbon, image=refresh_icon, command=lambda: self.refresh_parameters())
    refresh_button.image = refresh_icon
    refresh_button.pack(side='left', padx=2, pady=2)

    delete_button = ttk.Button(action_ribbon, image=delete_icon, command=lambda: self.delete_parameters())
    delete_button.image = delete_icon
    delete_button.pack(side='left', padx=2, pady=2)