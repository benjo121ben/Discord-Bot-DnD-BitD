from discord import Interaction, ApplicationContext, InteractionResponse


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
        delay = None
        if "delay" in kwargs:
            delay = kwargs["delay"]
            del kwargs["delay"]

        if not self.ctxType:
            response: InteractionResponse = self.interaction.response
            if not response.is_done():
                ret = await response.send_message(delete_after=delay, *args, **kwargs)
            else:
                ret = await self.interaction.followup.send(*args, **kwargs)
                if delay is not None:
                    ret = await ret.delete(delay=delay)
            return ret

        elif self.ctxType:
            ret = await self.ctx.respond(*args, **kwargs)
            if delay is not None:
                if isinstance(ret, Interaction):
                    ret = await ret.delete_original_response(delay=delay)
                else:
                    ret = await ret.delete(delay=delay)
            return ret


async def initContext(interaction: Interaction = None, ctx: ApplicationContext = None) -> ContextInfo:
    context = ContextInfo(interaction=interaction, ctx=ctx)
    if interaction is not None:
        await context.interaction.response.defer()
    return context
