from Command import *


class TestCommand(Command):
    def __call__(self, environment, args):
        print("TEST")
