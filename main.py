"""
Main entry point for my Casino Royale game
Sets up the window and starts the login scene
"""

# IMPORTS
from tkinter import *
from scenes.login_scene import login
from music import music
from Utils.encryption_service import EncryptionService
from variables import game_name, game_version, game_creator


class Main:
    """Main window and scene controller for the game"""

    def __init__(self):
        """Set up the main window"""
        self.window = None  # Tkinter root window
        self.canvas = None  # Canvas for drawing

    def run(self):
        """Start the application and show the login screen"""
        # WINDOW INITIALISATION
        self.window = Tk()
        self.window.geometry("1280x720")
        self.window.title(f'{game_name} - {game_version} | {game_creator}')
        self.window.attributes('-fullscreen', True)
        self.window.iconphoto(True, PhotoImage(file='images/icon.png'))

        # CANVAS SETUP
        self.canvas = Canvas(self.window, width=1920, height=1080)

        # INITIALISE SERVICES AND SCENES
        Protecting = EncryptionService()  # Set up encryption
        Music_Controller = music()  # Set up music player
        Login_Scene = login(self.window, Protecting, Music_Controller)  # Create login
        
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