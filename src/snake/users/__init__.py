from typing import Union
from snake.util import conjoin
from os import path
from json import load, dump
from collections import defaultdict
from hashlib import sha256
from base64 import b64encode, b64decode

class HighScore():
    def __init__(self, high_score) -> None:
        self.high_score = high_score

class Users:
    def __init__(self, filepath: Union[tuple, str] = ('snake', '/json', '/users.json'), default = lambda: None) -> None:
        if type(filepath) == tuple: filepath = conjoin(*filepath)
        self.filepath = filepath
        
        self.data = defaultdict(lambda: defaultdict(default))
        if not path.exists(self.filepath):
            with open(self.filepath, 'w') as file: 
                dump({}, file)
        else:
            with open(self.filepath, 'r') as file:
                self.data.update(load(file))
        
    def __hash__(s: str, encoding: str = 'utf-32') -> str:
        return b64encode(sha256(s.encode(encoding)).digest()).decode('utf-8')

    def __update__(self) -> None:
        with open(self.filepath, 'w') as file:
            dump(self.data, file)

    def add_user(self, username: str) -> None:
        hash = Users.__hash__(username)
        self.data[hash] = {}
        self.__update__()
    
    def remove_user(self, username: str) -> None:
        hash = Users.__hash__(username)
        del self.data[hash]
        self.__update__()
    
    def add_personalities(self, username: str, personalities: Union[dict, object]) -> None:
        if isinstance(personalities, object): personalities = vars(personalities)
        hash = Users.__hash__(username)
        self.data[hash].update(personalities)
        self.__update__()
    
    def remove_personalities(self, username: str, personalities: Union[dict, object]) -> None:
        if isinstance(personalities, object): personalities = vars(personalities)
        hash = Users.__hash__(username)
        [self.data[hash].pop(personality) for personality in personalities]
        self.__update__()

    def get_user(self, username: str) -> dict:
        hash = Users.__hash__(username)
        return self.data[hash]

    def get(self, username: str, personalities: Union[str, list, tuple]) -> tuple:
        if type(personalities) == str: personalities = [personalities]
        user = self.get_user(username)
        personalities = [user[personality] for personality in personalities]
        return tuple(personalities) if len(personalities) != 1 else personalities[0]
    
    def by(self, personality: str) -> dict:
        return {hash: personalities[personality] for hash, personalities in self.data.items() if personality in personalities}