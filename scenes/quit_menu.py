"""

# Code to load the login scene

"""

"""
# Import nessicary functions/ procedures
"""
import sys
from tkinter import *
from variables import frame_colour, button_colour, font, main_background, fall_back_colour
from Utils.json_handler import set_logged_in_user

# Quit the game

def tkquit():
    sys.exit()

"""
# Main class to control the scene
"""
class quit_menu:
    # Initialises the class with parameters passed in and set the base class specific variables   
    def __init__(self, window, username, protecting):
        self._window = window
        self._username = username
        self._protecting = protecting
        self._elements = {}
        self._main_background = None

    # Removes all elements from the screen apart from the main background
    def clear_screen(self):
        for element in self._elements.values():
            try:
                element.destroy()
            except:
                try:
                    element.place_forget()
                except:
                    pass
        self._elements.clear()

    # Load the background for the scene
    # Load any data from external files
    # Create any elements required for the GUI / Scene
    # Place all base elements on screen
    def load_utils(self):
        try:
            self._main_background = PhotoImage(file=main_background)
            bg = Label(self._window, image=self._main_background)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
            self._elements["background"] = bg
        except Exception as e:
            print("Error loading background:", e)
            self._window.configure(bg=fall_back_colour)

        frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=400)
        self._elements["frame"] = frame

        label = Label(frame, text="Are you sure you want to quit?",
                      font=(font, 25, 'bold'), bg=button_colour, fg="white", bd=10, relief=RIDGE,
                      wraplength=600, justify="center")
        label.place(relx=0.5, rely=0.25, anchor=CENTER)
        self._elements["label"] = label

        btn_no = Button(frame, text="NO", width=10, font=(font, 30, 'bold'),
                        bg=button_colour, fg="white", bd=10, relief=RIDGE,
                        activebackground=button_colour, activeforeground="white",
                        command=self.quit_unconfirm)
        btn_no.place(relx=0.5, rely=0.55, anchor=CENTER)
        self._elements["btn_no"] = btn_no

        btn_yes = Button(frame, text="YES", width=10, font=(font, 30, 'bold'),
                         bg=button_colour, fg="white", bd=10, relief=RIDGE,
                         activebackground=button_colour, activeforeground="white",
                         command=tkquit)
        btn_yes.place(relx=0.5, rely=0.85, anchor=CENTER)
        self._elements["btn_yes"] = btn_yes

    # Loads the main menu scene
    def quit_unconfirm(self):
        self.clear_quit_screen()
        from scenes.main_menu import main_menu
        main = main_menu(self._window, self._username, self._protecting)
        main.run()

    # Saves the current logged in user into the json file
    def save_current_user(self):
        username_value = self._username.get() if hasattr(self._username, 'get') else self._username

        set_logged_in_user(username_value, protecting=self._protecting, encrypt=True)

    # Runs the file (Called remotely)
    def run(self):
        self.load_utils()
        self.save_current_user()