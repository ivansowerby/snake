from typing import Union, Optional
from snake.util import *
from snake.ludus import Ludus, Viewport
from math import pi as PI
import keyboard
from toml import load
from hashlib import sha256
from snake.users import Users, HighScore

class Object:
    def __init__(self, name: str, body: list, velocity: list = []) -> None:
        self.name = name
        self.body = body
        self.velocity = velocity

class Attribute:
    def __init__(self, name: str, glyph: str) -> None:
        self.name = name
        self.glyph = glyph

class Snake:
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    def __init__(self, width: int = 20, height: int = 20, config: Union[tuple, str] = ('snake', '/toml', '/attributes.toml'), allow_keyboard_input: bool = True) -> None:
        self.viewport = Viewport(width, height)
        self.ludus = Ludus()

        #Config
        if type(config) == tuple: config = conjoin(*config)
        self.config = config

        with open(self.config, 'r') as file:
            self.attributes = load(file)

        #wall group
        self.wall_gid = self.ludus.new_group()
        wall_name = 'wall'
        wall_glyph = emoji_from_codepoint(self.attributes['name'][wall_name]['glyph'])
        wall_attribute = Attribute(wall_name, wall_glyph)
        self.ludus.add_attribute(self.wall_gid, wall_attribute)

        #wall body/edges
        wall_body = []
        for x in range(0, self.viewport.width):
            wall_body.extend(((0, x), (self.viewport.height - 1, x)))
        for y in range(1, self.viewport.height - 1): wall_body.extend(((y, 0), (y, self.viewport.width - 1)))
        
        #wall object
        wall_object = Object('wall', wall_body)
        self.wall_uid = self.ludus.add_object(wall_object, self.wall_gid) 

        #snake group
        self.snake_gid = self.ludus.new_group()
        snake_name = 'snake'
        snake_glyph = emoji_from_codepoint(self.attributes['name'][snake_name]['glyph'])
        snake_attribute = Attribute(snake_name, snake_glyph)
        self.ludus.add_attribute(self.snake_gid, snake_attribute)

        #snake body
        (y, x) = self.__generate_coordinates__(exclude = wall_body)
        exclude = []
        for n in range(0, 4):
            theta = 2 * PI * (n / 4)
            (dy, dx) = difference(theta)
            if (y + dy, x + dx) in wall_body: exclude.append(n)
        theta = randox(0, 4, exclude) / 4 * 2 * PI
        (dy, dx) = difference(theta)
        snake_body = [[y, x], [y + dy, x + dx]]

        #trace
        backward = 0
        (y, x) = snake_body[-1]
        while (y, x) not in wall_body:
            (y, x) = (y + dy, x + dx)
            backward += 1
        forward = 0
        (y, x) = snake_body[0]
        while (y, x) not in wall_body:
            (y, x) = (y - dy, x - dx)
            forward += 1
        
        if forward > backward or \
           (forward == backward and random() >= 0.5):
            (dy, dx) = (-dy, -dx)
        else:
            snake_body.reverse()
        
        snake_velocity = [[dy, dx] for _ in range(len(snake_body))]

        #snake object
        snake_object = Object('snake', snake_body, snake_velocity)
        self.snake_uid = self.ludus.add_object(snake_object, self.snake_gid)

        #history
        self.history = []

        #food group
        self.food_gid = self.ludus.new_group()
        food_name = 'food'
        food_glyph = emoji_from_codepoint(self.attributes['name'][food_name]['glyph'])
        food_attribute = Attribute(food_name, food_glyph)
        self.ludus.add_attribute(self.food_gid, food_attribute)

        #food
        self.generate_food()

        #keyboard
        self.allow_keyboard_input = allow_keyboard_input
        if self.allow_keyboard_input: keyboard.hook(self.__handler__)

        #users
        self.users = Users()

    def toggle_keyboard_input(self, allow: bool = None) -> None:
        if allow == None: allow = not self.allow_keyboard_input
        self.allow_keyboard_input = allow
        if self.allow_keyboard_input: keyboard.hook(self.__handler__)
        else: keyboard.unhook(self.__handler__)

    def __handler__(self, event: Union[keyboard.KeyboardEvent, str]) -> None:
        key = event
        if isinstance(key, keyboard.KeyboardEvent): key = key.name.lower()
        snake_object = self.ludus.get(self.snake_uid)
        head_velocity = snake_object['velocity'][0]
        if (key == 'w' or key == 'up') and head_velocity != [1, 0]:
            head_velocity = Snake.UP
        elif (key == 'a' or key == 'left') and head_velocity != [0, 1]:
            head_velocity = Snake.LEFT
        elif (key == 's' or key == 'down') and head_velocity != [-1, 0]:
            head_velocity = Snake.DOWN
        elif (key == 'd' or key == 'right') and head_velocity != [0, -1]:
            head_velocity = Snake.RIGHT
        self.ludus.objects[self.snake_uid]['velocity'][0] = list(head_velocity)
    
    def behead(self) -> tuple:
        return self.ludus.objects[self.snake_uid]['body'].pop(0)

    def get_head(self) -> tuple:
        return self.ludus.get(self.snake_uid)['body'][0]

    def set_direction(self, direction: tuple) -> None:
        event = None
        if direction == Snake.UP: event = 'up'
        elif direction == Snake.LEFT: event = 'left'
        elif direction == Snake.DOWN: event = 'down'
        elif direction == Snake.RIGHT: event = 'right'
        if event != None: self.__handler__(event)

    def length(self) -> int:
        if self.is_game_over(): return 0
        return len(self.ludus.get(self.snake_uid)['body'])

    def __generate_coordinates__(self, exclude: list = []) -> tuple:
        a = [y * self.viewport.width + x for (y, x) in exclude]
        i = randox(0, self.viewport.width * self.viewport.height, a)
        (y, x) = (i // self.viewport.width, i % self.viewport.width) 
        return (y, x)

    def __generate_food_coordinates__(self) -> list:
        food = self.ludus.get(self.food_gid)
        #integrated flatten
        exclude = []
        for value in self.ludus.objects.values():
            exclude += value['body']
        return self.__generate_coordinates__(exclude)

    def generate_food(self) -> None:
        n = len(self.ludus.get(self.food_gid))
        food_body = self.__generate_food_coordinates__()
        food_object = Object(f'food-{n}', [food_body])
        food_uid = self.ludus.add_object(food_object, gid = self.food_gid)
    
    def __get_food__(self) -> list:
        food_group = self.ludus.get(self.food_gid)
        food_body = []
        for food_uid in food_group:
            food_body += self.ludus.get(food_uid)['body']
        return food_body
    
    def newest_food(self) -> tuple:
        return self.__get_food__()[-1]

    def oldest_food(self) -> tuple:
        return self.__get_food__()[0]
    
    def __get_history__(self) -> list:
        return self.history + [tuple(self.get_head())]

    def hash(self) -> bytes:
        object = b''.join([bytes(event) for event in self.__get_history__()])
        return sha256(object).digest()

    def get_story(self) -> list:
        history = self.__get_history__()
        return [(j[0] - i[0], j[1] - i[1]) for (i, j) in zip(history, history[1:])]

    def __enforce__(self, snake_tail: tuple, snake_tail_velocity: tuple) -> None:        
        snake_object = self.ludus.get(self.snake_uid)
        snake_body = snake_object['body']
        wall_body = self.ludus.get(self.wall_uid)['body']
        if any([snake_body.count(joint) > 1 or tuple(joint) in wall_body for joint in snake_body]):
            self.ludus.remove_object(self.snake_uid)
            if self.allow_keyboard_input: keyboard.unhook(self.__handler__)
            return None
        
        for joint in snake_body:
            joint = tuple(joint)
            if joint in self.__get_food__():
                food_uid = self.ludus.by('body')[joint]
                self.ludus.remove_object(food_uid)
                self.ludus.objects[self.snake_uid]['body'].append(snake_tail)
                self.ludus.objects[self.snake_uid]['velocity'].append(list(snake_tail_velocity))
        
        if len(self.__get_food__()) == 0: self.generate_food()

    def is_game_over(self) -> bool:
        return self.snake_uid not in self.ludus.objects

    def update(self) -> None:
        snake_object = self.ludus.get(self.snake_uid)
        snake_tail = snake_object['body'][-1]
        (dy, dx) = snake_object['velocity'][-1]
        #update history
        self.history.append(tuple(snake_object['body'][0]))
        for i, ((y, x), (dy, dx)) in enumerate(zip(snake_object['body'], snake_object['velocity'])):
            self.ludus.objects[self.snake_uid]['body'][i] = [y + dy, x + dx]
        #update joint velocities
        self.ludus.objects[self.snake_uid]['velocity'].pop()
        self.ludus.objects[self.snake_uid]['velocity'].insert(0, snake_object['velocity'][0])
        #enforce rules
        self.__enforce__(snake_tail, (dy, dx))

    def scoreboard(self, username: Optional[str] = None) -> None:
        username = username if username != None else ''
        high_score = self.users.get(username, 'high_score')
        score = self.length()
        if score > (high_score if high_score != None else bool(high_score)):
            self.users.add_personalities(username, HighScore(score))

    def get_high_score(self, username: Optional[str] = None) -> int:
        if username == None:
            return max(self.users.by('high_score').values())
        else:
            high_score = self.users.get(username, 'high_score')
            return high_score if high_score != None else 0

    def render(self, clear = True, blank = 'U+2B1B') -> None:
        blank_glyph = emoji_from_codepoint(blank)
        if blank_glyph == '': blank_glyph = blank
        if clear: flush()
        body = self.ludus.by('body')
        for i in range(self.viewport.height):
            for j in range(self.viewport.width):
                value = (i, j)
                if value in body:
                    uid = body[value]
                    object = self.ludus.get(uid)
                    groups = object['gid']
                    if type(groups) == list and len(groups) > 0:
                        gid = groups[-1]
                        attributes = self.ludus.attributes[gid]
                        glyph = attributes['glyph']
                        print(glyph, end = '')
                        continue
                print(blank_glyph, end = '')
            print()
    
    def retry(self) -> None:
        self.__init__(
            self.viewport.width,
            self.viewport.height,
            self.config,
            self.allow_keyboard_input
        )