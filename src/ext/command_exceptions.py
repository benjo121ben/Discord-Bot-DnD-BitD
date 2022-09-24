

class CommandException(Exception):
    pass


class NotEnoughArgumentsException(CommandException):
    def __init__(self, min_args: int, infinite=False):
        message = "Missing command Arguments, expected "
        if not infinite:
            message = "Missing command Arguments, expected at least "
        super(NotEnoughArgumentsException, self).__init__(message + str(min_args))


class InvalidArgumentException(CommandException):
    def __init__(self, argument_name: str):
        super(InvalidArgumentException, self).__init__("Argument " + argument_name + " has an invalid value")
