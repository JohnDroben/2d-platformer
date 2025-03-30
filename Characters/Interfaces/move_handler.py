from Characters.action import Action


class MoveHandler:
   def __init__(self, entity):
      self.entity = entity

   def move(self, direction):
      self.entity.direction = direction
      if direction != 0:
         if self.entity.on_ground:  # Меняем анимацию только на земле
            if self.entity.is_sitting:
               self.entity.current_action = Action.SIT_MOVE
            else:
               self.entity.current_action = Action.MOVE

      # Применяем физическое перемещение
      self.entity.rect.x += self.entity.speed * direction

      # Если движение остановилось - обновляем анимацию
      if direction == 0 and self.entity.on_ground:
         if self.entity.is_sitting:
            self.entity.current_action = Action.SIT_IDLE
         else:
            self.entity.current_action = Action.IDLE