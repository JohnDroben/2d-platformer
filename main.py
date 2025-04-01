import sys

import pygame

from Characters.Enemies.enemy import Enemy
from Characters.Hero.hero import Hero
from custom_logging import Logger
from levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from menu import MainMenu  # Добавлен новый импорт

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platformer")
#Инициализация логгера
Logger().initialize()
# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (20, 30, 15)

# Шрифт
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 72)  # Для Game Over текста

ground_level = SCREEN_HEIGHT + 200


def main():
    # Инициализация меню
    menu = MainMenu()
    in_menu = True
    debug_mode = False

    # Игровые переменные (инициализируются при старте игры)
    clock = pygame.time.Clock()
    level_manager = None
    player = None
    enemy= None
    camera_offset = [0, 0]
    game_over = False

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if in_menu:
                action = menu.handle_event(event)
                if action == "start":
                    in_menu = False
                    debug_mode = False
                    # Инициализация игры
                    level_manager = LevelManager(debug_mode=debug_mode)
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                    player = Hero(start_pos)
                    level_manager.current_level.remove_start_portal()
                    Logger().debug(f"INIT_CREATE: start_pos:{start_pos}")
                elif action == "debug":
                    in_menu = False
                    debug_mode = True
                    # Инициализация debug режима
                    level_manager = LevelManager(debug_mode=True)
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                    100, SCREEN_HEIGHT - 150)
                    # ---------------------------------------
                    enemy_pos = (start_portal.rect.x + 150, start_portal.rect.y - 80) if start_portal else (
                    150, SCREEN_HEIGHT - 150)
                    enemy = Enemy(enemy_pos)
                    enemy.update_ai(level_manager.current_level.get_all_game_objects())
                    enemy.apply_physics(level_manager.current_level.get_all_game_objects(), SCREEN_WIDTH, SCREEN_HEIGHT)
                    # ---------------------------------------
                    player = Hero(start_pos)
                    level_manager.current_level.remove_start_portal()
                    Logger().debug(f"DEBUG_INIT: start_pos:{start_pos}")
                elif action == "credits":
                    menu.credits_shown = True
                elif action == "quit":
                    pygame.quit()
                    sys.exit()
            else:
                # Оригинальная обработка событий игры
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_menu = True  # Возврат в меню
                    elif event.key == pygame.K_F1:  # Переключение debug режима
                        debug_mode = not debug_mode
                        level_manager.reset(debug_mode=debug_mode)
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Hero(start_pos)
                        Logger().debug(f"Debug mode {'ON' if debug_mode else 'OFF'}")
                    if event.key == pygame.K_SPACE and level_manager.current_level.completed:
                        if not level_manager.next_level():
                            Logger().info("Игра завершена!")
                            in_menu = True
                        else:
                            start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish),
                                                None)
                            start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                                100, SCREEN_HEIGHT - 150)
                            player = Hero(start_pos)
                            Logger().debug(f"NEW_LEVEL: start_pos:{start_pos}")
                    elif event.key == pygame.K_r and game_over:  # Рестарт по нажатию R
                        level_manager.reset()
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Hero(start_pos)
                        Logger().debug(f"RESTART_GAME: start_pos:{start_pos}")
                        level_manager.current_level.portal_remove_timer = None
                        level_manager.current_level.remove_start_portal()
                        game_over = False

        # Отрисовка
        if in_menu:
            menu.draw(screen)
        else:
            # Оригинальная игровая логика
            if not level_manager.current_level.completed and not game_over:
                # Управление игроком
                keys = pygame.key.get_pressed()
                if keys[pygame.K_s]:
                    player.sit_down()
                else:
                    if player.is_sitting():
                        player.stand_up(level_manager.current_level.get_all_game_objects())

                if keys[pygame.K_a]:
                    player.move(-1)
                elif keys[pygame.K_d]:
                    player.move(1)
                else:
                    player.move(0)

                if keys[pygame.K_SPACE]:
                    player.jump()

                # Обновление уровня
                level_manager.update(player_rect=player.rect)

                # Обновление врага (ДОБАВЛЕНО)
                enemy.update_ai(level_manager.current_level.get_all_game_objects())
                enemy.apply_physics(level_manager.current_level.get_all_game_objects(), LEVEL_WIDTH, SCREEN_HEIGHT)

                # Обновление игрока
                player.update()
                player.apply_physics(level_manager.current_level.get_all_game_objects(), LEVEL_WIDTH, SCREEN_HEIGHT)

                if player.rect.top > SCREEN_HEIGHT:
                    game_over = True

                if not level_manager.current_level.start_portal_removed:
                    level_manager.current_level.remove_start_portal()

                if level_manager.current_level.check_hazard_collision(player.rect):
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player = Hero(start_pos)

                if level_manager.current_level.check_fall_into_pit(player.rect):
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player = Hero(start_pos)

                collected_points = level_manager.current_level.collect_bonuses(player.rect)
                level_manager.current_level.score += collected_points
                level_manager.current_level.collect_artifacts(player.rect)

                if level_manager.current_level.check_finish(player.rect):
                    level_manager.current_level.completed = True
                    level_manager.current_level.completion_time = pygame.time.get_ticks()

                camera_offset[0] = SCREEN_WIDTH // 2 - player.rect.centerx
                camera_offset[0] = max(min(camera_offset[0], 0), SCREEN_WIDTH - LEVEL_WIDTH)
            elif level_manager.current_level.completed and not game_over:
                if pygame.time.get_ticks() - level_manager.current_level.completion_time > 3000:
                    if not level_manager.next_level():
                        in_menu = True
                    else:
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Hero(start_pos)
                        Logger().debug(f"NEW_LEVEL: start_pos:{start_pos}")

            # Отрисовка игры
            screen.fill(DARK_GREEN)

            level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
            level_manager.current_level.draw(level_surface)
            screen.blit(level_surface, camera_offset)

            if player:
                player.draw(screen, camera_offset)

            enemy.draw(screen, camera_offset)

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
                text = font.render(
                    f"Level {level_manager.current_level_num} completed!" if level_manager.current_level.completed
                    else "",
                    True,
                    WHITE
                )
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

            if game_over:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 180))
                screen.blit(s, (0, 0))

                game_over_text = large_font.render("GAME OVER", True, RED)
                restart_text = font.render("Нажмите R для рестарта", True, WHITE)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                             SCREEN_HEIGHT // 2 - 50))
                screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                           SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()