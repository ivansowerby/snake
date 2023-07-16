import eel
from snake import Snake
from snake.util import conjoin
from snake.ludus import Viewport, Ludus
from math import inf
from copy import deepcopy

def defile(filepath: str) -> str:
    end = max(map(filepath.rfind, ('/', '\\')))
    if filepath.rfind('.') <= end: return filepath
    return filepath[:end]

WEB_ROOT = 'web'
WEB_FILENAME = 'index.html'

@eel.expose
def snakeBegin(width: int, height: int) -> None:
    global snake
    snake = Snake(
        width, height,
        filepath = ('snake', 'toml', 'attributes.toml'),
        allow_keyboard_input = False
    )

def cleanAttributes(attributes: dict) -> dict:
    if 'priority-level' in attributes and attributes['priority-level'] == inf:
        attributes['priority-level'] = 10 ** 1000
    if 'glyph' in attributes: del attributes['glyph']
    return attributes

@eel.expose
def getObjects() -> dict:
    return {uid: dict(properties) for uid, properties in deepcopy(snake.ludus.objects).items()}

@eel.expose
def getGroups() -> dict:
    return dict(deepcopy(snake.ludus.groups))

@eel.expose
def getAttributes() -> dict:
    return {gid: cleanAttributes(attributes) for gid, attributes in deepcopy(snake.ludus.attributes).items()}

@eel.expose
def snakeSetDirection(direction: str) -> None:
    if not snake.is_game_over():
        snake.__handler__(direction)

@eel.expose
def snakeUpdate(username: str) -> None:
    snake.update()
    snake.scoreboard(username)

@eel.expose
def snakeIsGameOver() -> None:
    game_over = snake.is_game_over()
    if not game_over:
        snake.render()
    return game_over

@eel.expose
def snakeLength() -> int:
    return snake.length()

@eel.expose
def snakeRetry() -> None:
    snake.retry()

@eel.expose
def getUserHighScore(username: str) -> int:
    return snake.get_high_score(username)

@eel.expose
def pathConjoin(*args: str) -> str:
    return conjoin(*args)

if __name__ == '__main__':
    eel.init(WEB_ROOT)
    eel.start(WEB_FILENAME, port = 8000)