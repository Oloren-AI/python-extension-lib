from .server import register, run

class choice:
    def __init__(self, choices):
        self.choices = choices

    def config(self):
        return {
            "type": "choice",
            "choices": self.choices
        }

class number:
    @staticmethod
    def config():
        return {
            "type": "number",
        }