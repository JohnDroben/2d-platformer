from Characters.object_type import ObjectType


class CollisionHandler:
   def __init__(self, entity):
      """
      Инициализация обработчика коллизий

      :param entity: Сущность, для которой обрабатываются коллизии
      """
      self.entity = entity

   def vertical_collision(self, game_objects, prev_rect):
      # Обработка вертикальных коллизий
      for obj in game_objects:
         if self.entity.rect.colliderect(obj.rect):
            if hasattr(obj, 'object_type') and obj.object_type.is_solid:
               if obj.object_type == ObjectType.PLATFORM:
                  if not prev_rect.colliderect(obj.rect):
                     if self.entity.velocity_y > 0:  # Падение вниз
                        self.entity.rect.bottom = obj.rect.top
                        self.entity.velocity_y = 0
                        self.entity.on_ground = True
                     elif self.entity.velocity_y < 0:  # Движение вверх
                        self.entity.rect.top = obj.rect.bottom
                        self.entity.velocity_y = 0

            if hasattr(obj, 'object_type') and obj.object_type.is_dangerous:
               # заглушка
               if obj.object_type == ObjectType.ENEMY:
                  self._dangerous_collision(obj)

            if hasattr(obj, 'object_type') and obj.object_type.is_collectible:
               self._collectible_collision(obj)


   def horizontal_collision(self, game_objects, prev_x):
      # Проверка горизонтальных коллизий
      for obj in game_objects:
         if self.entity.rect.colliderect(obj.rect):
            if hasattr(obj, 'object_type') and obj.object_type.is_solid:
               if obj.object_type == ObjectType.PLATFORM:
                  if self.entity.direction == 1:  # Вправо
                     self.entity.rect.right = obj.rect.left

                  elif self.entity.direction == -1:  # Влево
                     self.entity.rect.left = obj.rect.right

            if hasattr(obj, 'object_type') and obj.object_type.is_dangerous:
               # заглушка
               if obj.object_type == ObjectType.ENEMY:
                  # Горизонтальный контакт с врагом
                  self._dangerous_collision(obj)

            if hasattr(obj, 'object_type') and obj.object_type.is_collectible:
               self._collectible_collision(obj)

   def _dangerous_collision(self, obj):
      if self.entity.velocity_y > 0 and obj.object_type == ObjectType.ENEMY:  # Если падаем НА врага
         self.entity.take_damage(obj)
      else:
         obj.take_damage(self.entity)  # смерть

   def _collectible_collision(self, obj):
      if obj.object_type == ObjectType.COIN:
         self.entity.score += obj.collect()
      if obj.object_type == ObjectType.ARTIFACT:
         self.entity.artifact += obj.collect()