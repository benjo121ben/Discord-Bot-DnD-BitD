from src.ext.command_exceptions import *
from discord.ext.commands import Context
from src import GlobalVariables


def check_admin(ctx: Context) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return ctx.author.id == GlobalVariables.admin_id


def check_min_command_arg_len(min: int, *args, throw_error=True):
    return check_contained_command_arg_len(min, -1, *args, throw_error)


# This checks in case of missing parameters or invalid amounts. does not cover multiple versions of same Command
def check_contained_command_arg_len(min: int, max: int, *args, throw_error=True):
    if max != -1 and len(args) > max:
        if throw_error:
            raise TooManyArgumentsException(max)
    elif len(args) < min:
            return False
    return True
