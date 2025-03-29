import pygame


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7

    def load_sounds(self):
        # Загрузка звуков
        self.sounds = {
            'jump': pygame.mixer.Sound('assets/sounds/jump.mp3'),
            'coin': pygame.mixer.Sound('assets/sounds/coin.mp3'),
            'death': pygame.mixer.Sound('assets/sounds/death.mp3')
        }

        # Настройка громкости
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_music(self):
        pygame.mixer.music.load('assets/sounds/background.mp3')
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)  # Зацикливание

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()