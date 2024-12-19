from discord import Embed, Member, Interaction
from discord.ext.commands import Cog, command
from discord.app_commands import Group, describe
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
    async def profile_create(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message(embed=TOS, view=TosConfirmationView(interaction.user), ephemeral=True)
        if profile_data.get('approved') == False or profile_data.get('approved'):
            return await interaction.response.send_message("Your profile is already submitted and/or created~! use `/matching profile edit` to edit it!", ephemeral=True)
        

        profile_embed = generate_profile_embed(interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(), ephemeral=True)
    

    @profile.command(name='edit', description='a command to edit a profile')
    async def profile_edit(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message("You haven't created a profile! use `/matching profile create`")
        
        profile_embed = generate_profile_embed(interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(True), ephemeral=True)



    @profile.command(name="view", description="view the profile of yourself or another user")
    @describe(
        member = "The member of the profile you want to see"
    )
    async def matching_profile_view(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        member = member if member else interaction.user
        await interaction.response.defer()
        profile_embed = generate_profile_embed(member)
        await interaction.followup.send(embed=profile_embed)



    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
    


    @profile.command(name="status",description="See your approval status for your profile")
    @describe(
        member = "The member of the profile's status you want to see"
    )
    async def profile_status(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        member = member if member else interaction.user



        



    @matching.command(name="compatible", description="see all the compatiable profiles")
    async def compatible(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        



    @matching.command(name="unmatch", description="unmatch yourself from your pair")
    async def unmatch(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        



    @matching.command(name="match", description="match with people and find a pair!")
    async def match(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        

    

    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        
    


    @profile.command(name="status",description="See the status of your profile")
    async def profile_status(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)       
        
        
