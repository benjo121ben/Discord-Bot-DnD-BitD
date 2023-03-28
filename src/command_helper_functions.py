from discord.ext.bridge import BridgeExtContext
from . import GlobalVariables


def check_admin(ctx: BridgeExtContext) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return str(ctx.author.id) == str(GlobalVariables.admin_id)
