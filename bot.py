from discord.ext.commands import Bot, is_owner, Context
from discord import Intents, Embed
from settings import TOKEN

#Cog Modules
from levels import Levels
from moderation import Moderation
from config import Config
from matching import Matching
from roles import RoleView

class Bot(Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=Intents.all())

    async def setup_hook(self) -> None:
        self.add_view(RoleView())
        await self.add_cog(Levels())
        await self.add_cog(Moderation())
        await self.add_cog(Config())
        await self.add_cog(Matching())




bot = Bot()
tree = bot.tree


@bot.command()
async def pfp(ctx:Context):
    await ctx.send(f"`{ctx.author.avatar.url}`")

@bot.command()
@is_owner()
async def send_roles(ctx:Context):
    
    description = """
    Select a color from any of the options below

    <:White:1307861241536057385> <@&1307855860034306068>
    <:Pink:1307861237719240868> <@&1307856243314004028>
    <:Red:1307861240684478614> <@&1307855826173694013>
    <:Orange:1307861236431589468> <@&1307855837385064478> 
    <:Yellow:1307861278336749588> <@&1307855838802870362>
    <:Green:1307861235177492501> <@&1307855840262361160> 
    <:Blue:1307861233873195148> <@&1307855841491288086> 
    <:Purple:1307861239413604383> <@&1307855850836070460> 
    <:Black:1307861232887267358> <@&1307855861577809990>
    """.strip()

    role_embed = Embed(title='Color Roles', description=description, color=0xffa1dc)
    await ctx.send(embed=role_embed, view=RoleView())


@bot.command()
@is_owner()
async def sync(ctx:Context):
    msg = await ctx.send("Syncing..")
    await tree.sync()
    await msg.edit(content="Done!")


bot.run(TOKEN)