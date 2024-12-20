from database.matchingdb import generate_profile_embed, NoProfileException, get_profile, get_compatible, fetch_random_user
from discord.app_commands import Group, describe, default_permissions
from discord import Embed, Member, Interaction
from discord.ext.commands import Cog, command, Bot
from cogs.ui.profileui import TosConfirmationView, ProfileCreationView
from cogs.ui.matchingui import SwipeView

import random




tos_description = """
1.) Cupid Bot is designed to help users connect and make new friends in a fun and safe environment.

2.) The bot is strictly for friendship-based matchmaking and is not intended for romantic or dating purposes.

3.) Attempting to use Cupid Bot for dating or any activity that violates Discord's Terms of Service, including inappropriate conduct, may result in action being taken by discord, including potential bans. By using Cupid Bot, you agree to respect these guidelines and the community standards.

4.) Cupid bot will not enforce these guidelines and wont go after anyone, by agreeing you understand and agree to the risk involved.
"""

TOS = Embed(title="Terms Of Service", description=tos_description, color=0xff0000)


class Matching(Cog):
    def __init__(self, bot:Bot):
        super().__init__()
        self.bot:Bot = bot

    matching = Group(name="matching", description="A group of commands for match making")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    @profile.command(name='create', description='a command to create a profile')
    async def profile_create(self, interaction:Interaction):
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message(embed=TOS, view=TosConfirmationView(interaction.user), ephemeral=True)
        if profile_data.get('approved') == False or profile_data.get('approved'):
            return await interaction.response.send_message("Your profile is already submitted and/or created~! use `/matching profile edit` to edit it!", ephemeral=True)
        

        profile_embed = generate_profile_embed(user=interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(self.bot), ephemeral=True)
    

    @profile.command(name='edit', description='a command to edit a profile')
    async def profile_edit(self, interaction:Interaction):
        profile_data = get_profile(interaction.user)
        if not profile_data or not profile_data.get('tos_agreed'):
            return await interaction.response.send_message("You haven't created a profile! use `/matching profile create`")
        
        profile_embed = generate_profile_embed(user=interaction.user)

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(self.bot, True), ephemeral=True)



    @profile.command(name="view", description="view the profile of yourself or another user")
    @describe(
        member = "The member of the profile you want to see"
    )
    async def matching_profile_view(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        await interaction.response.defer()
        profile_embed = generate_profile_embed(user=member)
        await interaction.followup.send(embed=profile_embed)



    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
    


    @profile.command(name="status",description="See your approval status for your profile")
    @describe(
        member = "The member of the profile's status you want to see"
    )
    async def profile_status(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        profile_data = get_profile(member)
        status = profile_data.get('approved')

        match status:
            case True:
                await interaction.response.send_message("Your profile is already approved! feel free to use `/matching match`",ephemeral=True)
            case False:
                await interaction.response.send_message("Your profile is not approved! please edit and resubmit your profile via `/matching profile edit`", ephemeral=True)
            case 'waiting':
                await interaction.response.send_message("Staff hasnt gotten to approving your profile yet! please be paitent!", ephemeral=True)
            case _:
                await interaction.response.send_message("Your profile hasnt been submitted! use `/matching profile create` to submit it!`", ephemeral=True)



    @matching.command(name="compatible", description="see all the compatiable profiles")
    async def compatible(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        member = member if member else interaction.user
        profiles = get_compatible(member)
        await interaction.response.send_message(f'you have `{len(profiles)}` compatible profiles!')
    


    @matching.command(name="compatible_view", description="see all the compatiable profiles")
    @default_permissions()
    async def compatible(self, interaction:Interaction, member:Member=None):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('this command is reserved for the owner only. it will be hidden soon~ish', ephemeral=True)

        member = member if member else interaction.user
        profiles = get_compatible(member)
        profile_string = "\n".join(f"{profile.get('name')} | `{profile.get('age')}`" for profile in profiles)
        profiles_embed = Embed(title="All compatible profiles", description=profile_string, color=0xffa1dc)

        await interaction.response.send_message(embed=profiles_embed)



    @matching.command(name="match", description="match with people and find a pair!")
    async def match(self, interaction:Interaction):
        if interaction.user.id != 1267552151454875751: await interaction.response.send_message('command still under construction! check back later', ephemeral=True)
        profile_data = get_profile(interaction.user)
        if profile_data.get('approved') != True: return await interaction.response.send_message("You cant match until you are approved, see `/matching profile status`", ephemeral=True)

        # get a random profile
        profiles = get_compatible(interaction.user)
        
        user = fetch_random_user(self.bot, profiles) # gets a user we can see
        random_profile_embed = generate_profile_embed(user=user)
        await interaction.response.send_message(embed=random_profile_embed, view=SwipeView(user, self.bot), ephemeral=True)
    