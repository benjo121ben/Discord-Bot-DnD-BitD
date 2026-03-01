from .BaseUndoAction import BaseUndoAction


class UndoActionGroup(BaseUndoAction):
    def __init__(self, actions: list[BaseUndoAction]):
        self.actions = actions

    def __str__(self):
        return "\n".join(str(action) for action in self.actions)

    def undo(self, executing_user: str):
        if len(self.actions) == 0:
            raise Exception("A multiple stat is empty")
        return f"Undid changes:\n" + "\n".join(action.undo(executing_user) for action in self.actions)

    def redo(self, executing_user: str):
        return f"Reapplied changes\n" + "\n".join(action.redo(executing_user) for action in self.actions)
