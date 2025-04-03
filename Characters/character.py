import pygame
from typing import cast

from Characters.action import Action
from Characters.type_object import ObjectType
from levels.levels import Platform, MovingPlatformVertical
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
      self.on_lift = False
      self.is_sitting = False  # Добавляем флаг приседания
      self.sit_height = height // 2
      self.gravity = gravity
      self.ground_level = ground_level
      self.direction = 1
      self.current_action = Action.IDLE

   def teleport (self, x, y):
      self.rect.x = x
      self.rect.y = y

   def move(self, direction):
      self.direction = direction
      if direction != 0:
         if self.on_ground:  # Меняем анимацию только на земле
            if self.is_sitting:
               self.current_action = Action.SIT_MOVE
            else:
               self.current_action = Action.MOVE
      else:
         if self.on_ground:
            if self.is_sitting:
               self.current_action = Action.SIT_IDLE
            else:
               self.current_action = Action.IDLE

   def jump(self):

      if self.on_ground and not self.is_sitting:
         self.velocity_y = -self.jump_force
         self.on_ground = False
         self.current_action = Action.JUMP
         # Отменяем приседание при прыжке
         if self.is_sitting:
            self.is_sitting = False
            self.rect.height = self.original_height

   def sit_down(self):
      """Приседание без проверки платформ над головой"""
      if self.on_ground and not self.is_sitting:
         # Сохраняем нижнюю позицию
         prev_bottom = self.rect.bottom
         self.rect.height = self.sit_height
         self.rect.bottom = prev_bottom
         self.is_sitting = True
         self.current_action = Action.SIT

   def can_stand_up(self, platforms):
      """Проверка, можно ли встать в текущем месте"""
      if not self.is_sitting:
         return True

      # Создаем предполагаемый rect для стоячего положения
      stand_rect = pygame.Rect(
         self.rect.x,
         self.rect.bottom - self.original_height,  # Поднимаем верхнюю границу
         self.rect.width,
         self.original_height
      )

      # Проверяем столкновение со всеми НЕпроходимыми платформами
      for platform in platforms:
         if platform.object_type in (ObjectType.PLATFORM, ObjectType.MOVING_PLATFORM):  # Только обычные платформы
            if stand_rect.colliderect(platform.rect):
               return False
      return True

   def stand_up(self, platforms):
      """Пытается встать, если есть место"""
      if not self.is_sitting:
         return True

      if not self.can_stand_up(platforms):
         return False

      # Восстанавливаем высоту, сохраняя позицию низа
      prev_bottom = self.rect.bottom
      self.rect.height = self.original_height
      self.rect.bottom = prev_bottom
      self.is_sitting = False
      self.current_action = Action.IDLE
      return True

   def is_fully_inside_horizontally(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
      """
      Проверяет, помещается ли rect1 полностью внутри rect2 по горизонтали.

      :param rect1: Хитбокс первого объекта
      :param rect2: Хитбокс второго объекта
      :return: True, если rect1 полностью внутри rect2 по горизонтали, иначе False
      """
      return rect2.left <= rect1.left and rect1.right <= rect2.right

   def is_centr_inside_horizontally(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
      """
      Проверяет, находится ли цента rect1 внутри rect2 по горизонтали.

      :param rect1: Хитбокс первого объекта
      :param rect2: Хитбокс второго объекта
      :return: True, если rect1 полностью внутри rect2 по горизонтали, иначе False
      """
      return rect2.left <= rect1.center[0] <= rect2.right

   def apply_physics(self, game_objects, screen_width, screen_height):
      # Гравитация и вертикальное движение
      prev_rect = self.rect.copy()  # Запоминаем позицию до движения
      self.velocity_y += self.gravity
      self.rect.y += self.velocity_y
      self.on_ground = False
      self.on_lift = False
      # Ограничение по горизонтали
      if self.rect.left < 0:
         self.rect.left = 0
      if self.rect.right > screen_width:
         self.rect.right = screen_width

      # Ограничение по вертикали (верхняя граница)
      if self.rect.top < 0:
         self.rect.top = 0
         self.velocity_y = 0  # Сбрасываем скорость при ударе о верх
      # Обработка вертикальных коллизий
      for obj in game_objects:
         if self.rect.colliderect(obj.rect):
            # Платформы (физические коллизии)
            if obj.object_type is ObjectType.PLATFORM:

               platform = cast(Platform, obj)  # Явное приведение типа
               in_hole = False
               holes = getattr(platform, 'holes', [])  #берём люки с платформы если они есть.
               for hole in holes:
                  if self.is_centr_inside_horizontally(self.rect, hole.rect):
                     in_hole = True
                     break
               if not prev_rect.colliderect(obj.rect) and not in_hole:

                  if self.velocity_y > 0:  # Падение вниз
                     self.rect.bottom = obj.rect.top
                     self.velocity_y = 0
                     self.on_ground = True
                     self.can_double_jump = False
                  elif self.velocity_y < 0:  # Движение вверх
                     self.rect.top = obj.rect.bottom
                     self.velocity_y = 0

            if obj.object_type is ObjectType.MOVING_PLATFORM:

               mov_platform = cast(MovingPlatformVertical, obj)  # Явное приведение типа
               if self.is_centr_inside_horizontally(self.rect, mov_platform.rect):
                  if self.rect.bottom < mov_platform.rect.bottom:
                     self.on_lift = True


               if self.on_lift:
                  self.on_ground = True
                  self.velocity_y = mov_platform.speed * mov_platform.direction
                  if self.velocity_y > 0:  # Падение вниз
                     self.rect.bottom = obj.rect.top
                     self.can_double_jump = False

                  elif self.velocity_y < 0:  # Движение вверх
                     self.rect.bottom = mov_platform.rect.top
                     #self.velocity_y = 0
                     pass

            # Враги (тxриггер)
            elif obj.object_type == ObjectType.ENEMY:
               if self.velocity_y > 0:  # Если падаем НА врага
                  pass
                  # self.take_damage(10)
               elif self.velocity_y < 0:  # Если прыгаем ВО врага
                  self.velocity_y = -self.jump_force // 2  # Отскок

      # Проверка уровня земли (даже если нет платформ)
      if self.rect.bottom >= self.ground_level:
         self.rect.bottom = self.ground_level
         self.velocity_y = 0
         self.on_ground = True

      # Горизонтальное движение и коллизии
      prev_x = self.rect.x  # Запоминаем позицию до движения
      self.rect.x += self.speed * self.direction

      # Проверка горизонтальных коллизий
      for obj in game_objects:
         if self.rect.colliderect(obj.rect):
            # Блокировка движения через платформы
            if obj.object_type == ObjectType.PLATFORM:

               platform = cast(Platform, obj)  # Явное приведение типа
               in_hole = False
               holes = getattr(platform, 'holes', [])  # берём люки с платформы если они есть.
               for hole in holes:
                  if self.is_centr_inside_horizontally(prev_rect, hole.rect):
                     in_hole = True
                     if self.direction == 1:  # Вправо
                        if self.rect.right > hole.rect.right:
                           self.rect.right = hole.rect.right
                     elif self.direction == -1:  # Влево
                        if self.rect.left < hole.rect.left:
                           self.rect.left = hole.rect.left
                     break
               if not in_hole:
                  if self.direction == 1:  # Вправо
                     self.rect.right = obj.rect.left

                  elif self.direction == -1:  # Влево
                     self.rect.left = obj.rect.right

            # Горизонтальный контакт с врагом
            elif obj.object_type == ObjectType.ENEMY:
               #self.take_damage(20)
               self.rect.x = prev_x  # Отмена движения
      # Отдельный проход для триггеров (монетки, бонусы)
      for obj in game_objects[:]:  # Копия списка для безопасного удаления
         if self.rect.colliderect(obj.rect):
            if obj.object_type == ObjectType.COIN:
               #self.collect_coin(1)
               game_objects.remove(obj)
            # elif obj.object_type == "health_pack":
            #    #self.heal(25)
            #    game_objects.remove(obj)

      # Автоматический подъем при движении/прыжке
      if self.is_sitting and (not self.on_ground or abs(self.velocity_y) > 0):
         self.stand_up(game_objects)
      # Автоматический сброс анимации прыжка при приземлении
      if self.on_ground:
         if self.current_action in (Action.JUMP, Action.FALL):
            # Возвращаем к анимации idle/move
            self.current_action = Action.IDLE if self.direction == 0 else Action.MOVE
      else:
         # Если в воздухе, но действие не прыжок
         FALL_THRESHOLD_VELOCITY =  5*self.gravity
         if self.velocity_y > FALL_THRESHOLD_VELOCITY:
            if self.current_action != Action.JUMP:
               self.current_action = Action.FALL

      after_rect = self.rect

      if abs(prev_rect.x - after_rect.x) > self.width or abs(prev_rect.y - after_rect.y) > self.height :
         Logger().debug(f"prev_rect: {prev_rect} after_rect: {after_rect}: {(prev_rect.x - after_rect.x)}")
         Logger().error("Слишком больше смещение")