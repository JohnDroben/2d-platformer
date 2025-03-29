from Characters.character import Character

class Hero(Character):
   def __init__(self, name, speed: float, strength: float):
      super().__init__(name, speed, strength)

   def jump(self):
      """Логика прыжка и двойного прыжка"""
      if self.on_ground:
         # Обычный прыжок с земли
         self.velocity_y = -self.jump_force
         self.on_ground = False
         self.current_action = 'jump'
         self.can_double_jump = True  # Разрешаем двойной прыжок
      elif self.can_double_jump:
         # Двойной прыжок в воздухе
         self.velocity_y = -self.jump_force
         self.can_double_jump = False
         self.current_action = 'jump'
