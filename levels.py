# Level Features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, Group
from discord.ext.commands import Cog
from database import levels, config

import random

class Levels(Cog):
    def __init__(self) -> None:
        
        super().__init__()
    
    # event listener for level ups
    @Cog.listener('on_message')
    async def on_message(self, message:Message):
        if message.author.bot: return
        config_data:dict = config.find_one({"server_id":message.guild.id})
        data:dict = levels.find_one({"user_id":message.author.id})
        levelup = False
        if not data:
            xp = 0
            level = 1
            #check for level 1 rewards
            levelup = True

            level_rewards:dict = config_data.get('level_roles', None)
            rewards = level_rewards.get(str(level), None)
            if rewards:
                earned_roles = [message.guild.get_role(role_id) for role_id in rewards]
                new_roles = list(set(message.author.roles) | set(earned_roles))
                await message.author.edit(roles=new_roles)

        else:
            xp = data.get("xp")
            level = data.get("level")
        
        xp_required = level*100
        xp_mul = 1

        if message.author.premium_since:
            xp_mul = 1.15

        xp+= int(random.randint(1,40) * xp_mul)
        

        if xp >= xp_required:
            leftover = xp%xp_required
            level +=1
            xp = leftover
            levelup = True

            # check for role update
            
            level_rewards:dict = config_data.get('level_roles', None)
            rewards = level_rewards.get(str(level), None)

            if rewards:
                earned_roles = [message.guild.get_role(role_id) for role_id in rewards]
                new_roles = list(set(message.author.roles) | set(earned_roles))
                await message.author.edit(roles=new_roles)


        

        levels.update_one({"user_id":message.author.id}, {"$set": {"xp":xp, "level":level}}, upsert=True)
        if levelup:
            data:dict = config.find_one({"server_id":message.guild.id})
            chan_id = data.get("levelup_chan", None)
            if chan_id:
                chan = message.guild.get_channel(chan_id)
            else:
                chan = message.channel
            await chan.send(f"Congratulations {message.author.mention}! You leveled up to `{level}`")
        
    
    @command()
    async def view_level(self, interaction:Interaction, member:Member=None, hidden:bool=False):
        if not member: member = interaction.user
        data:dict = levels.find_one({"user_id":member.id})
        if not data:
            xp = 0
            level = 1
        else:
            xp = data.get("xp")
            level = data.get("level")
        
        level_embed = Embed(title="Level", description=f"❥﹒Level: `{level}`\n❥﹒Xp: `{xp}/{level*100}`\n", color=0xffa1dc)
        level_embed.set_author(name=member.global_name, icon_url=member.avatar.url)
        level_embed.set_footer(text="This will be a pretty UI at somepoint!")
        await interaction.response.send_message(embed=level_embed, ephemeral=hidden)
    

    levels = Group(name="level", description="A group of level based commands", default_permissions=None)
    

    @levels.command(name="set_xp", description="sets a users xp")
    async def level_set_xp(self, interaction:Interaction, member:Member, xp:int):
        levels.update_one({"user_id":member.id}, {"$set":{"xp":xp}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s xp to `{xp}`")
    


    @levels.command(name="set_level", description="sets a users level")
    async def level_set_level(self, interaction:Interaction, member:Member, level:int):
        levels.update_one({"user_id":member.id}, {"$set":{"level":level}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s level to `{level}`")
    
    

        


    
    

    
    
