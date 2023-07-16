from typing import Union
from os import urandom, system, name as os_name
from sys import byteorder
from math import floor, sin, cos
from functools import reduce

def flush() -> None:
    system('cls' if os_name == 'nt' else 'clear')

def random(n: int = 32) -> float:
    return int.from_bytes(urandom(n), byteorder) / (2 ** (n * 8) - 1)

#random-map
def randomap(a: int, b: int) -> int:
    return floor(random() * (b - a - 1) + a)

def randoice(l: Union[list, dict]):
    n = randomap(0, len(l))
    if type(l) == list:
        return l[n]
    elif type(l) == dict:
        return l[list(l.keys())[n]]

def randox(a: int, b: int, l: list) -> int:
    return randoice(list(set([i for i in range(a, b)]) - set(l)))

def flatten(l: list) -> list:
    return reduce(lambda a,b: a + b, l)

def difference(theta: float) -> tuple:
    return map(round, (sin(theta), cos(theta)))

def until(arg: str, conditional: tuple, start: int, increment: int) -> int:
    i = start
    while i >= 0 and i < len(arg) and arg[i] in conditional: i += increment
    return i

def unpad(arg: str, padding: tuple) -> str:
    if type(padding) != tuple: padding = tuple(padding)
    return arg[until(arg, padding, 0, +1):until(arg, padding, len(arg) - 1, -1)+1]

def conjoin(*args: str) -> str:
    joint = ('/', '\\')
    return '/'.join([arg[until(arg, joint, 0, +1):until(arg, joint, len(arg)-1, -1)+1] for arg in args])

def emoji_from_codepoint(codepoint: str) -> str:
    if len(codepoint) < 2 or codepoint[:2].upper() != 'U+': return ''
    return chr(int(codepoint[2:], base = 16))