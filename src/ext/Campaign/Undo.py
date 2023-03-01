from collections import deque

from .UndoActions.BaseUndoAction import BaseUndoAction
from .UndoActions.StatUndoAction import StatUndoAction

undo_dict = {}

queue_tag = "queue"
pointer_tag = "pointer"
timer_tag = "timer"


def get_action_queue(executing_user: str) -> deque[BaseUndoAction]:
    check_user_undo(executing_user)
    return undo_dict[executing_user][queue_tag]


def check_user_undo(executing_user: str):
    if executing_user in undo_dict:
        return
    else:
        undo_dict[executing_user] = {}
        undo_dict[executing_user][queue_tag] = deque()
        undo_dict[executing_user][pointer_tag] = -1


def get_pointer(executing_user: str) -> int:
    check_user_undo(executing_user)
    return undo_dict[executing_user][pointer_tag]


def set_pointer(executing_user: str, pointer: int):
    check_user_undo(executing_user)
    undo_dict[executing_user][pointer_tag] = pointer


def queue_undo_action(executing_user: str, action: BaseUndoAction):
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    while len(action_queue) > pointer + 1:
        action_queue.pop()
    action_queue.append(action)
    if len(action_queue) > 10:
        action_queue.popleft()
    else:
        pointer += 1
    set_pointer(executing_user, pointer)


def queue_basic_action(executing_user: str, char_tag, stat, old_val, new_val):
    queue_undo_action(executing_user, StatUndoAction(char_tag, stat, old_val, new_val))


def undo(executing_user: str) -> str:
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    if pointer > -1:
        ret_val = action_queue[pointer].undo(executing_user)
        pointer -= 1
        set_pointer(executing_user, pointer)
        return ret_val
    else:
        return "No actions to undo"


def redo(executing_user: str) -> str:
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    if pointer < len(action_queue) - 1:
        pointer += 1
        set_pointer(executing_user, pointer)
        return action_queue[pointer].redo(executing_user)
    else:
        return "No actions to redo"


def discard_undo_queue(executing_user: str):
    pointer = get_pointer(executing_user)
    action_queue = get_action_queue(executing_user)
    while len(action_queue) > pointer + 1:
        action_queue.pop()
