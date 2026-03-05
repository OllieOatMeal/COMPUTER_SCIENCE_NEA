import pygame
from variables import *


def load_music():
    try:
        pygame.mixer.music.load(start_music)
    except pygame.error as e:
        print(f"Error loading music: {e}")


class music:
    def __init__(self):
        self._VOLUME = 50
        self._MUSIC_MUTED = False

    def volume_up(self):
        if self._VOLUME < 100:
            self._VOLUME += 10
        pygame.mixer.music.set_volume(self._VOLUME / 100)

    def volume_down(self):
        if self._VOLUME > 0:
            self._VOLUME -= 10
        pygame.mixer.music.set_volume(self._VOLUME / 100)

    def toggle_music(self):
        if not self._MUSIC_MUTED:
            pygame.mixer.music.fadeout(1000)
            self._MUSIC_MUTED = True
        else:
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self._VOLUME / 100)
            self._MUSIC_MUTED = False

    def start_music(self):
        self._VOLUME = 50
        pygame.mixer.music.play(-1, 0.0, 1000)
        pygame.mixer.music.set_volume(0.5)
        self._MUSIC_MUTED = False

    def apply_saved_state(self, volume: int | None, muted: bool | None) -> None:
        if volume is not None:
            self._VOLUME = max(0, min(100, int(volume)))
        if muted is not None:
            self._MUSIC_MUTED = bool(muted)

        if self._MUSIC_MUTED:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self._VOLUME / 100)

    def change_track(self, track_number):
        try:
            pygame.mixer.music.stop()
            
            pygame.mixer.music.load(f"{path}/music/music_{track_number}.mp3")
            
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self._VOLUME / 100)
            self._MUSIC_MUTED = False
        except pygame.error as e:
            print(f"Error loading track music_{track_number}.mp3: {e}")

    def run(self):
        pygame.mixer.init()
        load_music()
        self.start_music()
