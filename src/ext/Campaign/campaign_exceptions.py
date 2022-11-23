class CommandException(Exception):
    pass


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
