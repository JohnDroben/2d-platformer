import pygame
import sys

from custom_logging import Logger

# Инициализация логгера
Logger().initialize()

from levels.levels import LevelManager, LEVEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT
from levels.menu import MainMenu, FinalMenu
from Characters.Hero.hero import Hero
from levels.audio import SoundManager  # класс управления звуками

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NO EXIT")

# Инициализация звуков
sound_manager = SoundManager()
sound_manager.load_sounds()
sound_manager.play_music()

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (20, 30, 15)

# Шрифт
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 72)  # Для Game Over текста


def wait_for_key_release(key):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP and event.key == key:
                return


def main():
    # Инициализация меню
    current_menu = MainMenu()
    in_menu = True
    debug_mode = False

    # Игровые переменные
    clock = pygame.time.Clock()
    level_manager = None
    player = None
    start_pos = [0, 0]
    camera_offset = [0, 0]
    game_over = False
    paused = False

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if in_menu:
                action = current_menu.handle_event(event)
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
                elif action == "debug":
                    in_menu = False
                    debug_mode = True
                    # Инициализация debug режима
                    level_manager = LevelManager(debug_mode=True)
                    start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                    start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                        100, SCREEN_HEIGHT - 150)
                    player = Hero(start_pos)
                    level_manager.current_level.remove_start_portal()
                elif action == "credits":
                    current_menu.credits_shown = True
                elif action == "main_menu":
                    current_menu = MainMenu()
                elif action == "quit":
                    pygame.quit()
                    sys.exit()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_menu = True
                        current_menu = MainMenu()
                    elif event.key == pygame.K_F1:
                        debug_mode = not debug_mode
                        level_manager.reset(debug_mode=debug_mode)
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Hero(start_pos)
                    elif event.key == pygame.K_SPACE and level_manager.current_level.completed:
                        if not level_manager.next_level():
                            current_menu = FinalMenu()
                            in_menu = True
                        else:
                            start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish),
                                                None)
                            start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                                100, SCREEN_HEIGHT - 150)
                            player = Hero(start_pos)
                    elif event.key == pygame.K_r and game_over:
                        level_manager.reset()
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player = Hero(start_pos)
                        level_manager.current_level.portal_remove_timer = None
                        level_manager.current_level.remove_start_portal()
                        game_over = False

        # Отрисовка
        if in_menu:
            current_menu.draw(screen)
        else:
            # Управление игрой
            keys = pygame.key.get_pressed()

            if keys[pygame.K_s]:
                player.sit_down()
            elif player.is_sitting():
                player.stand_up(level_manager.current_level.get_all_game_objects())

            if keys[pygame.K_a]:
                player.move(-1)
            elif keys[pygame.K_d]:
                player.move(1)
            else:
                player.move(0)

            if keys[pygame.K_SPACE] and player.on_ground:
                sound_manager.play_sound('jump')
                player.jump()

            if keys[pygame.K_p]:
                paused = not paused
                wait_for_key_release(pygame.K_p)

            if not level_manager.current_level.completed and not game_over and not paused:
                # Обновление игры
                level_manager.update(player_rect=player.rect)
                player.update()
                player.apply_physics(level_manager.current_level.get_all_game_objects(), LEVEL_WIDTH, SCREEN_HEIGHT)

                if player.rect.top > SCREEN_HEIGHT:
                    game_over = True

                if not level_manager.current_level.start_portal_removed:
                    level_manager.current_level.remove_start_portal()

                # Обработка столкновений
                if (level_manager.current_level.check_hazard_collision(player.rect) or
                        level_manager.current_level.check_fall_into_pit(player.rect)):
                    sound_manager.play_sound('death')
                    player.lose_life()
                    if not player.is_live():
                        game_over = True
                    player.teleport(start_pos)

                # Сбор бонусов
                collected_points = level_manager.current_level.collect_bonuses(player.rect)
                if collected_points:
                    sound_manager.play_sound('coin')
                level_manager.current_level.score += collected_points

                if level_manager.current_level.collect_artifacts(player.rect):
                    pass

                if level_manager.current_level.check_finish(player.rect):
                    level_manager.current_level.completed = True
                    level_manager.current_level.completion_time = pygame.time.get_ticks()

                camera_offset[0] = SCREEN_WIDTH // 2 - player.rect.centerx
                camera_offset[0] = max(min(camera_offset[0], 0), SCREEN_WIDTH - LEVEL_WIDTH)
            elif level_manager.current_level.completed and not game_over:
                if pygame.time.get_ticks() - level_manager.current_level.completion_time > 3000:
                    if not level_manager.next_level():
                        current_menu = FinalMenu()
                        in_menu = True
                    else:
                        start_portal = next((p for p in level_manager.current_level.portals if not p.is_finish), None)
                        start_pos = (start_portal.rect.x + 30, start_portal.rect.y - 50) if start_portal else (
                            100, SCREEN_HEIGHT - 150)
                        player.teleport(start_pos)

            # Отрисовка игры
            screen.fill(DARK_GREEN)
            level_surface = pygame.Surface((LEVEL_WIDTH, SCREEN_HEIGHT))
            level_manager.current_level.draw(level_surface)
            screen.blit(level_surface, camera_offset)

            if player:
                player.draw(screen, camera_offset)

            # UI
            info_y = 20
            player_lives, player_init_lives = player.get_lives()
            for text in [
                f"Уровень: {level_manager.current_level_num}/3",
                f"Счет: {level_manager.total_score + level_manager.current_level.score}",
                f"Артефакты: {level_manager.current_level.artifacts_collected}/{level_manager.current_level.artifacts_required}",
                f"Жизни: {player_lives}/{player_init_lives}",
            ]:
                screen.blit(font.render(text, True, WHITE), (20, info_y))
                info_y += 30

            if level_manager.current_level.completed:
                text = font.render(f"Level {level_manager.current_level_num} completed!", True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

            # Game Over/Pause экран
            if game_over or paused:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 180))
                screen.blit(s, (0, 0))

                line1 = "GAME OVER" if game_over else "ПАУЗА"
                line1_color = RED if game_over else GREEN
                line2 = "Нажмите R для рестарта" if game_over else "Нажмите P чтобы продолжить"

                game_over_text = large_font.render(line1, True, line1_color)
                restart_text = font.render(line2, True, WHITE)
                screen.blit(game_over_text,
                            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()