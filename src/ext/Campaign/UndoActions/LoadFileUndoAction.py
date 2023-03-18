from .BaseUndoAction import BaseUndoAction
from ..SaveDataManagement import live_save_manager as lsave


class LoadFileUndoAction(BaseUndoAction):
    def __init__(self, old_file: str, new_file: str):
        self.old_file = old_file
        self.new_file = new_file

    def __str__(self):
        return f"{{filechange}}=({self.old_file}->{self.new_file})"

    def undo(self, executing_user: str) -> str:
        lsave.access_file_as_user(executing_user, self.old_file)
        return f"Undid load of {self.new_file}. Returned to {self.old_file}."

    def redo(self, executing_user: str):
        lsave.access_file_as_user(executing_user, self.new_file)
        return f"Reapplied load of {self.new_file}."
