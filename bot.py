from discord.ext.commands import Bot, is_owner, Context
from discord import Intents
from settings import TOKEN

#Cog Modules
from levels import Levels
from moderation import Moderation
from config import Config
from matching import Matching

class Bot(Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=Intents.all())

    async def setup_hook(self) -> None:
        await self.add_cog(Levels())
        await self.add_cog(Moderation())
        await self.add_cog(Config())
        await self.add_cog(Matching())




bot = Bot()
tree = bot.tree


@bot.command()
@is_owner()
async def sync(ctx:Context):
    msg = await ctx.send("Syncing..")
    await tree.sync()
    await msg.edit(content="Done!")


bot.run(TOKEN)