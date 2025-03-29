import pygame
import sys
from levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from custom_logging import Logger

from Characters.action import Action
from Characters.character import Character
from Characters.animation2 import AnimatedObject
from Characters.type_object import ObjectType


# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer - Level Demo")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (20, 30, 15)

# Шрифт
font = pygame.font.SysFont('Arial', 24)

ground_level = SCREEN_HEIGHT


def create_player(x, y):
    player = Character(
        x=x,  # Стартовая позиция X (не привязывать к ground_level)
        y=y,  # Ставим на поверхность (ground_level - высота)
        width=60,  # Ширина hitbox (рекомендую уменьшить)
        height=80,  # Высота hitbox (рекомендую уменьшить)
        speed=4.0,  # Оптимальная скорость движения
        jump_force=12,  # Сила прыжка
        gravity=0.6,  # Гравитация
        ground_level=ground_level  # Уровень земли
    )
    player_anim = AnimatedObject(player)
    # Для каждого действия указываем файл и количество кадров
    player_anim.load_action_frames(Action.IDLE, 'Characters/assets/sprites/idle.png', 7)
    # player_anim.load_action_frames('move', 'assets/run.png', 6)
    player_anim.load_action_frames(Action.JUMP, 'Characters/assets/sprites/jump.png', 13)
    return player, player_anim


def main():
    clock = pygame.time.Clock()
    level_manager = LevelManager()
    Logger().initialize()

    # Инициализация игрока у стартового портала
    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (100, SCREEN_HEIGHT - 150)
    player, player_anim = create_player(*start_pos)


    # Параметры камеры
    camera_offset = [0, 0]
    running = True

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and level_manager.current_level.completed:
                    if not level_manager.next_level():
                        Logger().info("Демо завершено!")
                        running = False
                    else:
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                        player, player_anim = create_player(*start_pos)

            # Управление
        keys = pygame.key.get_pressed()
        player.direction = 0

        if keys[pygame.K_s]:
            player.sit_down()
        else:
            if player.is_sitting:
                player.stand_up(level_manager.current_level.get_all_game_objects())

        if keys[pygame.K_a]:
            player.move(-1)
        if keys[pygame.K_d]:
            player.move(1)
        if keys[pygame.K_s]:
            player.sit_down()
            # Приседание (без проверки)
            # Вставание (с проверкой)
        elif player.is_sitting:
            player.stand_up(level_manager.current_level.get_all_game_objects())  # передаем список всех объектов

            # Автоматическое вставание при прыжке/движении
            if (keys[pygame.K_SPACE] or
                    (player.is_sitting and (keys[pygame.K_a] or keys[pygame.K_d]))):
                player.stand_up(level_manager.current_level.get_all_game_objects())

        if keys[pygame.K_SPACE]:
            player.jump()


        # Обновление
        if not level_manager.current_level.completed:


            # Позиция камеры (следим за игроком)
            camera_offset[0] = SCREEN_WIDTH // 2 - player.rect.centerx
            # Ограничиваем камеру границами уровня
            camera_offset[0] = max(min(camera_offset[0], 0), SCREEN_WIDTH - LEVEL_WIDTH)
        else:
            # Автопереход на следующий уровень через 3 секунды
            if pygame.time.get_ticks() - level_manager.current_level.completion_time > 3000:
                if not level_manager.next_level():
                    running = False
                else:
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                    player, player_anim = create_player(*start_pos)

        # Отрисовка
        screen.fill(DARK_GREEN)

        # Отрисовка уровня с учетом смещения камеры
        level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
        level_manager.current_level.draw(level_surface)
        screen.blit(level_surface, camera_offset)

        # Отрисовка игрока
        player_anim.update()
        # В основном цикле отрисовки
        player.apply_physics(level_manager.current_level.get_all_game_objects(), LEVEL_WIDTH, SCREEN_HEIGHT)
        player_anim.draw(screen, camera_offset)

        #player_anim.draw(screen)
        # UI
        info_y = 20
        for text in [
            f"Уровень: {level_manager.current_level_num}/3",
            f"Счет: {level_manager.total_score + level_manager.current_level.score}",
            f"Артефакты: {level_manager.current_level.artifacts_collected}/{level_manager.current_level.artifacts_required}"
        ]:
            screen.blit(font.render(text, True, WHITE), (20, info_y))
            info_y += 30

        if level_manager.current_level.completed:
            text = font.render(level_manager.get_level_completion_message(), True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()