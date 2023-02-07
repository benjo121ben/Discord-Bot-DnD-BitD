from .BaseUndoAction import BaseUndoAction
from ..SaveDataManagement import live_save_manager as lsave


class StatUndoAction(BaseUndoAction):
    def __init__(self, character_tag: str, stat: str, old_val, new_val):
        self.stat = stat
        self.character_tag = character_tag
        self.new_val = new_val
        self.old_val = old_val

    def __str__(self):
        return f"{{{self.character_tag},{self.stat}}}=({self.old_val}->{self.new_val})"

    def undo(self, executing_user: str) -> str:
        lsave.get_loaded_chars(executing_user)[self.character_tag].__dict__[self.stat] = self.old_val
        return f"Undid {{{self.character_tag}, {self.stat}}}->{self.new_val}. Returned to {self.old_val}"

    def redo(self, executing_user: str):
        lsave.get_loaded_chars(executing_user)[self.character_tag].__dict__[self.stat] = self.new_val
        return f"Reapplied change of {{{self.character_tag}, {self.stat}}}{self.old_val}->{self.new_val}"