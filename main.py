"""
CASINO ROYALE - Main Application Module
Author: Ollie O'Neill
Purpose: Entry point for the Casino Royale gaming application
Initialises the GUI window and orchestrates scene management
"""

# IMPORTS
from scenes.login_scene import *
from scenes.main_menu import *
from music import *
from Utils.encryption_service import EncryptionService
from variables import *


class Main:
    """
    Main application controller
    Manages window creation and scene transitions
    """

    def __init__(self):
        """Initialise the main application"""
        self.window = None  # Tkinter root window
        self.canvas = None  # Canvas for drawing

    def run(self):
        """
        Run the main application
        Creates window, initialises services, and starts login scene
        """
        # WINDOW INITIALISATION
        self.window = Tk()
        self.window.geometry("1280x720")
        self.window.title(f'{game_name} - {game_version} | {game_creator}')
        self.window.attributes('-fullscreen', True)
        self.window.iconphoto(True, PhotoImage(file='images/icon.png'))

        # CANVAS SETUP
        self.canvas = Canvas(self.window, width=1920, height=1080)

        # INITIALISE SERVICES AND SCENES
        Protecting = EncryptionService()  # Create encryption service
        Music_Controller = music()  # Create music controller
        Login_Scene = login(self.window, Protecting, Music_Controller)  # Create login scene
        
        # GET ENCRYPTION KEY
        Protecting.get_key()
        
        # START MUSIC AND LOGIN SCREEN
        Music_Controller.run()
        Login_Scene.run()

        # DISPLAY CANVAS AND START MAIN LOOP
        self.canvas.place(x=0, y=0)
        self.window.mainloop()


if __name__ == "__main__":
    Main_Class = Main()
    Main_Class.run()