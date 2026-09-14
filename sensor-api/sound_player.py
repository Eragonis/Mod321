import os
os.environ["SDL_AUDIODRIVER"] = "alsa"
os.environ["AUDIODEV"] = "plughw:2,0"

import pygame

class SoundPlayer():
    def __init__(self, filepath="song.mp3"):
        self.filepath = filepath
        self.is_playing = False
        self.loaded = False
        try:
            pygame.mixer.init()
            self.available = True
        except pygame.error as e:
            print(f"Sound device not available: {e}")
            self.available = False

    def toggle(self):
        if not self.available:
            return False
        if not self.loaded:
            pygame.mixer.music.load(self.filepath)
            pygame.mixer.music.play()
            self.loaded = True
            self.is_playing = True
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
        return self.is_playing

    def restart(self):
        if not self.available:
            return False
        pygame.mixer.music.load(self.filepath)
        pygame.mixer.music.play()
        self.loaded = True
        self.is_playing = True
        return self.is_playing

    def seek(self, seconds):
        if not self.available:
            return False
        if not self.loaded:
            pygame.mixer.music.load(self.filepath)
            self.loaded = True
        pygame.mixer.music.play(start=seconds)
        self.is_playing = True
        return self.is_playing

    def status(self):
        return self.is_playing