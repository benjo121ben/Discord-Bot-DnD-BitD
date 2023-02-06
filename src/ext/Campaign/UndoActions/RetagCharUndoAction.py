import src.ext.Campaign.SaveDataManagement.char_data_access
from .BaseUndoAction import BaseUndoAction


class RetagCharUndoAction(BaseUndoAction):
    def __init__(self, old_tag: str, new_tag: str):
        self.old_tag = old_tag
        self.new_tag = new_tag

    def __str__(self):
        return f"{{char_retag}}=({self.old_tag}->{self.new_tag})"

    def undo(self, executing_user: str) -> str:
        src.ext.Campaign.SaveDataManagement.char_data_access.retag_char(executing_user, self.new_tag, self.old_tag)
        return f"Undid rentag of {self.old_tag} to {self.new_tag}. Returned to {self.old_tag}."

    def redo(self, executing_user: str):
        src.ext.Campaign.SaveDataManagement.char_data_access.retag_char(executing_user, self.old_tag, self.new_tag)
        return f"Reapplied retag of {self.old_tag} to {self.new_tag}."
