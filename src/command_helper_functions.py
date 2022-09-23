from src.ext.command_exceptions import *
from discord.ext.bridge import BridgeExtContext
from src import GlobalVariables


def check_admin(ctx: BridgeExtContext) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return ctx.author.id == GlobalVariables.admin_id


def check_min_command_arg_len(min: int, *args, throw_error=True):
    if len(args) < min:
        if throw_error:
            raise NotEnoughArgumentsException(min)
        else:
            return False
    return True


