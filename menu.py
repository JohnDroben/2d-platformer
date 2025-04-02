import pygame
from typing import Tuple, Optional, List
from levels import load_sprite, SCREEN_WIDTH, SCREEN_HEIGHT

# Типы для аннотаций
Color = Tuple[int, int, int]
Position = Tuple[int, int]
Size = Tuple[int, int]


class Button:
    """Класс кнопки меню"""

    def __init__(self, position: Position, text: str, action: str, size: Size = (300, 60)):
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.text = text
        self.action = action
        self.color = (51, 102, 51)  # Неактивный цвет
        self.active_color = (204, 102, 0)  # Активный цвет
        self.is_active = False
        self.font = pygame.font.SysFont('Arial', 36)

    def draw(self, surface: pygame.Surface):
        """Отрисовка кнопки"""
        color = self.active_color if self.is_active else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class MainMenu:
    """Главное меню игры"""

    def __init__(self):
        self.background = load_sprite("menu_background.jpg", (20, 30, 15))
        self.buttons = [
            Button((100, 300), "Начать игру", "start"),
            Button((100, 400), "Отладочный уровень", "debug"),
            Button((100, 500), "Разработчики", "credits"),
            Button((100, 600), "Выход", "quit")
        ]
        self.current_button_index = 0
        self.buttons[self.current_button_index].is_active = True
        self.credits_shown = False
        self.credits_font = pygame.font.SysFont('Arial', 24)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Обработка событий меню"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Вниз
                self._move_selection(1)
            elif event.key == pygame.K_w:  # Вверх
                self._move_selection(-1)
            elif event.key == pygame.K_SPACE:  # Выбор
                return self.buttons[self.current_button_index].action
            elif event.key == pygame.K_ESCAPE and self.credits_shown:
                self.credits_shown = False
        return None

    def _move_selection(self, direction: int):
        """Перемещение выбора кнопок"""
        self.buttons[self.current_button_index].is_active = False
        self.current_button_index = (self.current_button_index + direction) % len(self.buttons)
        self.buttons[self.current_button_index].is_active = True

    def draw(self, surface: pygame.Surface):
        """Отрисовка меню"""
        # Фон
        surface.blit(self.background, (0, 0))

        # Заголовок
        #title_font = pygame.font.SysFont('Arial', 72)
        #title = title_font.render("2D ПЛАТФОРМЕР", True, (255, 255, 255))
        #surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Кнопки
        for button in self.buttons:
            button.draw(surface)

        # Экран разработчиков
        if self.credits_shown:
            self._draw_credits(surface)

    def _draw_credits(self, surface: pygame.Surface):
        """Отрисовка экрана разработчиков"""
        # Затемнение фона
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        # Текст разработчиков
        credits = [
            "Разработчики:",
            "",
            "Программисты:",
            "Семен Чепурнов",
            "Евгений Козулин",
            "Станислав Царев",
            "Георгий Дробенюк",
            "",
            "Художники:",
            "Карапет Гаранян",
            "Исроил Алиев",
            "",
            "Гейм-дизайнер:",
            "Артем Лавров",
            "",
            "Нажмите ESC для возврата"
        ]

        y_pos = 200
        for line in credits:
            text = self.credits_font.render(line, True, (255, 255, 255))
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 40


class FinalMenu(MainMenu):
    """Финальное меню игры, появляется после прохождения всех уровней"""

    def __init__(self):
        super().__init__()  # Инициализация родительского класса
        self.background = load_sprite("menu_background.jpg", (0, 0, 0))  # Загрузка специального фона
        self.buttons = [
            Button((SCREEN_WIDTH // 2 - 150, 400), "В Главное Меню", "main_menu"),
            Button((SCREEN_WIDTH // 2 - 150, 500), "Выйти из игры", "quit")
        ]
        self.current_button_index = 0
        self.buttons[self.current_button_index].is_active = True
        self.congrats_font = pygame.font.SysFont('Arial', 48, bold=True)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Обработка событий с сохранением базовой логики"""
        action = super().handle_event(event)  # Используем логику родителя для навигации
        if action in ["main_menu", "quit"]:
            return action
        return None

    def draw(self, surface: pygame.Surface):
        """Отрисовка с добавлением поздравительного текста"""
        # Отрисовка фона и кнопок (базовая логика)
        surface.blit(self.background, (0, 0))

        # Поздравительный текст
        congrats_text = self.congrats_font.render("Поздравляем! Игра пройдена!", True, (255, 215, 0))  # Золотой цвет
        surface.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, 200))

        # Отрисовка кнопок
        for button in self.buttons:
            button.draw(surface)