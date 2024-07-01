from discord import ApplicationContext, Member, Interaction, InteractionResponded
from . import GlobalVariables
from .ContextInfo import init_context

MESSAGE_DELETION_DELAY: int = 10


def check_admin(ctx: ApplicationContext) -> bool:
    if GlobalVariables.admin_id is None:
        return True
    else:
        return str(ctx.author.id) == str(GlobalVariables.admin_id)


async def channel_perm_check(ctx: ApplicationContext):
    if ctx.guild is None:
        return True

    member_data: Member = ctx.guild.get_member(GlobalVariables.bot.user.id)
    if not ctx.channel.permissions_for(member_data).view_channel:
        await ctx.respond("The bot does not have permission to view this channel.\n"
                          "Some stuff just doesn't work without it, so please make sure you give it access. :)",
                          delete_after=MESSAGE_DELETION_DELAY
                          )
        return False
    return True


async def channel_perm_check_interaction(interaction: Interaction):
    if interaction.guild is None:
        return True

    member_data: Member = interaction.guild.get_member(GlobalVariables.bot.user.id)
    if not interaction.channel.permissions_for(member_data).view_channel:
        await (await init_context(interaction=interaction)).respond(
            "The bot does not have permission to view this channel.\n"
            "Some stuff just doesn't work without it, so please make sure you give it access. :)",
            delay=40
        )


# This will be deprecated in a future update of py-cord, which introduces interaction.respond and interaction.edit
# I'm making my own shorthand since I haven't yet figured out how to get access to that code
async def edit_interaction_message(interaction: Interaction, params: dict):
    if 'delay' in params:
        params['delete_after'] = params['delay']
        del params['delay']
    try:
        if not interaction.response.is_done():
            await interaction.response.edit_message(**params)
            return await interaction.original_response()
        else:
            return await interaction.edit_original_response(**params)
    except InteractionResponded:
        return await interaction.edit_original_response(**params)