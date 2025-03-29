# 2D Platformer
Игра разработана на Python с использованием Pygame.
![Gameplay Demo](Characters/assets/demonstration.gif)

### Особенности
Тестовый файл движения персонажа, обработки взаимодействия с обьектом, проигрыш анимации
### Реализованно
* Движение вправо\влево
* Прыжок
* Приседание(прохождение под обьектами)
* Прохождение сквозь обьекты не типа Platform
* Добавлена работа со звуком класс ___SoundObject___

### Управление

| Клавиша | Действие       |
|---------|---------------|
| a d     | Движение      |
| Пробел  | Прыжок        |
| s       | Приседание    |


### Загрузка Анимации
Происходит через класс AnimatedObject  
В файле test.py 
````python
# Добавляется обьект для анимации
player_anim = AnimatedObject(player)

# Для каждого действия указываем файл и количество кадров
player_anim.load_action_frames(Action.IDLE, 'assets/sprites/idle.png', 7)
````
* В классе Action файла action.py Указаны типы действий
* ___Изменить Action  в соответсвии с дейстaвительностью___

### Обьекты и типы
 ````python
 game_objects = [
   GameObject(0, 550, 800, 50, ObjectType.PLATFORM, (100, 200, 100)),  # Пол
   GameObject(200, 480, 100, 20, ObjectType.PLATFORM, (100, 200, 100)),  # Платформа 1
   GameObject(400, 350, 100, 20, ObjectType.PLATFORM, (100, 200, 100)),  # Платформа 2
   GameObject(100, 300, 40, 40, ObjectType.ENEMY, (200, 50, 50)),  # Враг
   GameObject(400, 200, 20, 20, ObjectType.COIN, (255, 215, 0)),  # Монетка
   GameObject(600, 250, 20, 20, ObjectType.COIN, (255, 215, 0))  # Монетка
]
 ````
* Тестовые обьекты 
* Класс обьектов должен иметь поле  ___self.object_type : ObjectType___
* Класс ___ObjectType___ определяет типы обьектов(нужно что бы игрок правильно взаимодействовал)
* ___Изменить ObjectType в соответсвии с действительностью___

### Для тестирования запустите файл _test.py_ подставив свои параметры

## Установка
```bash
git clone https://github.com/JohnDroben/2d-platformer/tree/develop-
pip install -r requirements.txt
