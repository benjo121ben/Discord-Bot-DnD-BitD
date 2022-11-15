from .Character import Character
from .campaign_helper import save, load, check_char_tag, check_file_loaded, rename_char_tag, \
    get_current_save_file_name_no_suff, check_if_user_has_char, get_char_tag_by_id, check_file_admin, session_tag
from .campaign_exceptions import CommandException
from .packg_variables import localCommDic, charDic, imported_dic
from . import Undo


def load_file(file_name: str) -> str:
    old_file_name = get_current_save_file_name_no_suff()
    ret_str = load(file_name)
    Undo.queue_undo_action(Undo.FileChangeUndoAction(old_file_name, get_current_save_file_name_no_suff()))
    return ret_str


def claim_character(executing_user: int, char_tag: str, assigned_user_id: int):
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    if check_if_user_has_char(assigned_user_id):
        raise CommandException(
            f"this user already has character {get_char_tag_by_id(assigned_user_id)} assigned")
    current_player = charDic[char_tag].player

    if current_player != "" and int(current_player) != executing_user and not check_file_admin(executing_user):
        raise CommandException(
            "You are not authorized to assign this character. It has already been claimed by a user.")
    charDic[char_tag].player = str(assigned_user_id)
    Undo.queue_basic_action(char_tag, "player", current_player, str(assigned_user_id))
    save()
    return f"character {char_tag} assigned to {assigned_user_id}"


def unclaim_user(executing_user: int, to_unclaim_user_id: int):
    check_file_loaded(raise_error=True)
    if to_unclaim_user_id != executing_user and not check_file_admin(executing_user):
        raise CommandException("You are not authorized to use this command on other people's characters")
    if not check_if_user_has_char(to_unclaim_user_id):
        raise CommandException("this user has no character assigned")
    char_tag = get_char_tag_by_id(to_unclaim_user_id)
    Undo.queue_basic_action(char_tag, "player", str(to_unclaim_user_id), "")
    charDic[char_tag].player = ""
    save()
    return f"Character {char_tag} unassigned"


def log(adv=False) -> str:
    ptr = Undo.get_pointer()
    check_file_loaded(raise_error=True)
    ret_string = f"**Session {imported_dic['session']}**\n"
    if len(charDic.values()) == 0:
        ret_string += "There are no characters at the moment\n"
    for char in charDic.values():
        ret_string += str(char) + "\n"

    if adv:
        ret_string += "---------\n"
        for indx, action in enumerate(Undo.actionQueue):
            if indx == ptr:
                ret_string += "-->"
            ret_string += str(action) + "\n---------\n"

    return ret_string


# adds new character to the roster
def add_char(tag: str, char_name: str, max_health: int) -> str:
    check_file_loaded(raise_error=True)
    if tag == "all":
        raise CommandException(
            "You are not allowed to call your character all, due to special commands using it a keyword."
            " Please call them something else"
        )

    if tag in charDic.keys():
        return "a character with this tag already exists"
    charDic[tag] = Character(tag, char_name, max_health)
    save()
    return "character " + char_name + " added"


def retag_character(char_tag_old: str, char_tag_new: str)->str:
    rename_char_tag(char_tag_old, char_tag_new)
    Undo.queue_undo_action(Undo.ReTagCharUndoAction(char_tag_old, char_tag_new))
    save()
    return f"Character {char_tag_old} has been renamed to {char_tag_new}"


# increases the caused damage stat
def cause_damage(char_tag: str, dam: int, kills: int) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    dam = abs(dam)
    kills = abs(kills)
    _char_name = charDic[char_tag].name
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_caused", "kills", "max_damage"])
    charDic[char_tag].cause_dam(dam, kills)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    if kills > 0:
        return f"character {_char_name} caused {dam} damage and kills {kills} enemies"
    return f"character {_char_name} caused {dam} damage"


# adds Damage taken to a character
def take_damage(char_tag: str, dam: int, resisted: bool) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    dam = abs(dam)
    _char_name = charDic[char_tag].name
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_taken", "health", "faints"])
    fainted, dam = charDic[char_tag].take_dam(dam, resisted)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    if fainted:
        return f"character {_char_name} takes {dam} damage and faints"
    else:
        return f"character {_char_name} takes {dam} damage"


def tank_damage(char_tag: str, amount: int) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    amount = abs(amount)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["damage_taken"])
    charDic[char_tag].tank(amount)
    save()
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    return f"{char_tag} tanks {amount} damage"


# heals character to their health maximum, corresponds to a long rest in D&D
def heal_max(char_tag: str) -> str:
    check_file_loaded(raise_error=True)
    if char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_max()
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        return "all characters were healed"
    _char_name = charDic[char_tag].name
    check_char_tag(char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "damage_healed"])
    charDic[char_tag].heal_max()
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    return "character " + _char_name + " healed to their maximum"


# heals by a certain amount
def heal(char_tag: str, healed: int) -> str:
    check_file_loaded(raise_error=True)
    healed = abs(healed)
    if char_tag == "all":
        for char in charDic.values():
            undo_action = Undo.MultipleBaseAction(char, ["health", "damage_healed"])
            char.heal_dam(healed)
            undo_action.update(char)
            Undo.queue_undo_action(undo_action)
        save()
        return f"All characters were healed by {healed}"
    else:
        check_char_tag(char_tag, raise_error=True)
        undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "damage_healed"])
        charDic[char_tag].heal_dam(healed)
        undo_action.update(charDic[char_tag])
        Undo.queue_undo_action(undo_action)
        save()
        _char_name = charDic[char_tag].name
        return "character " + _char_name + " healed " + str(healed)


# command usage: set_max char_name amount
def set_max_health(char_tag: str, new_max: int) -> str:
    new_max = abs(new_max)
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    undo_action = Undo.MultipleBaseAction(charDic[char_tag], ["health", "max_health"])
    charDic[char_tag].set_max_health(new_max)
    undo_action.update(charDic[char_tag])
    Undo.queue_undo_action(undo_action)
    save()
    _char_name = charDic[char_tag].name
    return "character " + _char_name + " health increased to " + str(new_max)


def crit(char_tag: str) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    crits = charDic[char_tag].crits
    Undo.queue_basic_action(char_tag, "crits", crits, crits + 1)
    charDic[char_tag].rolled_crit()
    save()
    return f"Crit of {char_tag} increased by 1"


def dodged(char_tag:str) -> str:
    check_file_loaded(raise_error=True)
    check_char_tag(char_tag, raise_error=True)
    dodged = charDic[char_tag].dodged
    Undo.queue_basic_action(char_tag, "dodged", dodged, dodged + 1)
    charDic[char_tag].dodge()
    save()
    return f"Character {char_tag}, dodged an attack"


def session_increase():
    check_file_loaded(raise_error=True)
    imported_dic[session_tag] += 1
    save()
    return "finished session, increased by one"


def undo_command(amount: int):
    check_file_loaded(raise_error=True)
    if amount > 10:
        amount = 10
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.undo() + "\n"
        if not get_current_save_file_name_no_suff() == "":
            save()
    return ret_val


def redo_command(amount: int) -> str:
    check_file_loaded(raise_error=True)
    ret_val = ""
    for _ in range(amount):
        ret_val += Undo.redo() + "\n"
        if not get_current_save_file_name_no_suff() == "":
            save()
    return ret_val


def setup_commands():
    def add_to_commands(com_name: str, command):
        localCommDic[com_name] = command

    # all used commands need to be added in order to work
    add_to_commands('addC', add_char)
    add_to_commands('cause', cause_damage)
    add_to_commands('take', take_damage)
    add_to_commands('set_health', set_max_health)
    add_to_commands('heal', heal)
    add_to_commands('healm', heal_max)
    add_to_commands('log', log)
