# Matchmaking features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, Group
from discord.ext.commands import Cog
from database import matching, generate_profile_description
from matchingui import ProfileCreationView









class Matching(Cog):
    def __init__(self) -> None:
        super().__init__()

    
    matching = Group(name="matching", description="group of matching commands")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    @matching.command()
    async def match(self, interaction:Interaction):
        await interaction.response.send_message("Kill yourself @castaways")

    @profile.command(name="create")
    async def profile_create(self, interaction:Interaction):       

        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(), ephemeral=True)
    
    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):       

        matching.delete_one({"user_id":interaction.user.id})

        await interaction.response.send_message("Your profile has been deleted! Whoops sorry for no confirm deletion button", ephemeral=True)
