from discord import Embed, Member, Interaction
from discord.ext.commands import Cog
from discord.app_commands import Group
from database.matchingdb import generate_profile_embed, NoProfileException, get_profile
from cogs.ui.profileui import TosConfirmationView, ProfileCreationView


tos_description = """
1.) Cupid Bot is designed to help users connect and make new friends in a fun and safe environment.

2.) The bot is strictly for friendship-based matchmaking and is not intended for romantic or dating purposes.

3.) Attempting to use Cupid Bot for dating or any activity that violates Discord's Terms of Service, including inappropriate conduct, may result in action being taken by discord, including potential bans. By using Cupid Bot, you agree to respect these guidelines and the community standards.

4.) Cupid bot will not enforce these guidelines and wont go after anyone, by agreeing you understand and agree to the risk involved.
"""

TOS = Embed(title="Terms Of Service", description=tos_description, color=0xff0000)


class Matching(Cog):
    def __init__(self):
        super().__init__()

    matching = Group(name="matching", description="A group of commands for match making")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    @profile.command(name='create', description='a command to create a profile')
    async def matching_profile_create(self, interaction:Interaction):
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message(embed=TOS, view=TosConfirmationView(interaction.user))
        if profile_data.get('approved') == False or profile_data.get('approved'):
            return await interaction.response.send_message("Your profile is already submitted and/or created~! use `/matching profile edit` to edit it!", ephemeral=True)
        

        profile_embed = generate_profile_embed(interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(), ephemeral=True)
    

    @profile.command(name='edit', description='a command to edit a profile')
    async def matching_profile_create(self, interaction:Interaction):
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message("You haven't created a profile! use `/matching profile create`")
        
        profile_embed = generate_profile_embed(interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(True), ephemeral=True)

        
