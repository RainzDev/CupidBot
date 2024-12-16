# Level Features for the bot
from discord import Embed, Member, Message, Interaction, File
from discord.app_commands import command, Group
from discord.ext.commands import Cog, is_owner
from database import levels as levels_data, config

from imagegen import generate_level, int_to_ordinal

import random

class Levels(Cog):
    def __init__(self) -> None:
        
        super().__init__()
    
    # event listener for level ups
    @Cog.listener('on_message')
    async def level_xp_gain(self, message:Message):
        user = message.author
        # check to see if we are not a bot and in a server, not dms
        if user.bot: return
        if not message.guild: return 

        # collect config data and user data
        config_data:dict = config.find_one({"server_id":message.guild.id})
        user_data:dict = levels_data.find_one({"user_id":user.id}) or {}

        # control variables
        levelup = False
        xp_multiplier = 1.75 if user.premium_since else 1 # boosters get 1.75x xp
        level = int(user_data.get('level', 0))
        xp = int(user_data.get('xp', 0))
        xp_required = level*100 if level > 0 else 50

        # stage the level up conditions

        xp += int(random.randint(1,40) * xp_multiplier)
        levelup = True if xp > xp_required else False
        leftover = xp%xp_required

        # increase xp and level on leve lup
        if levelup:
            level +=1
            xp = leftover

        # calculate rewards
        rewards_dict:dict = config_data.get('level_rewards')
        rewards_key = str(max((int(key) for key in rewards_dict if int(key) <= level), default=None))
        rewards:dict = rewards_dict.get(rewards_key, {})

        
        roles_to_add = set([message.guild.get_role(role_id) for role_id in rewards.get('add', [])])
        roles_to_remove = set([message.guild.get_role(role_id) for role_id in rewards.get('remove', [])])

        user_roles = set(user.roles)
        new_roles = (user_roles - roles_to_remove) | roles_to_add

        

        # add new roles to user
        if new_roles != user_roles:
            await user.edit(roles=new_roles)

        # update the users level
        levels_data.update_one({"user_id":message.author.id}, {"$set": {"xp":xp, "level":level}}, upsert=True)
        
        if levelup:
            chan_id = config_data.get("levelup_chan", message.channel)
            channel = message.guild.get_channel(chan_id)
            await channel.send(f"Congratulations {message.author.mention}! You leveled up to `{level}`")
        



    @command(description="View the level of yourself or another user")
    async def view_level(self, interaction:Interaction, member:Member=None, hidden:bool=False):
        await interaction.response.defer()
        if not member: member = interaction.user
        data:dict = levels_data.find_one({"user_id":member.id})
        leaderboard:list = sorted(levels_data.find(), key=lambda x:x.get('level'), reverse=True)
        user_ids = [record.get('user_id') for record in leaderboard] # make it easier to grab the index


        if not data:
            xp = 0
            level = 1
        else:
            xp = data.get("xp")
            level = data.get("level")

        
        rank_place= int_to_ordinal(user_ids.index(member.id) + 1)
        rank = f"{rank_place} Place"
        
        
        generate_level(member.name, level,rank,xp,member.avatar.url)
        file = File('output.png', filename=f"output_card.png")
        
        await interaction.followup.send(ephemeral=hidden, file=file)
    


    @command()
    async def leaderboard(self, interaction:Interaction):
        data:list = sorted(levels_data.find(), key=lambda x:x.get('level'), reverse=True)
        description = "\n".join(f"{i+1} | Level `{record.get('level')}` | Xp `{record.get('xp')}` |  {interaction.guild.get_member(int(record.get('user_id'))).mention}" for i, record in enumerate(data[0:10]))
        leaderboard_embed = Embed(title="Leaderboard", description=description, color=0xffa1dc)
        await interaction.response.send_message(embed=leaderboard_embed)



    levels = Group(name="level", description="A group of level based commands", default_permissions=None)
    



    @levels.command(name="set_xp", description="sets a users xp")
    async def level_set_xp(self, interaction:Interaction, member:Member, xp:int):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message("Fuck you for trying casties")
        levels_data.update_one({"user_id":member.id}, {"$set":{"xp":xp}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s xp to `{xp}`")
    


    @levels.command(name="set_level", description="sets a users level")
    async def level_set_level(self, interaction:Interaction, member:Member, level:int):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message("Fuck you for trying casties")
        levels_data.update_one({"user_id":member.id}, {"$set":{"level":level}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s level to `{level}`")

    
