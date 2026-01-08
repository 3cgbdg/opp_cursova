from services.core import ReversiCore
from ui.game_ui import GameUI
from ui.menu import MenuUI


def main():
    while True:
        # show menu first
        menu = MenuUI()
        start_game, music_enabled, volume, game_mode, difficulty = menu.run()
        
        if not start_game:
            break  # User chose "Exit" or closed the window
        
        # Start the game with settings from the menu
        core = ReversiCore()
        ui = GameUI(core, music_enabled=music_enabled, volume=volume, game_mode=game_mode, difficulty=difficulty)
        should_continue = ui.run()
        
        if not should_continue:
            break # User closed the window during game


if __name__ == "__main__":
    main()

