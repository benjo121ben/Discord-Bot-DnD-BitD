import src.ext.Campaign.campaign_helper as cmp_hlp
import src.ext.Campaign.packg_variables as pkg_var
from collections import deque
import abc
from .Character import Character


class UndoUpdateMissingException(Exception):
    def __init__(self):
        super().__init__("This UndoStatAction was not Updated")


class UndoMultipleStatException(Exception):
    def __init__(self):
        super().__init__("This UndoMultipleStatAction was not Updated")


class BaseUndoAction(abc.ABC):
    @abc.abstractmethod
    def undo(self) -> str:
        pass

    @abc.abstractmethod
    def redo(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self):
        pass


class StatUndoAction(BaseUndoAction):
    def __init__(self, character_name: str, stat: str, old_val, new_val):
        self.stat = stat
        self.character_name = character_name
        self.new_val = new_val
        self.old_val = old_val

    def __str__(self):
        return f"{{{self.character_name},{self.stat}}}=({self.old_val}->{self.new_val})"

    def undo(self) -> str:
        pkg_var.charDic[self.character_name].__dict__[self.stat] = self.old_val
        return f"Undid {{{self.character_name}, {self.stat}}}->{self.new_val}. Returned to {self.old_val}"

    def redo(self):
        pkg_var.charDic[self.character_name].__dict__[self.stat] = self.new_val
        return f"Reapplied change of {{{self.character_name}, {self.stat}}}{self.old_val}->{self.new_val}"


class FileChangeUndoAction(BaseUndoAction):
    def __init__(self, old_file: str, new_file: str):
        self.old_file = old_file
        self.new_file = new_file
        
    def __str__(self):
        return f"{{filechange}}=({self.old_file}->{self.new_file})"

    def undo(self) -> str:
        cmp_hlp.load(self.old_file)
        return f"Undid load of {self.new_file}. Returned to {self.old_file}."

    def redo(self):
        cmp_hlp.load(self.new_file)
        return f"Reapplied load of {self.new_file}."


class RenameCharUndoAction(BaseUndoAction):
    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name

    def __str__(self):
        return f"{{char_rename}}=({self.old_name}->{self.new_name})"

    def undo(self) -> str:
        cmp_hlp.rename_char(self.new_name, self.old_name)
        return f"Undid renaming of {self.old_name} to {self.new_name}. Returned to {self.old_name}."

    def redo(self):
        cmp_hlp.rename_char(self.old_name, self.new_name)
        return f"Reapplied rename of {self.old_name} to {self.new_name}."


class MultipleBaseAction(BaseUndoAction):
    def __init__(self, char: Character, stats: list[str]):
        self.character_name = char.name
        self.old_vals = []
        self.actions = []
        self.stats = stats
        for stat in stats:
            self.old_vals.append(char.__dict__[stat])

    def update(self, char: Character):
        for i in range(0, len(self.stats)):
            self.actions.append(
                StatUndoAction(
                    self.character_name,
                    self.stats[i],
                    self.old_vals[i],
                    char.__dict__[self.stats[i]]
                )
            )

    def __str__(self):
        return "\n".join(str(action) for action in self.actions)

    def undo(self):
        if len(self.actions) == 0:
            raise Exception("A multiple stat is empty")
        return f"Undid changes:\n" + "\n".join(action.undo() for action in self.actions)

    def redo(self):
        return f"Reapplied changes\n" + "\n".join(action.redo() for action in self.actions)


actionQueue: deque[BaseUndoAction] = deque()
pointer = -1

def get_pointer():
    return pointer


def queue_undo_action(action: BaseUndoAction):
    global pointer, actionQueue
    while len(actionQueue) > pointer + 1:
        actionQueue.pop()
    actionQueue.append(action)
    if len(actionQueue) > 10:
        actionQueue.popleft()
    else:
        pointer += 1


def queue_basic_action(char_name, stat, old_val, new_val):
    queue_undo_action(StatUndoAction(char_name, stat, old_val, new_val))


def undo():
    global pointer
    if pointer > -1:
        ret_val = actionQueue[pointer].undo()
        pointer -= 1
        return ret_val
    else:
        return "No actions to undo"


def redo():
    global pointer
    if pointer < len(actionQueue) - 1:
        pointer += 1
        return actionQueue[pointer].redo()
    else:
        return "No actions to redo"