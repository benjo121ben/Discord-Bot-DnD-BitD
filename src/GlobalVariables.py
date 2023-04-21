import discord.ext.bridge as bridge_com
import os
admin_id: str = None
modules_list: list[bool] = None
bot: bridge_com.Bot = None
env_file_rel_path = f'.{os.sep}.env'
bot_host_email: str = ""
logger = None

