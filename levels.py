# Level Features for the bot
from discord import Embed, Member, Message, Interaction, File
from discord.app_commands import command, Group
from discord.ext.commands import Cog
from database import levels as levels_data, config

from imagegen import generate_level, int_to_ordinal

import random

class Levels(Cog):
    def __init__(self) -> None:
        
        super().__init__()
    
    # event listener for level ups

    ### TODO
        # Refactor level rewards
        # Add an add / remove dict per level in the config file
        # on every message, check to see if the user has their level rewards, this is it get rid of the "fix" command
        

    @Cog.listener('on_message')
    async def on_message(self, message:Message):
        
        if message.author.bot: return
        if not message.guild: return # if not sent in a guild, ignore
        config_data:dict = config.find_one({"server_id":message.guild.id})
        data:dict = levels_data.find_one({"user_id":message.author.id})
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


        

        levels_data.update_one({"user_id":message.author.id}, {"$set": {"xp":xp, "level":level}}, upsert=True)
        if levelup:
            data:dict = config.find_one({"server_id":message.guild.id})
            chan_id = data.get("levelup_chan", None)
            if chan_id:
                chan = message.guild.get_channel(chan_id)
            else:
                chan = message.channel
            await chan.send(f"Congratulations {message.author.mention}! You leveled up to `{level}`")
        
    
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
        levels_data.update_one({"user_id":member.id}, {"$set":{"xp":xp}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s xp to `{xp}`")
    


    @levels.command(name="set_level", description="sets a users level")
    async def level_set_level(self, interaction:Interaction, member:Member, level:int):
        levels_data.update_one({"user_id":member.id}, {"$set":{"level":level}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s level to `{level}`")

    
    @levels.command(name="fix", description="give yourself the roles you deserve")
    async def level_fix(self, interaction:Interaction, member:Member=None):
        await interaction.response.defer()
        member = member if member else interaction.user

        config_data:dict = config.find_one({"server_id":interaction.guild.id})
        member_data = levels_data.find_one({'user_id':member.id})

        
        level_rewards:dict = config_data.get('level_roles', None)
        closest_level = max(int(level) for level in level_rewards.keys() if int(level) <= member_data.get('level'))

        print(closest_level)

        rewards = level_rewards.get(str(closest_level))

        if rewards:
            earned_roles = [interaction.guild.get_role(role_id) for role_id in rewards]
            new_roles = list(set(member.roles) | set(earned_roles))
            await member.edit(roles=new_roles)
        
        await interaction.followup.send('Done!')
    
    

        


    
    

    
    
