#Moderation Features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, describe
from discord.ext.commands import Cog
from database.database import infractions
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
        description = f"❥﹒User: {member.mention}\n❥﹒Points: `{points}`\n❥﹒Expiration: <t:{expiration}:R>\n❥﹒Reason:\n`{reason}`"
        moderation_embed = Embed(title="Infraction", description=description, color=0xff964f)
        moderation_embed.set_author(name=f"{member.global_name} | {member.id}", icon_url=member.avatar.url)
        moderation_embed.set_footer(text=f"Infraction Id: {resp.inserted_id}")

        await interaction.response.send_message(content=f"I have infracted {member.mention}", embed=moderation_embed)
    

    @command(name="infractions", description="View all the infractions a user has")
    @describe(
        member="The member you want to view the infractions of",
        active="True if you want to see ONLY active infraction, false for ALL",
    )
    async def infractions(self, interaction:Interaction, member:Member, active:bool=False):
        
        resp = infractions.find({"user_id":member.id})

        # Create embed
        description = "Below are all the notes / infractions a user has"
        moderation_embed = Embed(title="Infractions", description=description.strip(), color=0xff964f)

        # compile notes aka 0 point infractions, and warnings
        notes = "\n"
        warnings = []

        def sort(x):
            return x == 0


        for i, record in enumerate(sorted(resp, key=sort)):
            if record.get('points') == 0:
                moderation_embed.add_field(name="Note", value=f"Id: `{str(record.get('_id'))}`\nBy: <@{record.get('mod_id')}>\nDated: <t:{record.get('expires')}:f>\nNote: `{record.get('reason')}`\n---", inline=False)
                continue
            if active:
                print(record.get('expires'), int(time.time()))
                if record.get('expires') < int(time.time()): continue
            warnings.append(record)
            moderation_embed.add_field(name=f"Infraction", value=f"Id: `{str(record.get('_id'))}`\nModerator: <@{record.get('mod_id')}>\nPoints: `{record.get('points')}`\nExpiration: <t:{record.get('expires')}:R>\nReason:\n`{record.get('reason')}`\n---", inline=False)
        
        notes.strip()

        # commit the notes
        
        moderation_embed.set_author(name=f"{member.global_name} | {member.id}", icon_url=member.avatar.url)
        moderation_embed.set_footer(text=f"To view a specific infraction, use /infraction id")

        await interaction.response.send_message(embed=moderation_embed)
