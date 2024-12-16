from discord.ext.commands import Cog, command, Context, has_permissions
from discord import Message, Embed, Member

class Welcome(Cog):
    def __init__(self):
        super().__init__()

    @Cog.listener(name='on_member_join')
    async def on_member_join(self, member:Member):
        description = f"Be sure to get <#1306410018324877312> and checkout <#1306305360554102907>\nDont forget to create a profile using </matching profile create:1307464778163421185> in <#1306409460750876672>"
        welcome_embed = Embed(title="Welcome", description=description, color=0xffa1dc)
        welcome_embed.set_author(name=member.global_name, icon_url=member.avatar.url)
        
        welcome_channel = member.guild.get_channel(1298611846995116194)
        await welcome_channel.send(embed=welcome_embed, content=f"Welcome {member.mention}")
    
    @command(name="test_welcome")
    @has_permissions(administrator=True)
    async def test_welcome(self, ctx:Context):
        member = ctx.author

        description = f"Be sure to get <#1306410018324877312> and checkout <#1306305360554102907>\nDont forget to create a profile using </matching profile create:1307464778163421185> in <#1306409460750876672>"
        welcome_embed = Embed(title="Welcome", description=description, color=0xffa1dc)
        welcome_embed.set_author(name=member.global_name, icon_url=member.avatar.url)
        
        welcome_channel = member.guild.get_channel(1298611846995116194)
        await welcome_channel.send(embed=welcome_embed, content=f"Welcome {member.mention}")





    
    
