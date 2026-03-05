"""
Main file where game is ran from.
It initiates the window, begins music player, loads the encryption/decryption, loads the login screen
"""


from tkinter import *
from scenes.login_scene import login
from music import music
from Utils.json_handler import get_stored_music, get_music_volume, get_music_muted
from Utils.encryption_service import EncryptionService
from variables import game_name, game_version, game_creator

"""
Main Class
"""
class Main:
    """
    Initiates the class with the variables: window, canvas
    """
    def __init__(self):
        self._window = None
        self._canvas = None

    def run(self):
        self._window = Tk()
        self._window.geometry("1280x720")
        self._window.title(f'{game_name} - {game_version} | {game_creator}')
        self._window.attributes('-fullscreen', True)
        self._window.iconphoto(True, PhotoImage(file='images/icon.png'))

        self._canvas = Canvas(self._window, width=1920, height=1080)

        Protecting = EncryptionService()
        Music_Controller = music()
        Login_Scene = login(self._window, Protecting, Music_Controller)
        
        Protecting.get_key()
        
        Music_Controller.run()

        saved_track = get_stored_music()
        if saved_track:
            Music_Controller.change_track(saved_track)
        Music_Controller.apply_saved_state, get_music_volume(), get_music_muted()
        Login_Scene.run()

        self._canvas.place(x=0, y=0)
        self._window.mainloop()


if __name__ == "__main__":
    Main_Class = Main()
    Main_Class.run()