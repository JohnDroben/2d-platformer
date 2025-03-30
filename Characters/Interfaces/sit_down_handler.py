import pygame

from Characters.action import Action


class SitDownHandler:
   def __init__(self, entity):
      self.entity =entity
      
   def sit_down(self):
      """Приседание без проверки платформ над головой"""
      if self.entity.on_ground and not self.entity.is_sitting:
         # Сохраняем нижнюю позицию
         prev_bottom = self.entity.rect.bottom
         self.entity.rect.height = self.entity.sit_height
         self.entity.rect.bottom = prev_bottom
         self.entity.is_sitting = True
         self.entity.current_action = Action.SIT

   def can_stand_up(self, platforms):
      """Проверка, можно ли встать в текущем месте"""
      if not self.entity.is_sitting:
         return True

      # Создаем предполагаемый rect для стоячего положения
      stand_rect = pygame.Rect(
         self.entity.rect.x,
         self.entity.rect.bottom - self.entity.original_height,  # Поднимаем верхнюю границу
         self.entity.rect.width,
         self.entity.original_height
      )

      # Проверяем столкновение со всеми НЕпроходимыми платформами
      for platform in platforms:
         if hasattr(platform, 'object_type') and platform.object_type.is_solid:
            if stand_rect.colliderect(platform.rect):
               return False  # Есть коллизия с твёрдой платформой → нельзя пройти
      return True  # Нет коллизий → можно пройти

   def stand_up(self, platforms):
      """Пытается встать, если есть место"""
      if not self.entity.is_sitting:
         return True

      if not self.can_stand_up(platforms):
         return False

      # Восстанавливаем высоту, сохраняя позицию низа
      prev_bottom = self.entity.rect.bottom
      self.entity.rect.height = self.entity.original_height
      self.entity.rect.bottom = prev_bottom
      self.entity.is_sitting = False
      self.entity.current_action = Action.IDLE
      return True
