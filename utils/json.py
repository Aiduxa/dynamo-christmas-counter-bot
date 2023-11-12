__all__ = ["ChristmasTriviaJson"]

from json import loads, load
from os import getcwd
from random import choice

class jsonHandler:

    def __init__(self, dir: str = f"{getcwd()}/data") -> None:
        self.dir = dir

    def load(self, file: str) -> dict:

        with open(f"{self.dir}/{file}.json", "r") as f:
            data: dict = load(f)
            f.close()
            return data
        
class ChristmasTriviaJson(jsonHandler):
    
    def __init__(self) -> None:
        self.file = "christmas-trivia"
        super().__init__()

    def get_points(self) -> dict:
        data: dict = self.load(self.file)
        return data["points"]
    
    def get_random_question(self) -> dict:
        data: dict = self.load(self.file)
        return choice(data["trivia"])

