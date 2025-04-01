import random
import time
from typing import Tuple

import pygame

from Characters.action import Action
from Characters.animated_character import AnimatedCharacter
from Characters.type_object import ObjectType


class Enemy(AnimatedCharacter):
   def __init__(
           self,
           position: Tuple[int, int],  # position - кортеж (x, y)
           size: Tuple[int, int] = (60, 80),
           speed: float = 2.0,
           jump_force: float = 9,
           gravity: float = 0.6,
           obj_type: ObjectType = ObjectType.ENEMY
   ):
      # Распаковываем кортеж position в x и y
      self.jump_force = 10
      self.ground_level = 2000
      self.gravity = 0.6
      self.velocity_y = 0
      self.step_limit = 1000
      x, y = position

      super().__init__(
         position=(x, y),  # Передаём как кортеж (или x и y по отдельности)
         size=size,
         obj_type=obj_type,
         speed=speed,
         jump_force=jump_force,
         gravity=gravity,
         ground_level=self.ground_level,
         animation_config={
            "IDLE": {"file_path": "Characters/assets/sprites/player_stand.png", "frame_count": 1},
            "MOVE": {"file_path": "Characters/assets/sprites/player_walk.png", "frame_count": 2},
            "JUMP": {"file_path": "Characters/assets/sprites/player_jump.png", "frame_count": 1},
         }
      )
      self.current_direction = 1
      self.speed = 2
      self.step_counter = 0
      self.jump_interval = 4
      self.last_jump_time = time.time()

   def jump(self):
      if self.on_ground:
         self.velocity_y = -self.jump_force
         self.on_ground = False
         self.current_action = Action.JUMP

   def update_ai(self, game_objects):
      """Обновление ИИ врага с учетом времени"""
      # Получаем текущее время
      current_time = time.time()

      # Сбрасываем флаги перед проверками
      self.platform_edge = False
      self.obstacle_detected = False

      # Проверяем условия для разворота (только если на земле)
      if self.on_ground:
         # Проверка препятствий и края платформы
         if (self.step_counter >= self.step_limit or
                 self.check_obstacles(game_objects) or
                 not self.check_platform_edge(game_objects)):
            self.current_direction *= -1
            self.step_counter = 0

         # Горизонтальное движение
         self.rect.x += int(self.speed * self.current_direction)
         self.step_counter += 1

         # Прыжок при обнаружении препятствия
         if self.obstacle_detected:
            self.jump()

         # Случайный прыжок по таймеру
         if current_time - self.last_jump_time > self.jump_interval:
            if random.random() < 0.7:  # 70% вероятность прыжка
               self.jump()
               self.last_jump_time = current_time


   def find_moving_platform(self, game_objects):
      """Ищет движущуюся платформу впереди"""
      check_rect = pygame.Rect(
         self.rect.x + self.current_direction * 100,
         self.rect.y,
         self.rect.width,
         self.rect.height
      )

      for obj in game_objects:
         if (hasattr(obj, 'object_type') and
                 obj.object_type == ObjectType.MOVING_PLATFORM and
                 obj.rect.colliderect(check_rect)):
            return obj
      return None

   def check_platform_edge(self, game_objects):
      """Проверяет наличие платформы впереди с учетом разных типов"""
      check_rect = pygame.Rect(
         self.rect.x + self.current_direction * self.rect.width,
         self.rect.bottom + 1,
         self.rect.width,
         5
      )

      for obj in game_objects:
         if obj == self or not hasattr(obj, 'object_type'):
            continue

         # Проверяем только платформы (любого типа)
         if obj.object_type.is_platform and obj.rect.colliderect(check_rect):
            return True

      return False

   def check_obstacles(self, game_objects):
      """Проверка препятствий с разной реакцией на типы объектов"""
      check_rect = pygame.Rect(
         self.rect.x + self.current_direction * 40,
         self.rect.y,
         self.rect.width,
         self.rect.height
      )

      for obj in game_objects:
         if obj == self or not hasattr(obj, 'object_type'):
            continue

         if obj.object_type.is_solid and obj.rect.colliderect(check_rect):
            # Разное поведение для разных типов
            if obj.object_type == ObjectType.MOVING_PLATFORM:
               # Может запрыгнуть на движущуюся платформу
               if random.random() < 0.3:  # 30% вероятность прыжка
                  self.jump()
                  return False
            return True

      return False

   def apply_physics(self, game_objects, screen_width, screen_height):
      prev_rect = self.rect.copy()
      self.velocity_y += self.gravity
      self.rect.y += self.velocity_y
      self.on_ground = False

      for obj in game_objects:
         if obj == self or not hasattr(obj, 'object_type'):
            continue

         if obj.object_type.is_platform and self.rect.colliderect(obj.rect):
            # Обработка для разных типов платформ
            if obj.object_type == ObjectType.MOVING_PLATFORM:
               # Движение вместе с платформой
               if prev_rect.bottom <= obj.rect.top and self.velocity_y > 0:
                  self.rect.bottom = obj.rect.top
                  self.velocity_y = 0
                  self.on_ground = True
                  # Двигаемся вместе с платформой
                  self.rect.x += obj.speed if hasattr(obj, 'speed') else 0

            elif obj.object_type == ObjectType.HOLE:
               # Может провалиться при определенных условиях
               if self.velocity_y > 0 and random.random() < 0.1:  # 10% шанс провалиться
                  continue
               # Стандартная обработка
               if prev_rect.bottom <= obj.rect.top:
                  self.rect.bottom = obj.rect.top
                  self.velocity_y = 0
                  self.on_ground = True

            else:  # Обычные платформы
               if prev_rect.bottom <= obj.rect.top and self.velocity_y > 0:
                  self.rect.bottom = obj.rect.top
                  self.velocity_y = 0
                  self.on_ground = True