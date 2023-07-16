from snake import *
from snake.ludus import *
from time import sleep
from math import sqrt, inf, sin
from copy import deepcopy
from collections import defaultdict

def get_neighbours(instance: Snake, coordinates: tuple) -> list:
    y, x = coordinates
    
    snake_body = instance.ludus.get(instance.snake_uid)['body']
    wall_body = instance.ludus.get(instance.wall_uid)['body']
    barrier = list(map(tuple, snake_body)) + wall_body
    
    moveable = []
    for n in range(0, 4):
        theta = 2 * PI * (n / 4)
        (dy, dx) = difference(theta)
        if (y + dy, x + dx) not in barrier:
            moveable.append((dy, dx))
    return moveable

#idiotic
def opportunistic_search(instance: Snake) -> tuple:
    snake_head = instance.get_head()
    (y, x) = snake_head
    moveable = get_neighbours(instance, coordinates = snake_head)
    
    food_group = instance.ludus.get(instance.food_gid)
    food = []
    for food_uid in food_group:
        food += instance.ludus.get(food_uid)['body']
    
    change, minimum = (), inf
    for (dy, dx) in moveable:
        for (ty, tx) in food:
            distance = sqrt((ty - y - dy) ** 2 + (tx - x - dx) ** 2)
            density = len(get_neighbours(instance, coordinates  = (y + dy, x + dx)))
            weight = distance
            if minimum > weight:
                change = (dy, dx)
                minimum = weight
    return change

# def add(a: tuple, b: tuple) -> tuple:
#     if len(a) != len(b): return ()
#     return tuple(sum(i) for i in zip(a, b)) 

# def hypotenuse(a: tuple, b: tuple) -> float:
#     return ((b[0] - a[0]) ** 2 + (b[1] - a[0]) ** 2) ** (1 / 2)

def initialise_track(instance: Snake) -> str:
    #track group
    track_gid = instance.ludus.new_group(priority_level = Viewport.LOWEST_PRIORITY_LEVEL)
    track_name = 'track'
    track_glyph = emoji_from_codepoint(instance.attributes['name'][track_name]['glyph'])
    track_attribute = Attribute(track_name, track_glyph)
    instance.ludus.add_attribute(track_gid, track_attribute)
    return track_gid

def add_track(instance: Snake, body: list, gid: str) -> str:
    #track object
    n = len(instance.ludus.get(gid))
    track_object = Object(f'track-{n}', body)
    track_uid = instance.ludus.add_object(track_object, gid)
    return track_uid

#optimal
def breadth_first_search(instance: Snake, render_track: bool = False) -> tuple:
    #track group
    track_gid = initialise_track(instance)

    length = instance.length()
    context = len(instance.get_story())
    food_body = instance.__get_food__()
    queue = [instance]
    explored = []
    while True:
        instance = queue.pop()
        snake_head = instance.get_head()
        neighbours = get_neighbours(instance, coordinates = snake_head)
        # directions = defaultdict(int)
        # for neighbour in neighbours:
        #     (y, x) = add(snake_head, neighbour)
        #     for i, food in enumerate(food_body):
        #         distance = hypotenuse((y, x), food)
        #         directions[neighbour] = (directions[neighbour] + distance) / (i + 1)
        # for direction, _ in sorted(directions.items(), key = lambda i: i[1]):
        for direction in neighbours:
            clone = deepcopy(instance)
            clone.set_direction(direction)
            clone.update()
            story = clone.get_story()
            #accomplishment
            if clone.length() > length:
                return story[context:]
            #exploration
            hash = clone.hash()
            if hash in explored: continue
            explored.append(hash)
            #track
            if render_track:
                track_body = clone.history[:-clone.length()+1]
                track_uid = add_track(clone, track_body, track_gid)
                clone.render(clear = True)
                clone.ludus.remove_object(track_uid)
            queue.insert(0, clone)

#all-around
def a_star_search(instance: Snake) -> tuple:
    pass

if __name__ == '__main__':
    snake = Snake(10, 10)
    length = 0
    while not snake.is_game_over():
        length = snake.length()
        snake.render(clear = True)
        sleep(0.05)
        snake.update()
    print(f'Game Over! - final length: {length}')

    snake = Snake(10, 10, allow_keyboard_input = False)
    snake.render(clear = True)
    target = ()
    path = []
    while True:
        if len(path) == 0:
            path = breadth_first_search(snake)
        length = snake.length()
        direction = path.pop(0)
        snake.set_direction(direction)
        snake.update()
        if snake.is_game_over(): break
        snake.render(clear = True)
        sleep(0.05)
    print(f'Game Over! - final length: {snake.length()}')

    snake = Snake(10, 10, allow_keyboard_input = False)
    length = 0
    while not snake.is_game_over():
        length = snake.length()
        snake.render(clear = True)
        sleep(0.05)
        direction = opportunistic_search(snake)
        snake.set_direction(direction)
        snake.update()
    print(f'Game Over! - final length: {length}')