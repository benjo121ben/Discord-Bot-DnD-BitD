from src.Commands.helper_functions import *


class TestCommand(Command):
    def __init__(self):
        super().__init__("Test")

    def __call__(self, **kwargs):
        print("TEST")
