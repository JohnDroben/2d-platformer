import pygame

from Characters.action import Action


class SoundObject:
   def __init__(self, target_object):
      """
      :param target_object: Объект, к которому привязаны звуки (персонаж, платформа и т.д.)
      """
      self.target = target_object
      self.sounds = {}  # Словарь для хранения звуков {SoundAction: [sound1, sound2]}
      self.current_action = None
      self.volume = 1.0  # Громкость по умолчанию

   def load_sounds(self, action: Action, file_paths: list[str]):
      """
      Загружает звуки для конкретного действия
      :param action: Тип действия (SoundAction.JUMP и т.д.)
      :param file_paths: Список путей к файлам со звуками
      """
      loaded_sounds = []
      for path in file_paths:
         try:
            sound = pygame.mixer.Sound(path)
            loaded_sounds.append(sound)
         except Exception as e:
            print(f"Error loading sound {path}: {e}")

      if loaded_sounds:
         self.sounds[action] = loaded_sounds

   def set_volume(self, volume: float):
      """Устанавливает громкость всех звуков (0.0 - 1.0)"""
      self.volume = volume
      for sound_list in self.sounds.values():
         for sound in sound_list:
            sound.set_volume(volume)

   def play(self, action: Action, loop=0, fade_ms=0):
      """
      Воспроизводит звук для указанного действия
      :param action: Тип действия
      :param loop: Количество повторов (-1 для бесконечного)
      :param fade_ms: Плавное нарастание громкости (в мс)
      """
      if action in self.sounds and self.sounds[action]:
         sound = self.sounds[action][0]  # Берем первый звук из списка
         sound.set_volume(self.volume)
         sound.play(loops=loop, fade_ms=fade_ms)
         self.current_action = action

   def play_random(self, action: Action, loop=0, fade_ms=0):
      """
      Воспроизводит случайный звук из доступных для действия
      """
      if action in self.sounds and self.sounds[action]:
         import random
         sound = random.choice(self.sounds[action])
         sound.set_volume(self.volume)
         sound.play(loops=loop, fade_ms=fade_ms)
         self.current_action = action

   def stop(self, action: Action = None, fade_ms=0):
      """Останавливает звук"""
      if action is None:
         action = self.current_action
      if action in self.sounds:
         for sound in self.sounds[action]:
            sound.fadeout(fade_ms)

   def update(self):
      """Обновляет состояние звуков (например, проверка условий)"""
      pass  # Можно добавить логику автоматического воспроизведения