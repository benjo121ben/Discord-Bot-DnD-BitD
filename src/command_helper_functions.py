from discord import ApplicationContext
from . import GlobalVariables


def check_admin(ctx: ApplicationContext) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return str(ctx.author.id) == str(GlobalVariables.admin_id)
