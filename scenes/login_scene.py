"""

# Code to load the login scene

"""

"""
# Import nessicary functions/ procedures
"""
from Utils.db import get_user_password, user_exists, create_user, update_last_login
from tkinter import *
import sys
from scenes.main_menu import main_menu
from variables import font, button_colour, frame_colour, main_background, fall_back_colour
from music import music
from Utils.json_handler import get_logged_in_user, get_stored_music, get_music_volume, get_music_muted, set_logged_in_user

# Set the variables for the restrictions on username / password
DISALLOWED_USERNAME_CHARS = [' ', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '-', '/', '\\', '|', '{', '}', '[', ']', ':', ';', '"', "'", '<', '>', ',', '.', '?', '`', '~']
DISALLOWED_PASSWORD_CHARS = [' ', ';', '\'', '\"']
MAX_LENGTH = 12

# Quit the game
def tkquit():
    sys.exit()

"""
# Main class to control the scene
"""
class login:
    # Initialises the class with parameters passed in and set the base class specific variables 
    def __init__(self, window, protecting, music_controller=None):
        self._img_background = None
        self._window = window
        self._protecting = protecting
        self._music_controller = music_controller

        self._username = None
        self._password = None
        self._user_music = None

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
        self._login_frame = Frame(self._window, bg=frame_colour, bd=10, relief=RIDGE)
        self._login_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=700)

        try:
            self._main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self._window, bg=fall_back_colour, bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self._img_background = Label(self._window, image=self._main_background, bd=0)
            self._img_background.place(x=0, y=0)

        self._username = StringVar()
        self._password = StringVar()

        login_button = Button(self._login_frame, text='Login', font=(font, 12, 'bold'), width=6,
                            relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                            fg='#ffffff', activeforeground='#ffffff', command=self.login_pressed)
        signup_button = Button(self._login_frame, text='Sign Up', font=(font, 12, 'bold'),
                             relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                             fg='#ffffff', activeforeground='#ffffff', command=self.signup_pressed)
        quit_button = Button(self._window, text='Quit', font=(font, 25, 'bold'), width=9,
                           relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                           fg='#ffffff', activeforeground='#ffffff', command=tkquit)

        enter_username_label = Label(self._login_frame, text="Enter Username", font=(font, 40, 'bold'),
                                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        enter_password_label = Label(self._login_frame, text="Enter Password", font=(font, 40, 'bold'),
                                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        message_label = Label(self._login_frame, text="", font=(font, 20, 'bold'),
                            fg='#bb0000', bg='#de418e')

        username_field = Entry(self._login_frame, width=25, bg=button_colour, fg='#000000',
                             relief=RAISED, font=('Candara', 15, 'bold'), bd=10,
                             textvariable=self._username)
        password_field = Entry(self._login_frame, width=25, bg=button_colour, fg='#000000',
                             relief=RAISED, font=('Candara', 15, 'bold'), bd=10,
                             show="*", textvariable=self._password)

        self._elements = {
            "login_button": login_button,
            "signup_button": signup_button,
            "enter_username_label": enter_username_label,
            "enter_password_label": enter_password_label,
            "username_field": username_field,
            "password_field": password_field,
            "message_label": message_label,
            "quit_button": quit_button,
            "login_frame": self._login_frame,
        }

    # Places the elements on screen in their respective locations
    def create_login_screen(self):
        self._elements["enter_username_label"].place(relx=0.5, rely=0.2, anchor=CENTER)
        self._elements["username_field"].place(relx=0.5, rely=0.3125, anchor=CENTER)
        self._elements["enter_password_label"].place(relx=0.5, rely=0.5, anchor=CENTER)
        self._elements["password_field"].place(relx=0.5, rely=0.6125, anchor=CENTER)
        self._elements["login_button"].place(relx=0.4, rely=0.9, anchor=CENTER)
        self._elements["signup_button"].place(relx=0.6, rely=0.9, anchor=CENTER)
        self._elements["quit_button"].place(relx=0.1, rely=0.9, anchor=CENTER)
        self._login_frame.lift()

    # Validate the inputted username / password
    def validate_inputs(self):
        username = self._username.get() if hasattr(self._username, 'get') else self._username
        password = self._password.get()

        for ch in DISALLOWED_USERNAME_CHARS:
            if ch in username:
                self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
                self._elements["message_label"].config(text=f"Invalid character '{ch}' in username")
                return False

        for ch in DISALLOWED_PASSWORD_CHARS:
            if ch in password:
                self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
                self._elements["message_label"].config(text=f"Invalid character '{ch}' in password")
                return False

        if not username or not password:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text="Username and password cannot be empty")
            return False

        if len(username) > MAX_LENGTH:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text=f"Username cannot be longer than {MAX_LENGTH} characters")
            return False

        if len(password) > MAX_LENGTH:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text=f"Password cannot be longer than {MAX_LENGTH} characters")
            return False

        return True

    # Attempt to login the user
    def login_pressed(self):
        self._elements["message_label"].config(text="")

        if not self.validate_inputs():
            return

        username_value = self._username.get() if hasattr(self._username, 'get') else self._username

        stored_password = get_user_password(username_value, self._protecting)
        if stored_password is None:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text="Username not found")
            return

        if stored_password == self._password.get():
            update_last_login(username_value, self._protecting)
            self.clear_screen()
            Main_Menu = main_menu(self._window, self._username, self._protecting)
            Main_Menu.run()
        else:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text="Wrong Password Entered")

    # Attempt to signup the user
    def signup_pressed(self):
        self._elements["message_label"].config(text="")

        if not self.validate_inputs():
            return

        username_value = self._username.get() if hasattr(self._username, 'get') else self._username
        if user_exists(username_value, self._protecting):
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text="Username already exists")
            return

        created = create_user(username_value, self._password.get(), self._protecting, 10000, 0)
        if not created:
            self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self._elements["message_label"].config(text="Database error: could not create user")
            return

        self.clear_login_screen()
        Main_Menu = main_menu(self._window, self._username, self._protecting)
        Main_Menu.run()

    # Check if a user is set to auto login from the json save file
    def check_pre_loaded_user(self):
        data_username = get_logged_in_user(self._protecting)

        if data_username is not None:
            if not user_exists(data_username, self._protecting):
                set_logged_in_user(None, protecting=self._protecting, encrypt=False)
                return
            if hasattr(self._username, 'set'):
                self._username.set(data_username)
            else:
                self._username = data_username

            user_music = get_stored_music() or 2
            if self._music_controller:
                self._music_controller.change_track(user_music)
                saved_volume = get_music_volume()
                saved_muted = get_music_muted()
                self._music_controller.apply_saved_state(saved_volume, saved_muted)

            self.clear_screen()
            Main_Menu = main_menu(self._window, self._username, self._protecting)
            Main_Menu.run()

    # Inform the user that their account was deleted
    def acc_deleted(self):
        self.run()
        self._elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
        self._elements["message_label"].config(text="Your account was deleted")

    # Runs the file (Called remotley)
    def run_from_main_menu(self):
        self.load_utils()
        self.create_login_screen()

    # Runs the file (Called remotley)
    def run(self):
        self.load_utils()
        self.create_login_screen()
        self.check_pre_loaded_user()
