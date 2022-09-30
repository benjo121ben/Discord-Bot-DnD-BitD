import campaign_helper as cmp_hlp
import packg_variables as pkg_var
from collections import deque


class UndoAction:
    def __init__(self, character_name: str, stat: str, new_val, old_val):
        self.stat = stat
        self.character_name = character_name
        self.new_val = new_val
        self.old_val = old_val

    def undo(self) -> str:
        pkg_var.charDic[self.character_name].__dict__[self.stat] = self.old_val
        return f"Undid change of {self.stat}. Returned to {self.old_val}"

    def redo(self):
        pkg_var.charDic[self.character_name].__dict__[self.stat] = self.new_val
        return f"Reapplied change of {self.stat}. Changed to {self.new_val}"


class MultipleBaseAction(UndoAction):
    def __init__(self, character_name: str, stat: str, old_val, new_val, stat2: str, old_val2: str, new_val2: str):
        super().__init__(character_name, stat, new_val, old_val)
        self.action1 = UndoAction(character_name, stat, new_val, old_val)
        self.action2 = UndoAction(character_name, stat2, new_val2, old_val2)

    def undo(self):
        self.action1.undo()
        self.action2.undo()
        return f"Undid changes to {self.action1.stat} and {self.action2.stat}"

    def redo(self):
        self.action1.redo()
        self.action2.redo()
        return f"Reapplied changes to {self.action1.stat} and {self.action2.stat}"


actionQueue: deque[UndoAction] = deque()
pointer = -1


def queue_action(action: UndoAction):
    global pointer, actionQueue
    for i in range(0, len(actionQueue) - pointer + 1):
        actionQueue.pop()
    if len(actionQueue) > 10:
        actionQueue.popleft()
    actionQueue.append(action)
    pointer += 1


def undo():
    global pointer
    if pointer > -1:
        ret_val = actionQueue[pointer].undo()
        pointer -= 1
        return ret_val
    else:
        return "No actions to undo"
