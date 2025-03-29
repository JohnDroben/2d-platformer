import pygame
import sys
import random
import math
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Платформер с анимацией")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GROUND_COLOR = (100, 70, 0)
SKY_COLOR = (135, 206, 235)
RED = (255, 0, 0)

# Шрифт
try:
    font = pygame.font.SysFont('Arial', 24)
except:
    font = pygame.font.Font(None, 24)


class Character:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.width = 30
        self.height = 50
        self.speed = 5
        self.jump_power = 15
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = True
        self.facing_right = True

        # Параметры анимации
        self.arm_angle = 0
        self.leg_angle = 0
        self.animation_speed = 0.2
        self.is_walking = False

    def update(self, platforms):
        # Применяем гравитацию
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Проверка нахождения на земле или платформах
        self.on_ground = False
        if self.y + self.height >= SCREEN_HEIGHT - 50:
            self.y = SCREEN_HEIGHT - 50 - self.height
            self.velocity_y = 0
            self.on_ground = True

        for platform in platforms:
            if (self.x < platform.rect.x + platform.rect.width and
                    self.x + self.width > platform.rect.x and
                    self.y + self.height > platform.rect.y and
                    self.y < platform.rect.y + platform.rect.height and
                    self.velocity_y > 0):
                self.y = platform.rect.y - self.height
                self.velocity_y = 0
                self.on_ground = True

        # Анимация ходьбы
        if self.is_walking:
            self.arm_angle = math.sin(pygame.time.get_ticks() * 0.01) * 30
            self.leg_angle = math.sin(pygame.time.get_ticks() * 0.01) * 20
        else:
            # Плавное возвращение в исходное положение
            self.arm_angle *= 0.9
            self.leg_angle *= 0.9

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False

    def draw(self, surface):
        # Тело
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, RED, body_rect)

        # Голова
        head_radius = self.width // 2
        head_x = self.x + self.width // 2
        head_y = self.y - head_radius
        pygame.draw.circle(surface, (255, 200, 150), (head_x, head_y), head_radius)

        # Глаза
        eye_offset = 5 if self.facing_right else -5
        pygame.draw.circle(surface, BLACK, (head_x + eye_offset, head_y - 5), 3)

        # Руки
        arm_length = self.width * 0.8
        arm_start_x = self.x + self.width // 2
        arm_start_y = self.y + self.height // 3

        # Левая рука
        left_arm_angle = -self.arm_angle if self.facing_right else 180 + self.arm_angle
        left_arm_end_x = arm_start_x + arm_length * math.cos(math.radians(left_arm_angle))
        left_arm_end_y = arm_start_y + arm_length * math.sin(math.radians(left_arm_angle))
        pygame.draw.line(surface, (255, 200, 150), (arm_start_x, arm_start_y),
                         (left_arm_end_x, left_arm_end_y), 5)

        # Правая рука
        right_arm_angle = self.arm_angle if self.facing_right else 180 - self.arm_angle
        right_arm_end_x = arm_start_x + arm_length * math.cos(math.radians(right_arm_angle))
        right_arm_end_y = arm_start_y + arm_length * math.sin(math.radians(right_arm_angle))
        pygame.draw.line(surface, (255, 200, 150), (arm_start_x, arm_start_y),
                         (right_arm_end_x, right_arm_end_y), 5)

        # Ноги
        leg_length = self.width
        leg_start_x = self.x + self.width // 2
        leg_start_y = self.y + self.height

        # Левая нога
        left_leg_angle = -self.leg_angle if self.facing_right else 20 + self.leg_angle
        left_leg_end_x = leg_start_x + leg_length * math.cos(math.radians(left_leg_angle))
        left_leg_end_y = leg_start_y + leg_length * math.sin(math.radians(left_leg_angle))
        pygame.draw.line(surface, BLUE, (leg_start_x, leg_start_y),
                         (left_leg_end_x, left_leg_end_y), 5)

        # Правая нога
        right_leg_angle = self.leg_angle if self.facing_right else 20 - self.leg_angle
        right_leg_end_x = leg_start_x + leg_length * math.cos(math.radians(right_leg_angle))
        right_leg_end_y = leg_start_y + leg_length * math.sin(math.radians(right_leg_angle))
        pygame.draw.line(surface, BLUE, (leg_start_x, leg_start_y),
                         (right_leg_end_x, right_leg_end_y), 5)


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, self.rect)


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = []
        self.setup_level()

    def setup_level(self):
        self.platforms = []

        if self.level_num == 1:
            self.platforms.append(Platform(200, 400, 100, 20))
            self.platforms.append(Platform(400, 300, 100, 20))
            self.platforms.append(Platform(600, 400, 100, 20))
        else:
            self.platforms.append(Platform(150, 450, 80, 20))
            self.platforms.append(Platform(300, 350, 80, 20))
            self.platforms.append(Platform(450, 250, 80, 20))
            self.platforms.append(Platform(600, 350, 80, 20))

    def draw(self, surface):
        # Земля
        pygame.draw.rect(surface, GROUND_COLOR, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        # Платформы
        for platform in self.platforms:
            platform.draw(surface)


def main():
    try:
        clock = pygame.time.Clock()
        current_level = 1
        level = Level(current_level)
        character = Character()
        paused = False

        running = True
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_SPACE and not paused:
                        character.jump()
                    elif event.key == K_p:
                        paused = not paused
                    elif event.key == K_n and paused:
                        current_level = 2 if current_level == 1 else 1
                        level = Level(current_level)
                        character = Character()

            if not paused:
                # Управление персонажем
                keys = pygame.key.get_pressed()
                character.is_walking = False

                if keys[K_a]:
                    character.x -= character.speed
                    character.facing_right = False
                    character.is_walking = True
                if keys[K_d]:
                    character.x += character.speed
                    character.facing_right = True
                    character.is_walking = True

                # Обновление персонажа
                character.update(level.platforms)

                # Ограничение выхода за границы экрана
                character.x = max(0, min(character.x, SCREEN_WIDTH - character.width))

            # Отрисовка
            screen.fill(SKY_COLOR)

            # Рисуем солнце
            pygame.draw.circle(screen, (255, 255, 0), (100, 100), 40)

            # Рисуем уровень
            level.draw(screen)

            # Рисуем персонажа
            character.draw(screen)

            # Интерфейс
            level_text = font.render(f"Уровень: {current_level}", True, BLACK)
            controls_text = font.render("Управление: A/D - движение, ПРОБЕЛ - прыжок, P - пауза", True, BLACK)

            screen.blit(level_text, (10, 10))
            screen.blit(controls_text, (10, 40))

            if paused:
                pause_text = font.render("ПАУЗА (N - сменить уровень)", True, BLUE)
                screen.blit(pause_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))

            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"Ошибка: {e}")
        pygame.quit()
        sys.exit()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()