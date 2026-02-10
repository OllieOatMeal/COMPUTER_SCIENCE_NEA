"""
Placeholder for multiplayer game (coming soon)
"""

from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour


class multiplayer:
    """Multiplayer game (not finished yet)"""
    def __init__(self, window, username, balance, protecting):
        # Keep state for this placeholder screen
        self.window = window
        self.username = username
        self.balance = balance
        self.elements = {}
        self.protecting = protecting

    def clear_screen(self):
        # Hide widgets before leaving the scene
        for element in self.elements.values():
            element.place_forget()

    def load_utils(self):
        # Build the placeholder UI and background
        try:
            self.main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self.window, bg=fall_back_colour, bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
            background.lower()
        else:
            self.img_background = Label(self.window, image=self.main_background, bd=0)
            self.img_background.place(x=0, y=0)

        mp_frame = Frame(self.window, width=1500, height=720, bg=frame_colour, bd=10, relief=RAISED)
        mp_frame.place(relx=0.5, rely=0.6, anchor=CENTER)
        mp_frame.lift()
        self.elements["mp_frame"] = mp_frame

        self.elements["mp_label"] = Label(mp_frame, text="Sorry there is no Multiplayer Mode currently. \nPlease check back later.", font=(font, 30, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        self.elements["exit_button"] = Button(mp_frame, text="Exit", font=(font, 40, 'bold'), relief=RAISED, bd=10, bg=button_colour, fg='#ffffff', activebackground=button_colour, activeforeground='#ffffff', command=self.back_to_main_menu)

        self.elements["mp_label"].place(relx=0.5, rely=0.4, anchor=CENTER)
        self.elements["exit_button"].place(relx=0.05, rely=0.8, anchor='w', width=200, height=100)

        for element in self.elements.values():
            element.lift()

    def back_to_main_menu(self):
        # Return to main menu
        from scenes.main_menu import main_menu
        self.clear_screen()
        main_meu = main_menu(self.window, self.username, self.protecting)
        main_meu.run()

    def run(self):
        # Build and show placeholder screen
        self.load_utils()