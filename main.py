import os
import logging
import importlib
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("bot-in-the-dark")


def _is_modern_discord_py() -> bool:
    try:
        major_version = int(getattr(discord, "__version__", "0").split(".")[0])
    except (ValueError, TypeError, AttributeError):
        major_version = 0

    if major_version >= 2:
        return True

    try:
        importlib.import_module("discord.app_commands")
    except Exception:
        return False
    return True


def _ensure_compatibility() -> None:
    if _is_modern_discord_py():
        return
    version = getattr(discord, "__version__", "unknown")
    raise RuntimeError(
        "This bot requires discord.py 2.x (app_commands support). "
        f"Detected discord version: {version}. "
        "Install requirements and run using the workspace virtual environment."
    )


def _get_bool_env(var_name: str, default: bool = False) -> bool:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_optional_int_env(var_name: str) -> int | None:
    value = os.getenv(var_name)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid %s value %r; ignoring.", var_name, value)
        return None


intents = discord.Intents.default()
intents.message_content = _get_bool_env("ENABLE_MESSAGE_CONTENT_INTENT", default=False)


class BotInTheDark(commands.Bot):
    def __init__(self, *, dev_guild_id: int | None, sync_commands: bool):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        if not hasattr(self, "tree"):
            if _is_modern_discord_py():
                self.tree = discord.app_commands.CommandTree(self)
                logger.warning(
                    "commands.Bot did not initialize command tree automatically; "
                    "initialized fallback tree. Verify interpreter/package consistency."
                )
            else:
                _ensure_compatibility()
        self.dev_guild_id = dev_guild_id
        self.sync_commands = sync_commands

    async def setup_hook(self) -> None:
        if not self.sync_commands:
            logger.info("Command sync disabled via SYNC_COMMANDS.")
            return

        if self.dev_guild_id is not None:
            guild = discord.Object(id=self.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info("Synced %s command(s) to guild %s.", len(synced), self.dev_guild_id)
            return

        synced = await self.tree.sync()
        logger.info("Synced %s global command(s).", len(synced))


bot = BotInTheDark(
    dev_guild_id=_get_optional_int_env("DEV_GUILD_ID"),
    sync_commands=_get_bool_env("SYNC_COMMANDS", default=True),
)

@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)

@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    _ensure_compatibility()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables.")
        exit(1)

    bot.run(token)
