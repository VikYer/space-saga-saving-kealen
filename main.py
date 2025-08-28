from game_state import GameState
from gui import SpaceSaga

if __name__ == '__main__':
    state = GameState()
    app = SpaceSaga(state)
    app.run()
