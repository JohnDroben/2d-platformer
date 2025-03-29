import pygame

from Characters.action import Action
from Characters.character import Character
from Characters.animation2 import AnimatedObject
from Characters.type_object import ObjectType

# Инициализация PyGame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Platformer Demo")
clock = pygame.time.Clock()

# Загрузка шрифта
font = pygame.font.Font(None, 36)


class GameObject:
   def __init__(self, x, y, width, height, obj_type: ObjectType, color=None):
      self.rect = pygame.Rect(x, y, width, height)
      self.object_type = obj_type  # Используем ObjectType вместо строки
      self.color = color or self._get_default_color()

   def _get_default_color(self):
      """Возвращает цвет по умолчанию для типа объекта"""
      return {
         ObjectType.PLATFORM: (100, 200, 100),
         #ObjectType.PASSABLE_PLATFORM: (150, 200, 150),
         ObjectType.ENEMY: (200, 50, 50),
         ObjectType.COIN: (255, 215, 0),
         #ObjectType.SPIKE: (150, 50, 50),
         #ObjectType.CHECKPOINT: (0, 200, 200),
         #ObjectType.DOOR: (200, 100, 50),
         #ObjectType.POWERUP: (150, 50, 200)
      }.get(self.object_type, (200, 200, 200))  # Серый по умолчанию

   @property
   def is_solid(self):
      return self.object_type.is_solid

   @property
   def is_dangerous(self):
      return self.object_type.is_dangerous

# Создание персонажа
ground_level = 600-50
player = Character(
    x=100,  # Стартовая позиция X (не привязывать к ground_level)
    y=ground_level - 100,  # Ставим на поверхность (ground_level - высота)
    width=60,  # Ширина hitbox (рекомендую уменьшить)
    height=80,  # Высота hitbox (рекомендую уменьшить)
    speed=4.0,  # Оптимальная скорость движения
    jump_force=12,  # Сила прыжка
    gravity=0.6,  # Гравитация
    ground_level=ground_level  # Уровень земли
)
player_anim = AnimatedObject(player)

# Для каждого действия указываем файл и количество кадров
player_anim.load_action_frames(Action.IDLE, 'assets/sprites/idle.png', 7)
# player_anim.load_action_frames('move', 'assets/run.png', 6)
player_anim.load_action_frames(Action.JUMP, 'assets/sprites/jump.png', 13)

# Создание объектов
game_objects = [
   GameObject(0, 550, 800, 50, ObjectType.PLATFORM, (100, 200, 100)),  # Пол
   GameObject(200, 480, 100, 20, ObjectType.PLATFORM, (100, 200, 100)),  # Платформа 1
   GameObject(370, 400, 100, 20, ObjectType.PLATFORM, (100, 200, 100)),  # Платформа 2
   GameObject(100, 300, 40, 40, ObjectType.ENEMY, (200, 50, 50)),  # Враг
   GameObject(400, 200, 20, 20, ObjectType.COIN, (255, 215, 0)),  # Монетка
   GameObject(600, 250, 20, 20, ObjectType.COIN, (255, 215, 0))  # Монетка
]

# Игровой цикл
running = True
while running:
   # Обработка событий
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

   # Управление
   keys = pygame.key.get_pressed()
   player.direction = 0

   if keys[pygame.K_s]:
      player.sit_down()
   else:
      if player.is_sitting:
         player.stand_up(game_objects)

   if keys[pygame.K_a]:
      player.move(-1)
   if keys[pygame.K_d]:
      player.move(1)
   if keys[pygame.K_s]:
      player.sit_down()
      # Приседание (без проверки)
      # Вставание (с проверкой)
   elif player.is_sitting:
      player.stand_up(game_objects)  # передаем список всех объектов

      # Автоматическое вставание при прыжке/движении
      if (keys[pygame.K_SPACE] or
              (player.is_sitting and (keys[pygame.K_a] or keys[pygame.K_d]))):
         player.stand_up(game_objects)

   if keys[pygame.K_SPACE]:
      player.jump()

   # Обновление физики

   # Отрисовка
   screen.fill((30, 30, 30))  # Темно-серый фон

   # Рисуем объекты
   for obj in game_objects:
      pygame.draw.rect(screen, obj.color, obj.rect)
      # Рисуем хитбоксы для демо
      pygame.draw.rect(screen, (255, 255, 255), obj.rect, 1)

   # В основном цикле отрисовки
   player.apply_physics(game_objects, 800, 600)
   pygame.draw.line(screen, (255, 0, 0), (0, player.ground_level), (800, player.ground_level))

   # Обновление анимации
   player_anim.update()
   player_anim.draw(screen)

   # Интерфейс
   # health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
   # coins_text = font.render(f"Coins: {player.coins}", True, (255, 215, 0))
   # screen.blit(health_text, (10, 10))
   # screen.blit(coins_text, (10, 50))

   pygame.display.flip()
   clock.tick(60)

pygame.quit()