from audio import SoundManager # класс управления звуками

# Инициализация звуков
sound_manager = SoundManager()
sound_manager.load_sounds()
sound_manager.play_music()

# В игровом цикле при сборе монеты:
if check_coin_collision(player, coins):
    sound_manager.play_sound('coin')

# передача звука смерти
if player.lives <= 0:
    sound_manager.play_sound('death')
    show_game_over_screen()

# В обработчике паузы
if event.key == K_p:
    if paused:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()