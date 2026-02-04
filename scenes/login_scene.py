"""
Login and signup screen
Lets users create an account or login to an existing one
"""

from Utils.db import get_user_password, user_exists, create_user
from tkinter import *
import sys
from scenes.main_menu import main_menu
from variables import font, button_colour, frame_colour, main_background
from music import music
from Utils.json_handler import get_logged_in_user, get_stored_music

# Input validation constants
DISALLOWED_USERNAME_CHARS = [' ', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '-', '/', '\\', '|', '{', '}', '[', ']', ':', ';', '"', "'", '<', '>', ',', '.', '?', '`', '~']
DISALLOWED_PASSWORD_CHARS = [' ', ';', '\'', '\"']
MAX_LENGTH = 12  # Maximum characters for username and password


def tkquit():
    """Close the application"""
    sys.exit()


class login:
    """The login screen where users sign in or create accounts"""

    def __init__(self, window, protecting, music_controller=None):
        """
        Initialise login scene
        Args:
            window: Tkinter root window
            protecting: EncryptionService instance
            music_controller: music controller instance
        """
        self.img_background = None
        self.window = window
        self.protecting = protecting
        self.music_controller = music_controller

        self.username = None
        self.password = None
        self.user_music = None

        self.elements = {}  # Dictionary to store UI elements
        self.main_background = None

    def clear_login_screen(self):
        """Remove all UI elements from the login screen"""
        for element in self.elements.values():
            element.place_forget()

    def load_utils(self):
        """
        Load and create all UI elements for the login screen
        Sets up background image, frames, buttons, and input fields
        """
        # CREATE MAIN FRAME
        self.login_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=700, height=700)

        # LOAD BACKGROUND IMAGE
        try:
            self.main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self.window, bg='#FF03A5', bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.img_background = Label(self.window, image=self.main_background, bd=0)
            self.img_background.place(x=0, y=0)

        # CREATE STRING VARIABLES FOR INPUT FIELDS
        self.username = StringVar()
        self.password = StringVar()

        # CREATE BUTTONS
        login_button = Button(self.login_frame, text='Login', font=(font, 12, 'bold'), width=6,
                            relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                            fg='#ffffff', activeforeground='#ffffff', command=self.login_pressed)
        signup_button = Button(self.login_frame, text='Sign Up', font=(font, 12, 'bold'),
                             relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                             fg='#ffffff', activeforeground='#ffffff', command=self.signup_pressed)
        quit_button = Button(self.window, text='Quit', font=(font, 25, 'bold'), width=9,
                           relief=RAISED, bd=10, bg=button_colour, activebackground=button_colour,
                           fg='#ffffff', activeforeground='#ffffff', command=tkquit)

        # CREATE LABELS
        enter_username_label = Label(self.login_frame, text="Enter Username", font=(font, 40, 'bold'),
                                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        enter_password_label = Label(self.login_frame, text="Enter Password", font=(font, 40, 'bold'),
                                   relief=RAISED, bd=10, bg=button_colour, fg='#ffffff')
        message_label = Label(self.login_frame, text="", font=(font, 20, 'bold'),
                            fg='#bb0000', bg='#de418e')

        # CREATE INPUT FIELDS
        username_field = Entry(self.login_frame, width=25, bg=button_colour, fg='#000000',
                             relief=RAISED, font=('Candara', 15, 'bold'), bd=10,
                             textvariable=self.username)
        password_field = Entry(self.login_frame, width=25, bg=button_colour, fg='#000000',
                             relief=RAISED, font=('Candara', 15, 'bold'), bd=10,
                             show="*", textvariable=self.password)

        # STORE ALL ELEMENTS IN DICTIONARY
        self.elements = {
            "login_button": login_button,
            "signup_button": signup_button,
            "enter_username_label": enter_username_label,
            "enter_password_label": enter_password_label,
            "username_field": username_field,
            "password_field": password_field,
            "message_label": message_label,
            "quit_button": quit_button,
            "login_frame": self.login_frame,
        }

    def create_login_screen(self):
        """Position all UI elements on the login screen"""
        self.elements["enter_username_label"].place(relx=0.5, rely=0.2, anchor=CENTER)
        self.elements["username_field"].place(relx=0.5, rely=0.3125, anchor=CENTER)
        self.elements["enter_password_label"].place(relx=0.5, rely=0.5, anchor=CENTER)
        self.elements["password_field"].place(relx=0.5, rely=0.6125, anchor=CENTER)
        self.elements["login_button"].place(relx=0.4, rely=0.9, anchor=CENTER)
        self.elements["signup_button"].place(relx=0.6, rely=0.9, anchor=CENTER)
        self.elements["quit_button"].place(relx=0.1, rely=0.9, anchor=CENTER)
        self.login_frame.lift()

    def validate_inputs(self):
        """
        Validate username and password inputs
        Checks for disallowed characters and length constraints
        Returns: bool - True if inputs are valid
        """
        username = self.username.get() if hasattr(self.username, 'get') else self.username
        password = self.password.get()

        # CHECK FOR DISALLOWED CHARACTERS IN USERNAME
        for ch in DISALLOWED_USERNAME_CHARS:
            if ch in username:
                self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
                self.elements["message_label"].config(text=f"Invalid character '{ch}' in username")
                return False

        # CHECK FOR DISALLOWED CHARACTERS IN PASSWORD
        for ch in DISALLOWED_PASSWORD_CHARS:
            if ch in password:
                self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
                self.elements["message_label"].config(text=f"Invalid character '{ch}' in password")
                return False

        # CHECK IF FIELDS ARE EMPTY
        if not username or not password:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text="Username and password cannot be empty")
            return False

        # CHECK LENGTH CONSTRAINTS
        if len(username) > MAX_LENGTH:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text=f"Username cannot be longer than {MAX_LENGTH} characters")
            return False

        if len(password) > MAX_LENGTH:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text=f"Password cannot be longer than {MAX_LENGTH} characters")
            return False

        return True

    def login_pressed(self):
        """
        Handle login button press
        Validates inputs and checks credentials against database
        Transitions to main menu on success
        """
        self.elements["message_label"].config(text="")  # Clear previous messages

        if not self.validate_inputs():
            return

        # Determine username string
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username

        # QUERY DATABASE FOR USER (centralised in Utils.db, with encryption)
        stored_password = get_user_password(username_value, self.protecting)
        if stored_password is None:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text="Username not found")
            return

        # VERIFY PASSWORD
        if stored_password == self.password.get():
            self.clear_login_screen()
            Main_Menu = main_menu(self.window, self.username, self.protecting)
            Main_Menu.run()
        else:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text="Wrong Password Entered")

    def signup_pressed(self):
        """
        Handle signup button press
        Creates new user account with default starting money
        """
        self.elements["message_label"].config(text="")  # Clear previous messages

        if not self.validate_inputs():
            return

        # CHECK IF USERNAME ALREADY EXISTS AND INSERT NEW USER
        username_value = self.username.get() if hasattr(self.username, 'get') else self.username
        if user_exists(username_value, self.protecting):
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text="Username already exists")
            return

        created = create_user(username_value, self.password.get(), self.protecting, 10000, 0)
        if not created:
            self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
            self.elements["message_label"].config(text="Database error: could not create user")
            return

        # PROCEED TO MAIN MENU
        self.clear_login_screen()
        Main_Menu = main_menu(self.window, self.username, self.protecting)
        Main_Menu.run()

    def check_pre_loaded_user(self):
        """
        Check if a user was previously logged in
        Loads user data from saved JSON file and transitions to main menu
        """
        # Use json_handler helpers which integrate with EncryptionService
        data_username = get_logged_in_user(self.protecting)

        if data_username is not None:
            # Ensure we set the StringVar if present
            if hasattr(self.username, 'set'):
                self.username.set(data_username)
            else:
                self.username = data_username

            user_music = get_stored_music() or 2
            if self.music_controller:
                self.music_controller.change_track(user_music)

            self.clear_login_screen()
            Main_Menu = main_menu(self.window, self.username, self.protecting)
            Main_Menu.run()

    def acc_deleted(self):
        """Display account deleted message and reload login screen"""
        self.run()
        self.elements["message_label"].place(relx=0.5, rely=0.75, anchor=CENTER)
        self.elements["message_label"].config(text="Your account was deleted")

    def run_from_main_menu(self):
        """
        Load and display login screen (called when logging out from main menu)
        Does not check for pre-loaded user
        """
        self.load_utils()
        self.create_login_screen()

    def run(self):
        """
        Main entry point for login scene
        Loads UI and checks for pre-loaded user
        """
        self.load_utils()
        self.create_login_screen()
        self.check_pre_loaded_user()
