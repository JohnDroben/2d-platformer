import pygame
import sys
from Characters.Hero.hero import Hero
from Characters.action import Action
from Characters.animation2 import AnimatedObject
from Characters.object_type import ObjectType
from Characters.Enemies.enemy import Enemy
from custom_logging import Logger

# Инициализация PyGame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Platformer Demo")
clock = pygame.time.Clock()

# Инициализация логгера
Logger().initialize()

# Загрузка шрифта
font = pygame.font.Font(None, 36)


class GameObject:
   def __init__(self, x, y, width, height, obj_type: ObjectType, color=None):
      self.rect = pygame.Rect(x, y, width, height)
      self.object_type = obj_type
      self.color = color or self._get_default_color()

   def _get_default_color(self):
      return {
         ObjectType.PLATFORM: (100, 200, 100),
         ObjectType.ENEMY: (200, 50, 50),
         ObjectType.COIN: (255, 215, 0),
      }.get(self.object_type, (200, 200, 200))

   @property
   def is_solid(self):
      return self.object_type.is_solid

   @property
   def is_dangerous(self):
      return self.object_type.is_dangerous


# Создание персонажа
ground_level = 600 - 50
player = Hero(
   x=100,
   y=ground_level - 100,
   width=60,
   height=80,
   speed=4.0,
   jump_force=12,
   gravity=0.6,
   ground_level=ground_level
)
player_anim = AnimatedObject(player)

# Создание врага - ИСПРАВЛЕНО: используем правильные параметры
enemy = Enemy(
   x=500,
   y=ground_level - 100,
   width=60,
   height=80,
   speed=2,
   jump_force=10,
   gravity=0.6,
   ground_level=ground_level
)

# ИСПРАВЛЕНО: создаем отдельную анимацию для врага
enemy_anim = AnimatedObject(enemy)  # Передаем enemy, а не player

# Загрузка анимаций
try:
   player_anim.load_action_frames(Action.IDLE, 'assets/sprites/idle.png', 7)
   player_anim.load_action_frames(Action.JUMP, 'assets/sprites/jump.png', 13)

   # ИСПРАВЛЕНО: загружаем анимации для врага (можно использовать те же или другие)
   enemy_anim.load_action_frames(Action.IDLE, 'assets/sprites/idle.png', 7)
   enemy_anim.load_action_frames(Action.JUMP, 'assets/sprites/jump.png', 13)
except Exception as e:
   Logger().error(f"Ошибка загрузки анимаций: {e}")

# Создание объектов
game_objects = [
   GameObject(0, 550, 800, 50, ObjectType.PLATFORM),
   GameObject(200, 480, 100, 20, ObjectType.PLATFORM),
   GameObject(370, 400, 100, 20, ObjectType.PLATFORM),
   GameObject(400, 200, 20, 20, ObjectType.COIN),
   GameObject(600, 250, 20, 20, ObjectType.COIN)
]

# Игровой цикл
running = True
while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

   # Управление
   keys = pygame.key.get_pressed()
   if keys[pygame.K_s]:
      player.sit_down()
   elif player.is_sitting:
      player.sit_handler.stand_up(game_objects)

   if keys[pygame.K_a]:
      player.move(-1)
   elif keys[pygame.K_d]:
      player.move(1)
   else:
      player.move(0)

   if keys[pygame.K_SPACE]:
      player.jump()

   # Обновление ИИ врага
   enemy.update_ai(game_objects)

   # Обновление физики
   player.apply_physics(game_objects, 800, 600)
   enemy.apply_physics(game_objects, 800, 600)

   # Отрисовка
   screen.fill((30, 30, 30))

   # Рисуем объекты
   for obj in game_objects:
      pygame.draw.rect(screen, obj.color, obj.rect)
      pygame.draw.rect(screen, (255, 255, 255), obj.rect, 1)

   # Отрисовка игрока и врага
   player_anim.update()
   player_anim.draw(screen, [0, 0])

   enemy_anim.update()
   enemy_anim.draw(screen, [0, 0])  # ИСПРАВЛЕНО: рисуем анимацию врага

   # UI
   health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
   coins_text = font.render(f"Coins: {player.score}", True, (255, 215, 0))
   screen.blit(health_text, (10, 10))
   screen.blit(coins_text, (10, 50))

   pygame.display.flip()
   clock.tick(60)

pygame.quit()
sys.exit()