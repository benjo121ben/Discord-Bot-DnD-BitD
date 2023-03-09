from .BaseUndoAction import BaseUndoAction
from .StatUndoAction import StatUndoAction
from ..Character import Character


class MultipleBaseAction(BaseUndoAction):
    def __init__(self, char: Character, stats: list[str]):
        self.character_tag: str = char.tag
        self.char: Character = char
        self.old_vals = []
        self.actions: list[BaseUndoAction] = []
        self.stats = stats
        for stat in stats:
            self.old_vals.append(char.__dict__[stat])

    def update(self):
        for i in range(0, len(self.stats)):
            self.actions.append(
                StatUndoAction(
                    self.character_tag,
                    self.stats[i],
                    self.old_vals[i],
                    self.char.__dict__[self.stats[i]]
                )
            )

    def __str__(self):
        return "\n".join(str(action) for action in self.actions)

    def undo(self, executing_user: str):
        if len(self.actions) == 0:
            raise Exception("A multiple stat is empty")
        return f"Undid changes:\n" + "\n".join(action.undo(executing_user) for action in self.actions)

    def redo(self, executing_user: str):
        return f"Reapplied changes\n" + "\n".join(action.redo(executing_user) for action in self.actions)
