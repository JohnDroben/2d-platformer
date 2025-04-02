import random
import time
from typing import List, Tuple
import pygame
from Characters.action import Action
from Characters.animated_character import AnimatedCharacter
from Characters.type_object import ObjectType
from levels import Hole, HoleWithLift, Platform, Portal


class Enemy(AnimatedCharacter):
   def __init__(
           self,
           position: Tuple[int, int],
           size: Tuple[int, int] = (60, 80),
           speed: float = 2.0,
           jump_force: float = 9,
           gravity: float = 0.6,
           obj_type: ObjectType = ObjectType.ENEMY
   ):
      super().__init__(
         position=position,
         size=size,
         obj_type=obj_type,
         speed=speed,
         jump_force=jump_force,
         gravity=gravity,
         ground_level=2000,
         animation_config={
            "IDLE": {"file_path": "Characters/assets/sprites/player_stand.png", "frame_count": 1},
            "MOVE": {"file_path": "Characters/assets/sprites/player_walk.png", "frame_count": 2},
            "JUMP": {"file_path": "Characters/assets/sprites/player_jump.png", "frame_count": 1},
            "FALL": {"file_path": "Characters/assets/sprites/player_fall.png", "frame_count": 1}
         }
      )
      # Физические параметры
      self.jump_force = 10
      self.velocity_y = 0
      self.on_ground = False
      self.ground_level = 2000
      self.gravity = 0.6
      self.speed = 3

      # Параметры ИИ
      self.step_limit = 100
      self.current_direction = random.choice([-1, 1])
      self.step_counter = 0
      self.jump_interval = 4
      self.last_jump_time = time.time()
      self.hole_check_distance = 70
      self.safe_ground_buffer = 35
      self.respawn_position_range = (100, 300)
      self.min_direction_change_interval = 0.5
      self.last_direction_change = 0
      self.portal_check_distance = 60

   def update_ai(self, game_objects: List):
      """Обновление логики ИИ врага"""
      current_time = time.time()

      # Проверка необходимости разворота
      if self.should_reverse_direction(game_objects, current_time):
         self.reverse_direction(current_time)

      # Движение с проверкой коллизий
      self._move_with_collision_check(game_objects)

      # Прыжки с рандомизацией
      self.handle_jump(current_time)

   def apply_physics(self, game_objects: List, screen_width: int, screen_height: int):
      """Полная реализация физики врага"""
      # Гравитация и вертикальное движение
      self.velocity_y += self.gravity
      self.rect.y += self.velocity_y
      self.on_ground = False

      # Обработка вертикальных коллизий
      self._handle_vertical_collisions(game_objects, screen_height)

      # Ограничение границ экрана
      self._constrain_to_screen(screen_width, screen_height)

      # Обновление анимации
      self._update_animation_state()

   def _move_with_collision_check(self, game_objects: List):
      """Движение с проверкой горизонтальных коллизий"""
      self.rect.x += int(self.speed * self.current_direction)
      self.step_counter += 1

      # Проверка столкновений после движения
      for obj in game_objects:
         if self.rect.colliderect(obj.rect):
            if obj.object_type.is_solid and obj != self:
               # Коррекция позиции при столкновении
               if self.current_direction > 0:
                  self.rect.right = obj.rect.left
               else:
                  self.rect.left = obj.rect.right
               self._force_reverse_direction()
               break

   def _handle_vertical_collisions(self, game_objects: List, screen_height: int):
      """Обработка вертикальных столкновений"""
      for obj in game_objects:
         if not self.rect.colliderect(obj.rect):
            continue

         # Обработка платформ
         if isinstance(obj, Platform):
            in_hole = any(
               self.is_fully_inside_horizontally(self.rect, hole.rect)
               for hole in getattr(obj, 'holes', [])
            )

            if not in_hole:
               if self.velocity_y > 0:  # Падение вниз
                  self.rect.bottom = obj.rect.top
                  self.velocity_y = 0
                  self.on_ground = True
               elif self.velocity_y < 0:  # Движение вверх
                  self.rect.top = obj.rect.bottom
                  self.velocity_y = 0

         # Обработка столкновений с другими врагами
         elif obj.object_type == ObjectType.ENEMY and obj != self:
            if self.velocity_y < 0:  # Удар снизу
               self.velocity_y = -self.jump_force // 2

      # Проверка уровня земли
      if self.rect.bottom >= self.ground_level:
         self.rect.bottom = self.ground_level
         self.velocity_y = 0
         self.on_ground = True

   def _constrain_to_screen(self, screen_width: int, screen_height: int):
      """Ограничение перемещения в пределах экрана"""
      if self.rect.left < 0:
         self.rect.left = 0
         self._force_reverse_direction()
      elif self.rect.right > screen_width:
         self.rect.right = screen_width
         self._force_reverse_direction()
      if self.rect.top < 0:
         self.rect.top = 0
         self.velocity_y = 0

   def _update_animation_state(self):
      """Обновление состояния анимации"""
      if self.on_ground:
         self.current_action = Action.MOVE if abs(self.speed) > 0 else Action.IDLE
      else:
         if self.velocity_y > 5 * self.gravity:
            self.current_action = Action.FALL
         elif self.velocity_y < 0:
            self.current_action = Action.JUMP

   def _force_reverse_direction(self):
      """Немедленный разворот направления"""
      self.current_direction *= -1
      self.step_counter = 0
      self.last_direction_change = time.time()

   def should_reverse_direction(self, game_objects: List, current_time: float) -> bool:
      """Определяет необходимость разворота"""
      if current_time - self.last_direction_change < self.min_direction_change_interval:
         return False

      # Создаем область сканирования перед врагом
      scan_rect = pygame.Rect(
         self.rect.x + self.current_direction * (self.rect.width + self.hole_check_distance),
         self.rect.y,
         self.hole_check_distance,
         self.rect.height
      )

      # Проверка препятствий впереди
      for obj in game_objects:
         if scan_rect.colliderect(obj.rect):
            if isinstance(obj, (Hole, HoleWithLift, Portal)) or obj.object_type.is_solid:
               return True

      # Проверка наличия земли под ногами
      ground_check = pygame.Rect(
         scan_rect.x,
         scan_rect.bottom + 1,
         scan_rect.width,
         5
      )

      has_ground = any(
         isinstance(obj, Platform) and
         ground_check.colliderect(obj.rect) and
         not any(
            self.is_fully_inside_horizontally(ground_check, hole.rect)
            for hole in getattr(obj, 'holes', [])
         )
         for obj in game_objects
      )
      return not has_ground or self.step_counter >= self.step_limit

   def reverse_direction(self, current_time: float):
      """Разворот направления с учетом времени"""
      if current_time - self.last_direction_change >= self.min_direction_change_interval:
         self.current_direction *= -1
         self.step_counter = 0
         self.last_direction_change = current_time

   def handle_jump(self, current_time: float):
      """Обработка прыжков с рандомизацией"""
      if current_time - self.last_jump_time > self.jump_interval:
         if self.on_ground and random.random() < 0.7:
            self.jump()
            self.last_jump_time = current_time

   def jump(self):
      """Выполнение прыжка"""
      if self.on_ground:
         self.velocity_y = -self.jump_force
         self.on_ground = False
         self.current_action = Action.JUMP

   def is_fully_inside_horizontally(self, rect: pygame.Rect, hole_rect: pygame.Rect) -> bool:
      """Проверка полного нахождения внутри ямы по горизонтали"""
      return (hole_rect.left <= rect.left) and (rect.right <= hole_rect.right)

   def respawn(self, screen_width: int, screen_height: int):
      """Возрождение врага"""
      self.rect.topleft = (
         random.randint(*self.respawn_position_range),
         screen_height - 200
      )
      self.velocity_y = 0
      self.on_ground = True
      self.current_action = Action.IDLE
      self.current_direction = random.choice([-1, 1])
      self.step_counter = 0