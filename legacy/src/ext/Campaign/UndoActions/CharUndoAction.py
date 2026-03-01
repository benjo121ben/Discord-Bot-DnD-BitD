from typing import Optional

from .BaseUndoAction import BaseUndoAction
from ..SaveDataManagement import live_save_manager as lsave
from ..Character import Character


class CharUndoAction(BaseUndoAction):
    def __init__(self, old_char: Optional[Character], new_char: Optional[Character]):
        self.old_char = old_char
        self.new_char = new_char
        self.addition = new_char is not None

    def __str__(self):
        return f"{self.old_char.name if self.old_char is not None else ''}->{self.new_char.name if self.new_char is not None else ''}"

    def undo(self, executing_user: str) -> str:

        _dict = lsave.get_loaded_chars(executing_user)
        if self.addition:
            del _dict[self.new_char.tag]
            return f"Undid addition of {self.new_char.name}."
        else:
            _dict[self.old_char.tag] = self.old_char
            return f"Undid removal of {self.old_char.name}."

    def redo(self, executing_user: str):
        _dict = lsave.get_loaded_chars(executing_user)
        if self.addition:
            _dict[self.new_char.tag] = self.new_char
            return f"Added {self.new_char.name} back into file."
        else:
            del _dict[self.old_char.tag]
            return f"Removed {self.old_char.name} again."
