#Configuration commands for the bot
from discord import Embed, Member, Message, Interaction, TextChannel, Role
from discord.app_commands import command, describe, Group
from discord.ext.commands import Cog
from database import config
import time

class Config(Cog):
    def __init__(self):
        super().__init__()
    
    config = Group(name="config", description="a group of config commands", default_permissions=None)
    levels = Group(name="levels", description="Subgroup of level config commands", parent=config, default_permissions=None)

    # level configuration
    @levels.command(name="channel", description="configure the level up channel")
    @describe(
        channel="the text channel for the leveup messages to go"
    )
    async def config_levels_chan(self, interaction:Interaction, channel:TextChannel=None):
        if not channel:
            config.update_one({"server_id":interaction.guild_id}, {"$unset": {"levelup_chan":""}}, upsert=True)
            await interaction.response.send_message(f"I have set the levelup channel to {channel}")
            return
        else:
            config.update_one({"server_id":interaction.guild_id}, {"$set":{"levelup_chan":channel.id}}, upsert=True)
            await interaction.response.send_message(f"I have set the levelup channel to {channel.mention}")
    


    @levels.command(name="reward", description="role rewards for certain level achivements")
    @describe(
        level="The level for this reward",
        roles="a list of roles for this reward to acquire, must be seperated by a comma"
    )
    async def config_levels_reward(self, interaction:Interaction, level:int, roles:str):
        try:
            role_ids = [int(role.strip().strip('<@&').strip('>')) for role in roles.split(',')]
        except:
            return await interaction.response.send_message("An error occured! did you forget to put a , between roles?")
        
        config.update_one({"server_id":interaction.guild_id}, {"$set":{f"level_roles.{level}":role_ids}}, upsert=True)
        
        role_msg = ", ".join(interaction.guild.get_role(role).mention for role in role_ids)
        update_embed = Embed(title='Level Rewards', description=f"I have updated the roles for level {level} to be:\n{role_msg}")
        
        await interaction.response.send_message(embed=update_embed)


