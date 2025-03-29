from Characters.character import Character

class Enemy(Character):
   def __init__(self, name, speed: float, strength: float):
      super().__init__(name, speed, strength)