import pygame
from variables import *

def load_music():
    try:
        pygame.mixer.music.load(start_music)
    except pygame.error as e:
        print(f"Error loading music: {e}")

class music:
    def __init__(self):
        self.VOLUME = 50
        self.MUSIC_MUTED = False

    def volume_up(self):
        if self.VOLUME < 100:
            self.VOLUME += 10
            pygame.mixer.music.set_volume(self.VOLUME / 100)

    def volume_down(self):
        if self.VOLUME > 0:
            self.VOLUME -= 10
            pygame.mixer.music.set_volume(self.VOLUME / 100)

    def toggle_music(self):
        if not self.MUSIC_MUTED:
            pygame.mixer.music.fadeout(1000)
            self.MUSIC_MUTED = True
        else:
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self.VOLUME / 100)
            self.MUSIC_MUTED = False

    def start_music(self):
        self.VOLUME = 50
        pygame.mixer.music.play(-1, 0.0, 1000)
        pygame.mixer.music.set_volume(0.5)
        self.MUSIC_MUTED = False

    def change_track(self, track_number):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(f"{path}/music/music_{track_number}.mp3")
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self.VOLUME / 100)
            self.MUSIC_MUTED = False
        except pygame.error as e:
            print(f"Error loading track music_{track_number}.mp3: {e}")

    def run(self):
        pygame.mixer.init()
        load_music()
        self.start_music()
