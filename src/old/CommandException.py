class CommandException(Exception):
    def __init__(self, message="Custom Command failed. Somthing has gone very wrong"):
        self.message = message
        super().__init__(self.message)


class CommandArgAmountException(CommandException):
    def __init__(self, arguments_needed, message="invalid arguments for this command. Needed: "):
        self.message = message
        self.arguments_needed = arguments_needed
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}{self.arguments_needed}'


class InvalidGameException(CommandException):
    def __init__(self, game_id, message="Game with this id does not exist. ID= "):
        self.message = message
        self.game_id = game_id
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}{self.game_id}'
