import pygame
import random
import time
from Characters.character import Character
from Characters.object_type import ObjectType


class Enemy(Character):
   def __init__(self, x, y, width, height, speed, jump_force, gravity, ground_level):
      super().__init__(x, y, width, height, speed, jump_force, gravity, ground_level)
      self.health = 1
      self.step_counter = 0
      self.current_direction = 1  # 1 - вправо, -1 - влево
      self.platform_edge = False
      self.obstacle_detected = False
      self.last_jump_time = time.time()  # Время последнего прыжка
      self.jump_interval = 4  # Интервал между прыжками в секундах

   def update_ai(self, game_objects):
      """Основная логика ИИ врага"""
      current_time = time.time()

      # Сбрасываем флаги перед новой проверкой
      self.platform_edge = False
      self.obstacle_detected = False

      # Проверка условий для разворота
      if self.step_counter >= 10 or self.check_obstacles(game_objects):
         self.current_direction *= -1
         self.step_counter = 0

      # Проверка края платформы
      if not self.check_platform_edge(game_objects):
         self.current_direction *= -1
         self.step_counter = 0

      # Движение
      self.move(self.current_direction)
      self.step_counter += 1

      # Прыжок при обнаружении препятствия
      if self.obstacle_detected and self.on_ground:
         self.jump()

      # Случайный прыжок раз в 4 секунды
      if current_time - self.last_jump_time > self.jump_interval and self.on_ground:
         if random.random() < 0.7:  # 70% вероятность прыжка
            self.jump()
            self.last_jump_time = current_time

   def check_obstacles(self, game_objects):
      """Проверка наличия препятствий"""
      check_rect = self.rect.copy()
      check_rect.x += self.current_direction * 40

      for obj in game_objects:
         if obj == self:
            continue
         if obj.rect.colliderect(check_rect):
            if hasattr(obj, 'object_type'):
               if obj.object_type.is_solid and obj.object_type not in [ObjectType.PASSABLE_PLATFORM]:
                  self.obstacle_detected = True
                  return True
      return False

   def check_platform_edge(self, game_objects):
      """Проверка края платформы"""
      check_rect = self.rect.copy()
      check_rect.y += 2
      check_rect.x += self.current_direction * self.rect.width

      platform_found = False
      for obj in game_objects:
         if obj == self:
            continue
         if obj.rect.colliderect(check_rect):
            if hasattr(obj, 'object_type'):
               if obj.object_type in [ObjectType.PLATFORM, ObjectType.MOVING_PLATFORM]:
                  platform_found = True
                  break
      return platform_found

   def move(self, direction):
      """Переопределяем метод движения"""
      super().move(direction)

   def jump(self):
      """Переопределяем метод прыжка"""
      if self.on_ground:
         super().jump()