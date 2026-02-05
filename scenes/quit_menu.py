"""
Screen that asks if you want to quit
Saves your info before closing
"""

import sys
from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour
from Utils.json_handler import set_logged_in_user


def tkquit():
    """Close the game"""
    sys.exit()


class quit_menu:
    """Quit confirmation screen"""
    
    def old_init(self):
        """
    Quit menu scene controller
    Displays confirmation dialog and handles user session data
    """

    def __init__(self, window, username, protecting):
        """
        Initialise quit menu
        Args:
            window: Tkinter root window
            username: Current logged-in username
            protecting: EncryptionService instance
        """
        self.window = window
        self.username = username
        self.protecting = protecting
        self.elements = {}
        self.main_background = None

    def clear_quit_screen(self):
        """
        Remove all UI elements from the quit screen
        Attempts to destroy widgets and fallback to place_forget
        """
        for element in self.elements.values():
            try:
                element.destroy()  # Fully remove the widget
            except:
                try:
                    element.place_forget()
                except:
                    pass
        self.elements.clear()

    def load_utils(self):
        """
        Load and create all UI elements for the quit confirmation dialog
        Sets up background, frame, labels, and buttons
        """
        # LOAD BACKGROUND
        try:
            self.main_background = PhotoImage(file=main_background)
            bg = Label(self.window, image=self.main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self.elements["background"] = bg
        except Exception as e:
            print("Error loading background:", e)
            self.window.configure(bg=fall_back_colour)

        # CREATE CENTER FRAME
        frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=400)
        self.elements["frame"] = frame

        # CREATE CONFIRMATION LABEL
        label = Label(frame, text="Are you sure you want to quit?",
                      font=(font, 25, 'bold'), bg=button_colour, fg="white", bd=10, relief=RIDGE,
                      wraplength=600, justify="center")
        label.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.elements["label"] = label

        # CREATE NO BUTTON
        btn_no = Button(frame, text="NO", width=10, font=(font, 30, 'bold'),
                        bg=button_colour, fg="white", bd=10, relief=RIDGE,
                        activebackground=button_colour, activeforeground="white",
                        command=self.quit_unconfirm)
        btn_no.place(relx=0.5, rely=0.55, anchor=CENTER)
        self.elements["btn_no"] = btn_no

        # CREATE YES BUTTON
        btn_yes = Button(frame, text="YES", width=10, font=(font, 30, 'bold'),
                         bg=button_colour, fg="white", bd=10, relief=RIDGE,
                         activebackground=button_colour, activeforeground="white",
                         command=tkquit)
        btn_yes.place(relx=0.5, rely=0.85, anchor=CENTER)
        self.elements["btn_yes"] = btn_yes

    def quit_unconfirm(self):
        """Cancel quit operation and return to main menu"""
        self.clear_quit_screen()
        from scenes.main_menu import main_menu
        main = main_menu(self.window, self.username, self.protecting)
        main.run()

    def save_current_user(self):
        """
        Save current user session data to JSON file
        Encrypts username and preserves all existing JSON data
        """
        # Safely extract raw username string
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        # Use json handler which will encrypt the value when requested
        set_logged_in_user(username_value, protecting=self.protecting, encrypt=True)

    def run(self):
        """
        Main entry point for quit menu scene
        Loads UI and saves user session before showing confirmation
        """
        self.load_utils()
        self.save_current_user()