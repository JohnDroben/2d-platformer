# 2D Platformer
Игра разработана на Python с использованием Pygame.

### Особенности
* Переработана Структура
* Добавлены Интерфесы для работы с движением и обработкой
````Cmd
├── Interfaces/ # Обработчики взаимодействий
----                 -------------         ------ ----
--- collision_handler.py
--- damage_handler.py
--- jump_handler.py
--- move_handler.py
--- sit_down_handler.py
````
* Проверка коллизий происходит в ___collision_handler.py___
* Класс __Character__ является родительским
* Классы __Hero__ __Enemy__  наследуются от __Character__
* Измененна группировка в __ObjectType__

### Debag
* Интегрировать в основной код
* Обьекты типа __Enemy__ должны добавляться в _LevelManager_
  (level_manager.add(obj))
что бы правильно обрабатываться в __CollisionHandler__
* Коллизии обрабатываются по типу _Игрок_->_Обьект_
В зависимости от типа _solid_, _collectable_, _dangerous_
происходит обработка
* 1 Добавлено поле _health_  для __Hero__, __Enemy__
* 2 Добавлены поля _score_, _artifact_ для __Hero__
* Отрисовать Интерфейс Игры используя 1, 2 выше
* Интерфейс ___DamageHandler___ на данный момент явл. заглушкой 
в теории привязать к нему экран __GameOver__ а так же __death__ для классов __Hero__ __Enemy__

### Изменения в _main.py_
* ````python
    def create_player(x, y):
        player = Hero(...) # Было Character(...)
    #----------------------------
    # везде где были вызовы   player.stand_up(...)  
    player.sit_handler.stand_up(...) # стало


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


## 📥 Как получить эту версию
```bash
git clone -b physics https://github.com/JohnDroben/2d-platformer.git
pip install -r requirements.txt
