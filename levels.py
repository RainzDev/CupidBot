# Level Features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command
from discord.ext.commands import Cog
from database import levels

class Levels(Cog):
    def __init__(self) -> None:
        
        super().__init__()
    
    # event listener for level ups
    @Cog.listener('on_message')
    async def on_message(self, message:Message):
        if message.author.bot: return
        data:dict = levels.find_one({"user_id":message.author.id})
        levelup = False
        if not data:
            xp = 0
            level = 1
        else:
            xp = data.get("xp")
            level = data.get("level")
        
        xp_required = level*100
        xp+=20
        
        if xp >= xp_required:
            leftover = xp%xp_required
            level +=1
            xp = leftover
            levelup = True
        
        levels.update_one({"user_id":message.author.id}, {"$set": {"xp":xp, "level":level}}, upsert=True)
        if levelup:
            await message.channel.send(f"Congratulations {message.author.mention}! You leveled up to `{level}`")
        
    
    @command()
    async def level(self, interaction:Interaction, member:Member=None, hidden:bool=False):
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
        


    
    

    
    
