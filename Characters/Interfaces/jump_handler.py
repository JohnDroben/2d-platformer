from Characters.action import Action


class JumpHandler:
   def __init__(self, entity):
      self.entity = entity

   def jump(self):
      if self.entity.on_ground and not self.entity.is_sitting:
         self.entity.velocity_y = -self.entity.jump_force
         self.entity.on_ground = False
         self.entity.current_action = Action.JUMP
         # Отменяем приседание при прыжке
         if self.entity.is_sitting:
            self.entity.is_sitting = False
            self.entity.rect.height = self.entity.original_height