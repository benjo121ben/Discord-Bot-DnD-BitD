from src.ext.command_exceptions import CommandException


class NotFileAdminException(CommandException):
    def __init__(self, msg=None):
        if msg is None:
            super().__init__("You are not authorised to use this command in this save_file")
        else:
            super().__init__(msg)


class NotBotAdminException(CommandException):
    def __init__(self, msg=None):
        if msg is None:
            super().__init__("You must be a BOT administrator to use this command")
        else:
            super().__init__(msg)


class SaveFileNotFoundException(CommandException):
    def __init__(self):
        super().__init__("The savefile was unexpectedly deleted")


class SaveFileImportException(CommandException):
    def __init__(self):
        super().__init__(f"The savefile you tried to import is from an old version that cannot be parsed, "
              f"I am sorry for this inconvenience. Please contact the bot creator")


class NoAssignedSaveException(CommandException):
    def __init__(self, m=""):
        if m == "":
            m = "No savefile has been loaded. Use the load command to load an existing file or create a new one"
        super().__init__(m)


class UserNotPlayerException(CommandException):
    def __init__(self, m=""):
        if m == "":
            m = "You are not a participant in this game, the admin of the file needs to add you via the add_player " \
                "command"
        super().__init__(m)


class UndoUpdateMissingException(Exception):
    def __init__(self):
        super().__init__("This UndoStatAction was not Updated")


class UndoMultipleStatException(Exception):
    def __init__(self):
        super().__init__("This UndoMultipleStatAction was not Updated")
