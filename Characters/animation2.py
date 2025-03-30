import pygame
from Characters.action import Action
from Characters.character import Character
from custom_logging import Logger

class AnimatedObject:
   def __init__(self, character: Character):
      self.character = character
      self.animation_speed = 100  # ms per frame
      self.frames = {}  # Хранит кадры для каждого действия
      self.current_action = Action.IDLE
      self.prev_action = None  # Добавлено для отслеживания предыдущего действия
      self.frame = 0
      self.last_update = pygame.time.get_ticks()
      self.direction = 1
      self.draw_hitbox = True  # Флаг для отключения хитбокса
      self.sound_played_for_frame = {}  # Для отслеживания воспроизведенных звуков
      self.sound_triggers = {  # Определяем, на каких кадрах какие звуки играть
         Action.JUMP: {0: Action.JUMP},
         Action.MOVE: {0: Action.MOVE}
      }

   def load_action_frames(self, action: Action, file_path: str, frame_count: int, sit_frames: bool = False):
      """Загружает кадры для конкретного действия"""
      sprite_sheet = pygame.image.load(file_path).convert_alpha()
      frame_width = sprite_sheet.get_width() // frame_count
      frame_height = sprite_sheet.get_height()

      frames = []
      for i in range(frame_count):
         frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
         if sit_frames:
            frame = pygame.transform.scale(frame, (self.character.width, self.character.sit_height))
         else:
            frame = pygame.transform.scale(frame, (self.character.width, self.character.height))
         frames.append(frame)

      self.frames[action] = frames

   def update_animation(self):
      """Обновляет кадр анимации и проверяет звуковые триггеры"""
      now = pygame.time.get_ticks()
      if now - self.last_update > self.animation_speed:
         self.last_update = now

         # Проверка звуковых триггеров перед обновлением кадра
         self._check_sound_triggers()

         # Обновление кадра
         if self.current_action == Action.JUMP:
            if self.frame < len(self.frames[self.current_action]) - 1:
               self.frame += 1
         else:
            self.frame = (self.frame + 1) % len(self.frames[self.current_action])

   def _check_sound_triggers(self):
      """Проверяет и воспроизводит звуки для текущего кадра"""
      if self.current_action in self.sound_triggers:
         frame_triggers = self.sound_triggers[self.current_action]

         if self.frame in frame_triggers:
            sound_action = frame_triggers[self.frame]
            if not self.sound_played_for_frame.get((self.current_action, self.frame), False):
               if hasattr(self.character, 'sound_obj'):
                  self.character.sound_obj.play(sound_action)
                  self.sound_played_for_frame[(self.current_action, self.frame)] = True

      # Сброс флагов при смене действия
      if self.current_action != self.prev_action:
         self.sound_played_for_frame.clear()
         self.prev_action = self.current_action

   def change_action(self, new_action: Action):
      """Меняет текущее действие"""
      if new_action != self.current_action and new_action in self.frames:
         Logger().debug(f"Change_action to: {new_action}")
         self.current_action = new_action
         self.frame = 0
         self.sound_played_for_frame.clear()  # Сбрасываем флаги звуков

   def update(self):
      """Обновляет состояние анимации"""
      self.change_action(self.character.current_action)
      self.update_animation()

   def draw(self, surface: pygame.Surface, camera_offset):
      """Отрисовывает текущий кадр"""
      player_rect = self.character.rect.move(camera_offset[0], camera_offset[1])

      if self.current_action in self.frames:


         frames = self.frames[self.current_action]
         frame = frames[self.frame]

         # Отражение при смене направления
         if self.character.direction != self.direction and self.character.direction != 0:
            self.direction = self.character.direction

         if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)


         # Отрисовываем спрайт персонажа
         surface.blit(frame, player_rect)

      # Отрисовка хитбокса (только в режиме отладки)
      if self.draw_hitbox:
         hitbox_surf = pygame.Surface((player_rect.w, player_rect.h), pygame.SRCALPHA)
         pygame.draw.rect(hitbox_surf, (255, 0, 0, 50), hitbox_surf.get_rect())
         pygame.draw.rect(hitbox_surf, (255, 0, 0, 255), hitbox_surf.get_rect(), 1)
         surface.blit(hitbox_surf, player_rect)