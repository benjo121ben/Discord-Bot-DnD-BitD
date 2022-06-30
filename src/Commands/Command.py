from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def __call__(self, environment,args):
        pass