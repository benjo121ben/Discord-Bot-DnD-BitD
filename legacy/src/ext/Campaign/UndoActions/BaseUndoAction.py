import abc


class BaseUndoAction(abc.ABC):
    @abc.abstractmethod
    def undo(self, executing_user: str) -> str:
        pass

    @abc.abstractmethod
    def redo(self, executing_user: str) -> str:
        pass

    @abc.abstractmethod
    def __str__(self):
        pass
