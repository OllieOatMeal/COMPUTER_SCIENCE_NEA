"""
Music Module
Purpose: Manages audio playback, volume control, and track switching
Uses Pygame mixer for audio handling
"""

import pygame
from variables import *


def load_music():
    """
    Load the default starting music file
    Handles pygame.error exceptions gracefully
    """
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
        """Initialise music controller with default settings"""
        self.VOLUME = 50  # Default volume as percentage
        self.MUSIC_MUTED = False

    def volume_up(self):
        """
        Increase volume by 10% (maximum 100%)
        Updates pygame mixer immediately
        """
        if self.VOLUME < 100:
            self.VOLUME += 10
            pygame.mixer.music.set_volume(self.VOLUME / 100)

    def volume_down(self):
        """
        Decrease volume by 10% (minimum 0%)
        Updates pygame mixer immediately
        """
        if self.VOLUME > 0:
            self.VOLUME -= 10
            pygame.mixer.music.set_volume(self.VOLUME / 100)

    def toggle_music(self):
        """
        Toggle music mute state
        Either fade out or resume playback based on current state
        """
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
        self.VOLUME = 50
        pygame.mixer.music.play(-1, 0.0, 1000)
        pygame.mixer.music.set_volume(0.5)
        self.MUSIC_MUTED = False

    def change_track(self, track_number):
        """
        Change to a different music track
        Args: track_number (int) - track identifier
        Handles file loading errors gracefully
        """
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
        pygame.mixer.init()
        load_music()
        self.start_music()
