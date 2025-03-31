import pygame


class SoundManager:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 128)  # Оптимизация буфера
        pygame.mixer.set_num_channels(8)  # Установка количества каналов
        self.sounds = {}
        self.music_volume = 0.2
        self.sfx_volume = 0.7

    def load_sounds(self):
        # Загрузка звуков в формате WAV
        self.sounds = {
            'jump': pygame.mixer.Sound('Sounds/jump.wav'),
            'coin': pygame.mixer.Sound('Sounds/coin.wav'),
            'death': pygame.mixer.Sound('Sounds/death.wav')
        }

        # Настройка громкости
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_music(self):
        pygame.mixer.music.load('Sounds/background.wav')
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)  # Зацикливание

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()