import pygame

class SoundPlayer():
    def __init__(self, filepath="song.mp3"):
        pygame.mixer.init()
        self.filepath = filepath
        self.is_playing = False
        self.loaded = False

    def toggle(self):
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
        pygame.mixer.music.load(self.filepath)
        pygame.mixer.music.play()
        self.loaded = True
        self.is_playing = True
        return self.is_playing

    def seek(self, seconds):
        if not self.loaded:
            pygame.mixer.music.load(self.filepath)
            self.loaded = True
        pygame.mixer.music.play(start=seconds)
        self.is_playing = True
        return self.is_playing

    def status(self):
        return self.is_playing
