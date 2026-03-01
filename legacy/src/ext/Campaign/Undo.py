from collections import deque

from .SaveDataManagement.TempEntryDict import TempEntryDict

from .UndoActions.BaseUndoAction import BaseUndoAction
from .UndoActions.StatUndoAction import StatUndoAction

UNDO_DELETION_SECONDS = 43200

QUEUE_TAG = "queue"
POINTER_TAG = "pointer"
TIMER_TAG = "timer"

undo_dict: TempEntryDict = TempEntryDict(UNDO_DELETION_SECONDS, "UndoDeque")


def get_action_queue(executing_user: str) -> deque[BaseUndoAction]:
    global undo_dict, QUEUE_TAG
    check_user_undo(executing_user)
    return undo_dict.get(executing_user)[QUEUE_TAG]


def get_pointer(executing_user: str) -> int:
    global undo_dict, POINTER_TAG
    check_user_undo(executing_user)
    return undo_dict.get(executing_user)[POINTER_TAG]


def check_user_undo(executing_user: str):
    global undo_dict, POINTER_TAG, QUEUE_TAG
    if executing_user in undo_dict:
        return
    else:
        undo_dict.set(executing_user, {QUEUE_TAG: deque(), POINTER_TAG: -1})


def set_pointer(executing_user: str, pointer: int):
    global undo_dict, POINTER_TAG
    check_user_undo(executing_user)
    undo_dict.get(executing_user)[POINTER_TAG] = pointer


def queue_undo_action(executing_user: str, action: BaseUndoAction):
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    discard_undo_queue_after_pointer(executing_user)
    action_queue.append(action)
    if len(action_queue) > 10:
        action_queue.popleft()
    else:
        pointer += 1
    set_pointer(executing_user, pointer)


def queue_basic_action(executing_user: str, char_tag, stat, old_val, new_val):
    queue_undo_action(executing_user, StatUndoAction(char_tag, stat, old_val, new_val))


def undo(executing_user: str) -> tuple[bool, str]:
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    if pointer > -1:
        ret_val = action_queue[pointer].undo(executing_user)
        pointer -= 1
        set_pointer(executing_user, pointer)
        return True, ret_val
    else:
        return False, "No actions to undo"


def redo(executing_user: str) -> tuple[bool, str]:
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    if pointer < len(action_queue) - 1:
        pointer += 1
        set_pointer(executing_user, pointer)
        return True, action_queue[pointer].redo(executing_user)
    else:
        return False, "No actions to redo"


def discard_undo_queue_after_pointer(executing_user: str):
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    while len(action_queue) > pointer + 1:
        action_queue.pop()


def reset_undo():
    global undo_dict
    undo_dict.clear()
