"""
Shows the credits with who made the game
"""

from tkinter import *
from variables import *


class credits_scene:
    """Credits screen"""

    def __init__(self, window, username, protecting):
        """
        Initialise credits scene
        Args:
            window: Tkinter root window
            username: Current logged-in username
            protecting: EncryptionService instance
        """
        self.window = window
        self.elements = {}
        self.main_background = None
        self.username = username
        self.protecting = protecting

    def clear_screen(self):
        """
        Remove all UI elements from the credits screen
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
        Load and create all UI elements for the credits screen
        Sets up background image, frame, and credits information
        """
        # CREATE CREDITS FRAME
        self.credits_frame = Frame(self.window, bg=frame_colour, bd=10, relief=RIDGE)
        self.credits_frame.place(relx=0.5, rely=0.1, anchor="n", width=1500, height=700)
        
        # LOAD BACKGROUND IMAGE
        try:
            self.main_background = PhotoImage(file=main_background)
        except (TclError, OSError) as e:
            print(f"Error loading images: {e}")
            print("Creating window with default background...")
            background = Label(self.window, bg='#1803A5', bd=0)
            background.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            # Create and place background only if image loaded successfully
            img_background = Label(self.window, image=self.main_background, bd=0)
            img_background.place(x=0, y=0)
            img_background.lower()

        # CREATE BACK BUTTON
        back_button = Button(self.window, text="Back", width=10, font=(font, 40, 'bold'), relief=RAISED, bd=10, 
                           bg=button_colour, activebackground=button_colour, fg='#ffffff', 
                           activeforeground='#ffffff', command=self.create_main_menu)
        
        # CREATE CREDITS LABEL
        credits_label = Label(self.credits_frame, text="Creator - Ollie O'Neill\nMusic - YouTube & Amazon Music\nCards - Vlad", 
                            font=(font, 50, 'bold'), relief=RAISED, bd=10, padx=20, bg=button_colour, fg='#ffffff')

        # STORE ELEMENTS
        self.elements = {
            "back_button": back_button,
            "credits_label": credits_label,
            "frame": self.credits_frame,
        }

    def create_quit_menu(self):
        """Position all UI elements on the credits screen"""
        self.elements["back_button"].place(x=100, y=900)
        self.elements["credits_label"].place(relx=0.5, rely=0.5, anchor=CENTER)

    def create_main_menu(self):
        """Return to main menu"""
        self.clear_screen()
        from scenes.main_menu import main_menu
        Main_Menu = main_menu(self.window, self.username, self.protecting)
        Main_Menu.run()

    def run(self):
        """
        Main entry point for credits scene
        Loads UI elements and displays credits
        """
        self.load_utils()
        self.create_quit_menu()