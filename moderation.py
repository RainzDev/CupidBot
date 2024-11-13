#Moderation Features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, describe
from discord.ext.commands import Cog
from database import infractions
import time

class Moderation(Cog):
    def __init__(self) -> None:
        super().__init__()
    
    @command(name="infract", description="Infract a user, 0 points counts as a note")
    @describe(
        member="The member you want to infract",
        reason="The reason for the infraction",
        points="The amount of points you wish to add to this infraction"

    )
    async def infract(self, interaction:Interaction, member:Member, reason:str, points:int=0):
        expiration = int(time.time()+84000*points)
        data = {
            "user_id":member.id,
            "mod_id": interaction.user.id,
            "reason":reason,
            "points":points,
            "expires": expiration
        }
        resp = infractions.insert_one(data)
        description = f"❥﹒User: {member.mention}\n❥﹒Expiration: <t:{expiration}:R>\n❥﹒Reason:\n`{reason}`"
        moderation_embed = Embed(title="Infraction", description=description, color=0xff964f)
        moderation_embed.set_author(name=f"{member.global_name} | {member.id}", icon_url=member.avatar.url)
        moderation_embed.set_footer(text=f"Infraction Id: {resp.inserted_id}")

        await interaction.response.send_message(content=f"I have infracted {member.mention}", embed=moderation_embed)
