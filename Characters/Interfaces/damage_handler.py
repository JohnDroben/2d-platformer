from Characters.object_type import ObjectType


class DamageHandler:
   def __init__(self, entity):
      self.entity = entity

   # Передаем обьект которому наносим урон
   def take_damage(obj, self):
      self.obj.health -= self.entity.damage

      if self.obj.object_type == ObjectType.PLAYER:
         if self.obj.health == 0:
            self.game_over()
         else:
            self.death()
      if self.entity.object_type == ObjectType.ENEMY:
         if self.entity.health == 0:
            self.death()

   def _death(self):
      pass

   def _game_over(self):
      pass