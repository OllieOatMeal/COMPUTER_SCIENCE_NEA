### CASINO ROYALE - MAIN

# IMPORTS

from scenes.login_scene import *
from scenes.main_menu import *
from music import *

from variables import *

class Main:
    def __init__(self):
        # Main Window
        self.window = None
        self.canvas = None

    # Function to run the main window
    def run(self):
        # Create the window with basic attributes
        self.window = Tk()
        self.window.geometry("1280x720")
        self.window.title(f'{game_name} - {game_version} | {game_creator}')
        self.window.attributes('-fullscreen', True)
        self.window.iconphoto(True, PhotoImage(file='images/icon.png'))

        self.canvas = Canvas(self.window, width=1920, height=1080)

        # Run main commands then loop the main
        Login_Scene = login(self.window)
        Music_Controller = music()
        Login_Scene.run()
        Music_Controller.run()

        self.canvas.place(x=0, y=0)
        self.window.mainloop()

if __name__ == "__main__":
    Main_Class = Main()
    Main_Class.run()