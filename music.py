"""
Handles music and audio volume for the game
"""

import pygame
from variables import *


def load_music():
    """Load the main music file"""
    # Just try to load the default track on startup
    try:
        pygame.mixer.music.load(start_music)
    except pygame.error as e:
        print(f"Error loading music: {e}")


class music:
    """
    Music controller for handling volume and track management
    Controls playback state and audio settings
    """

    def __init__(self):
        """
        Start with volume at 50%
        """
        # Default audio state for a fresh session
        self.VOLUME = 50
        self.MUSIC_MUTED = False

    def volume_up(self):
        """
        Increase volume by 10% (maximum 100%)
        Updates pygame mixer immediately
        """
        # Bump volume and sync it with the mixer
        if self.VOLUME < 100:
            self.VOLUME += 10
        pygame.mixer.music.set_volume(self.VOLUME / 100)

    def volume_down(self):
        """
        Decrease volume by 10% (minimum 0%)
        Updates pygame mixer immediately
        """
        # Drop volume and sync it with the mixer
        if self.VOLUME > 0:
            self.VOLUME -= 10
        pygame.mixer.music.set_volume(self.VOLUME / 100)

    def toggle_music(self):
        """
        Toggle music mute state
        Either fade out or resume playback based on current state
        """
        # Flip between muted and playing
        if not self.MUSIC_MUTED:
            # Fade out over 1 second
            pygame.mixer.music.fadeout(1000)
            self.MUSIC_MUTED = True
        else:
            # Resume playback
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self.VOLUME / 100)
            self.MUSIC_MUTED = False

    def start_music(self):
        """
        Initialise and start music playback with default settings
        Sets volume to 50% and begins looped playback
        """
        # Reset to defaults and start looping
        self.VOLUME = 50
        pygame.mixer.music.play(-1, 0.0, 1000)
        pygame.mixer.music.set_volume(0.5)
        self.MUSIC_MUTED = False

    def apply_saved_state(self, volume: int | None, muted: bool | None) -> None:
        """Apply saved volume/mute state to the mixer and controller."""
        # Pull in last saved settings if we have them
        if volume is not None:
            self.VOLUME = max(0, min(100, int(volume)))
        if muted is not None:
            self.MUSIC_MUTED = bool(muted)

        if self.MUSIC_MUTED:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.VOLUME / 100)

    def change_track(self, track_number):
        """
        Change to a different music track
        Args: track_number (int) - track identifier
        Handles file loading errors gracefully
        """
        # Swap to a new track and keep volume steady
        try:
            # Stop current playback
            pygame.mixer.music.stop()
            
            # Load new track from file
            pygame.mixer.music.load(f"{path}/music/music_{track_number}.mp3")
            
            # Start playback with current volume
            pygame.mixer.music.play(-1, 0.0, 1000)
            pygame.mixer.music.set_volume(self.VOLUME / 100)
            self.MUSIC_MUTED = False
        except pygame.error as e:
            print(f"Error loading track music_{track_number}.mp3: {e}")

    def run(self):
        """
        Initialise pygame mixer and start default music playback
        Called once during application startup
        """
        # Boot the mixer and start background music
        pygame.mixer.init()
        load_music()
        self.start_music()
