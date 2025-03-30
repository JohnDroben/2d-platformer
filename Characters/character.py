import pygame

from Characters.Interfaces.collision_handler import CollisionHandler
from Characters.Interfaces.damage_handler import DamageHandler
from Characters.Interfaces.jump_handler import JumpHandler
from Characters.Interfaces.move_handler import MoveHandler
from Characters.Interfaces.sit_down_handler import SitDownHandler
from Characters.action import Action
from custom_logging import Logger


class Character:
   def __init__(self, x, y, width, height, speed, jump_force, gravity, ground_level):
      self.rect = pygame.Rect(x, y, width, height)
      self.speed = speed
      self.jump_force = jump_force
      self.width = width
      self.height = height
      self.original_height = height
      self.velocity_y = 0
      self.on_ground = True
      self.is_sitting = False  # Добавляем флаг приседания
      self.sit_height = height // 2
      self.gravity = gravity
      self.ground_level = ground_level
      self.direction = 1
      self.current_action = Action.IDLE

      # Инициализация обработчиков
      self.move_handler = MoveHandler(self)
      self.jump_handler = JumpHandler(self)
      self.sit_handler = SitDownHandler(self)
      self.collision_handler = CollisionHandler(self)
      self.damage_handler = DamageHandler(self)

   def move(self, direction):
      """Обработка движения через MoveHandler"""
      self.move_handler.move(direction)

   def jump(self):
      """Обработка прыжка через JumpHandler"""
      self.jump_handler.jump()

   def sit_down(self):
      """Обработка приседания через SitDownHandler"""
      self.sit_handler.sit_down()

   def take_damage(self, damage):
      self.damage_handler.take_damage(damage)

   def death(self):
      self.damage_handler.death()

   def apply_physics(self, game_objects, screen_width, screen_height):
      # Гравитация и вертикальное движение
      prev_rect = self.rect.copy()  # Запоминаем позицию до движения
      self.velocity_y += self.gravity
      self.rect.y += self.velocity_y
      self.on_ground = False
      # Ограничение по горизонтали
      if self.rect.left < 0:
         self.rect.left = 0
      if self.rect.right > screen_width:
         self.rect.right = screen_width

      # Ограничение по вертикали (верхняя граница)
      if self.rect.top < 0:
         self.rect.top = 0
         self.velocity_y = 0  # Сбрасываем скорость при ударе о верх

      self.collision_handler.vertical_collision(game_objects, prev_rect)

      # Проверка уровня земли (даже если нет платформ)
      if self.rect.bottom >= self.ground_level:
         self.rect.bottom = self.ground_level
         self.velocity_y = 0
         self.on_ground = True

      # Горизонтальное движение
      prev_x = self.rect.x  # Запоминаем позицию до движения
      self.rect.x += self.speed * self.direction


      self.collision_handler.horizontal_collision(game_objects, prev_x)

      # Автоматический подъем при движении/прыжке
      if self.is_sitting and (not self.on_ground or abs(self.velocity_y) > 0):
         self.sit_handler.stand_up(game_objects)
      # Автоматический сброс анимации прыжка при приземлении
      if self.on_ground:
         if self.current_action == Action.JUMP:
            # Возвращаем к анимации idle/move
            self.current_action = Action.IDLE if self.direction == 0 else Action.MOVE
      else:
         # Если в воздухе, но действие не прыжок
         if self.current_action != Action.JUMP:
            self.current_action = Action.JUMP

      after_rect = self.rect

      if abs(prev_rect.x - after_rect.x) > self.width or abs(prev_rect.y - after_rect.y) > self.height :
         Logger().debug(f"prev_rect: {prev_rect} after_rect: {after_rect}: {(prev_rect.x - after_rect.x)}")
         Logger().error("сильное смещение")