from discord import Interaction, ApplicationContext


class ContextInfo:
    def __init__(self, interaction: Interaction = None, ctx: ApplicationContext = None):
        if (interaction is None and ctx is None) or (interaction is not None and ctx is not None):
            raise RuntimeError(
                "When creating a contextInfo Object, you should only provide an interaction or a context object")
        if interaction is not None:
            self.ctxType = False
            self.interaction: Interaction = interaction
            self.author = interaction.user
        elif ctx is not None:
            self.ctxType = True
            self.ctx: ApplicationContext = ctx
            self.author = ctx.author

    async def respond(self, *args, **kwargs):
        if not self.ctxType:
            await self.interaction.followup.send(*args, **kwargs)
        elif self.ctxType:
            await self.ctx.respond(*args, **kwargs)


async def initContext(interaction: Interaction = None, ctx: ApplicationContext = None) -> ContextInfo:
    context = ContextInfo(interaction=interaction, ctx=ctx)
    if interaction is not None:
        await context.interaction.response.defer()
    return context
