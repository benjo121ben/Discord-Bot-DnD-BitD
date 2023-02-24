from discord.ext.bridge import BridgeExtContext
from . import GlobalVariables


def check_admin(ctx: BridgeExtContext) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return ctx.author.id == GlobalVariables.admin_id
