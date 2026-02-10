from tkinter import *
from scenes.login_scene import login
from music import music
from Utils.json_handler import get_stored_music, get_music_volume, get_music_muted
from Utils.encryption_service import EncryptionService
from variables import game_name, game_version, game_creator


class Main:
    def __init__(self):
        self.window = None
        self.canvas = None

    def run(self):
        self.window = Tk()
        self.window.geometry("1280x720")
        self.window.title(f'{game_name} - {game_version} | {game_creator}')
        self.window.attributes('-fullscreen', True)
        self.window.iconphoto(True, PhotoImage(file='images/icon.png'))

        self.canvas = Canvas(self.window, width=1920, height=1080)

        Protecting = EncryptionService()
        Music_Controller = music()
        Login_Scene = login(self.window, Protecting, Music_Controller)
        
        Protecting.get_key()
        
        Music_Controller.run()

        saved_track = get_stored_music()
        if saved_track:
            Music_Controller.change_track(saved_track)
        Music_Controller.apply_saved_stateget_music_volume(), get_music_muted()
        Login_Scene.run()

        self.canvas.place(x=0, y=0)
        self.window.mainloop()


if __name__ == "__main__":
    Main_Class = Main()
    Main_Class.run()