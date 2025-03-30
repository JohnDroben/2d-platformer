from Characters.character import Character

class Hero(Character):
   def __init__(self, x, y, width, height, speed, jump_force, gravity, ground_level):
      super().__init__(x, y, width, height, speed, jump_force, gravity, ground_level)
      self.score = 0
      self.health = 3
      self.artifact = 0


