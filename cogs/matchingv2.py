from discord import Embed, Member, Interaction
from discord.ext.commands import Cog
from discord.app_commands import Group
from database.matchingdb import generate_profile_embed

class Matching(Cog):
    def __init__(self):
        super().__init__()

    matching = Group(name="matching", description="A group of commands for match making")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    @profile.command(name='create', description='a command to create a profile')
    async def matching_profile_create(self, interaction:Interaction):
        await interaction.response.send_message(embed=generate_profile_embed(interaction.user))
