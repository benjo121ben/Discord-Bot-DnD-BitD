import logging

from discord import slash_command, ApplicationContext
from discord.ext.commands import Cog, Bot
from . import wrapped_commands as commands, campaign_helper as cmp_hlp
from .ContextInfo import initContext

logger = logging.getLogger('bot')


class CampaignCog(Cog):
    @slash_command(name="edit_char",
                   description="Use a simple button interface to change a characters' stats")
    async def view_char(self, ctx: ApplicationContext, char_tag: str = None):
        return await commands.sendCharView(await initContext(ctx=ctx), char_tag)

    @slash_command(
        name="add",
        description="Add character to save file. If user_id is provided, it tries to claim the character for that user"
    )
    async def add_c(self, ctx: ApplicationContext, char_tag: str, char_name: str, user_id: str = None):
        return await commands.add_c(await initContext(ctx=ctx), char_tag, char_name, user_id)

    @slash_command(
        name="remove",
        description="Remove character from save file."
    )
    async def rem_c(self, ctx: ApplicationContext, char_tag: str):
        return await commands.rem_c(await initContext(ctx=ctx), char_tag)

    # @slash_command(name="crit", description="Character has rollet a nat20")
    async def crit(self, ctx: ApplicationContext, amount: int = 1, char_tag: str = None):
        return await commands.crit((await initContext(ctx=ctx)), amount, char_tag)

    # @slash_command(name="faint", description="Character faints")
    async def faint(self, ctx: ApplicationContext, amount: int = 1, char_tag: str = None):
        return await commands.faint((await initContext(ctx=ctx)), amount, char_tag)

    # @slash_command(name="dodged", description="Character dodged an attack")
    async def dodged(self, ctx: ApplicationContext, amount: int = 1, char_tag: str = None):
        return await commands.dodged((await initContext(ctx=ctx)), amount, char_tag)

    # @slash_command(name="cause", description="Character causes damage to enemy")
    async def cause(self, ctx: ApplicationContext, amount: int, kills: int = 0, char_tag: str = None):
        return await commands.cause((await initContext(ctx=ctx)), amount, kills, char_tag)

    # @slash_command(name="take", description="Character takes full damage")
    async def take(self, ctx: ApplicationContext, amount: int, char_tag: str = None):
        return await commands.take((await initContext(ctx=ctx)), amount, char_tag)

    # @slash_command(name="taker", description="Character takes reduced damage")
    async def take_reduced(self, ctx: ApplicationContext, amount: int, char_tag: str = None):
        return await commands.take_reduced((await initContext(ctx=ctx)), amount, char_tag)

    # @slash_command(name="heal", description="Character heals another by amount. Increases damage_healed stat")
    async def heal(self, ctx: ApplicationContext, amount: int, char_tag: str = None):
        return await commands.heal((await initContext(ctx=ctx)), amount, char_tag)

    @slash_command(name="log", description="Outputs all current Character information")
    async def log(self, ctx: ApplicationContext, adv=False):
        return await commands.log((await initContext(ctx=ctx)), adv)

    @slash_command(
        name="retag",
        description="Change the tag of a character on the current save file."
    )
    async def retag_pc(self, ctx: ApplicationContext, char_tag_old: str, char_tag_new: str):
        return await commands.retag_pc((await initContext(ctx=ctx)), char_tag_old, char_tag_new)

    @slash_command(
        name="rename",
        description="Change the name of a character on the current save file."
    )
    async def rename_pc(self, ctx: ApplicationContext, char_tag: str, char_name_new: str):
        return await commands.rename_pc((await initContext(ctx=ctx)), char_tag, char_name_new)

    @slash_command(name="session", description="increase session counter by 1")
    async def session(self, ctx: ApplicationContext):
        return await commands.session((await initContext(ctx=ctx)))

    @slash_command(
        name="load",
        description="Load an existing campaign save file or create a new one"
    )
    async def load_command(self, ctx: ApplicationContext, file_name: str):
        return await commands.load_command((await initContext(ctx=ctx)), file_name)

    @slash_command(
        name="claim",
        description="Claim a character. If a userId is provided, the Character is assigned to that user instead"
    )
    async def claim(self, ctx: ApplicationContext, char_tag: str, user_id: str = None):
        return await commands.claim((await initContext(ctx=ctx)), char_tag, user_id)

    @slash_command(name="unclaim", description="Unclaim an assigned Character")
    async def unclaim(self, ctx: ApplicationContext, character_tag: str = None):
        return await commands.unclaim((await initContext(ctx=ctx)), character_tag)

    @slash_command(name="player_add", description="Remove player from this savefile")
    async def add_player(self, ctx: ApplicationContext, user_id: str):
        return await commands.add_player((await initContext(ctx=ctx)), user_id)

    @slash_command(name="player_rem", description="Remove player from this savefile")
    async def rem_player(self, ctx: ApplicationContext, user_id: str):
        return await commands.rem_player((await initContext(ctx=ctx)), user_id)

    @slash_command(name="cache", description="Admin command: caches the last save file into the provided server chat")
    async def cache(self, ctx: ApplicationContext):
        return await commands.cache((await initContext(ctx=ctx)))

    @slash_command(name="get_cache", description="Admin command: tries to download the latest save from cache server chat")
    async def get_cache(self, ctx: ApplicationContext):
        return await commands.get_cache((await initContext(ctx=ctx)))

    @slash_command(name="download", description="Downloads the loaded savefile")
    async def download(self, ctx: ApplicationContext):
        return await commands.download(ctx)

    @slash_command(name="undo", description="Undo your mistakes")
    async def undo(self, ctx: ApplicationContext, amount: int = 1):
        return await commands.undo(ctx, amount)

    @slash_command(name="redo", description="Redo your undone non-mistakes")
    async def redo(self, ctx: ApplicationContext, amount: int = 1):
        return await commands.redo(ctx, amount)


def setup(bot: Bot):
    cmp_hlp.check_base_setup()
    bot.add_cog(CampaignCog())

    logger.info("campaign extension loaded\n")
