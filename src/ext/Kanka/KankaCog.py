import logging
from typing import Union

import requests
from discord import ApplicationContext
from discord.ext import commands

from ...UserSaveDataManagement import load_user_dict, kanka_data_tag, save_user_dict

logger = logging.getLogger('bot')
kanka_id_tag = "id"
kanka_token_tag = "token"


def load_kanka_data(user_id: str) -> Union[dict, None]:
    user_dict = load_user_dict(user_id)
    if kanka_data_tag not in user_dict or len(user_dict[kanka_data_tag]) == 0:
        return None
    return user_dict[kanka_data_tag]


class KankaCog(commands.Cog):
    @commands.slash_command(name="kanka", description="Query a kanka database you or your dungeonmaster has set up")
    async def kanka(self, ctx: ApplicationContext, query_keyword: str):
        kanka_data = load_kanka_data(str(ctx.author.id))
        if kanka_data is None:
            await ctx.respond("No kanka information set yet. Please use the _kanka\_setup_ command")
            return
        if kanka_token_tag not in kanka_data:
            await ctx.respond("Kanka API TOKEN not set. Generate one in your Kanka user settings then use the _kanka\_setup_ command")
            return
        if kanka_id_tag not in kanka_data:
            await ctx.respond("Kanka campaign ID not set. Please use the _kanka\_setup_ command")
            return
        search_query = 'https://kanka.io/api/1.0/campaigns/' + kanka_data[kanka_id_tag] + '/search/' + query_keyword
        r = requests.get(search_query ,
                         headers={"Authorization": f"Bearer {kanka_data[kanka_token_tag]}", "Content-type": "application/json"})
        if r.status_code != 200:
            await ctx.respond("There seems to have been an error making the request. Keep in mind that API Tokens stop working after 365 days.\n"
                              "Also make sure you have the correct campaign ID")
            return
        result_dict: dict = r.json()
        for val in result_dict["data"]:
            await ctx.respond(val["urls"]["view"])

    @commands.slash_command(name="kanka_setup", description="set/remove the campaign id in order to use the kanka command")
    async def kanka_setup(self, ctx: ApplicationContext, campaign_id: str = None, token: str = None, remove: bool = False):
        user_id = str(ctx.author.id)
        user_dict = load_user_dict(user_id)

        if campaign_id is None and token is None and not remove:  # user wants to check his currently set key
            if kanka_data_tag not in user_dict:
                await ctx.respond(f"No kanka information set yet. Please use the _kanka\_setup_ command")
                return
            kanka_data = user_dict[kanka_data_tag]
            token = kanka_data[kanka_token_tag][0:5] if kanka_token_tag in kanka_data else "not set"
            id = kanka_data[kanka_id_tag] if kanka_id_tag in kanka_data else "not set"
            await ctx.respond(f"Current kanka API token (first five letters): {token}\nCurrent Campaign ID: {id}")
            return

        if remove:
            if kanka_data_tag in user_dict:
                del user_dict[kanka_data_tag]
            await (await ctx.respond(f"kanka campaign ID removed")).delete_original_message(delay=10)
        else:
            base_data = {} if kanka_data_tag not in user_dict else user_dict[kanka_data_tag]
            ret_val = ""
            if campaign_id is not None:
                base_data[kanka_id_tag] = campaign_id
                ret_val += f"kanka campaign ID changed to: {campaign_id}\n"
            if token is not None:
                base_data[kanka_token_tag] = token
                ret_val += f"kanka token changed to (first five letters): {token[0:5]}"
            if ret_val != "":
                await (await ctx.respond(ret_val)).delete_original_message(delay=10)
            user_dict[kanka_data_tag] = base_data
        save_user_dict(user_id, user_dict)


def setup(bot: commands.Bot):
    # Every extension should have this function
    bot.add_cog(KankaCog())
    logger.info("kanka extension loaded\n")