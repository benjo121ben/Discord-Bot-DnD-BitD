class CommandException(Exception):
    pass


class InvalidArgumentAmountException(CommandException):
    def __init__(self, nr_expected: int, infinite=False):
        message = "Missing command Arguments, expected "
        if not infinite:
            message = "Missing command Arguments, expected at least"
        super(InvalidArgumentAmountException, self).__init__(message + str(nr_expected))


class InvalidArgumentException(CommandException):
    def __init__(self, argument_name: str):
        super(InvalidArgumentException, self).__init__("Argument " + argument_name + " has an invalid value")
