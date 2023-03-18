from typing import Any

from .BaseUndoAction import BaseUndoAction
from ..SaveDataManagement import live_save_manager as lsave


class ChangeFileDataUndoAction(BaseUndoAction):
    def __init__(self, stat: str, old_value: Any, new_value: Any):
        self.stat = stat
        self.old_value = old_value
        self.new_value = new_value

    def __str__(self):
        return f"{{{self.stat}}}=({self.old_value}->{self.new_value})"

    def undo(self, executing_user: str) -> str:
        lsave.get_loaded_dict(executing_user)[self.stat] = self.old_value
        return f"Undid change of {self.stat}. Returned to {self.old_value}."

    def redo(self, executing_user: str):
        lsave.get_loaded_dict(executing_user)[self.stat] = self.new_value
        return f"Redid change of {self.stat}. Returned to {self.new_value}."
