from discord import Embed, Member, Interaction
from discord.ext.commands import Cog, command
from discord.app_commands import Group, describe
from database.matchingdb import generate_profile_embed, NoProfileException, get_profile
from cogs.ui.profileui import TosConfirmationView, ProfileCreationView

## BELOW IMPORTS FOR COMPATABILITY 
from database.database import generate_profile_description, find_compatible_profiles
from database.databasev2 import MATCHING
from cogs.ui.matchingui import MatchingView
import random


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

    @profile.command(name="view", description="view the profile of yourself or another user")
    @describe(
        member = "The member of the profile you want to see"
    )
    async def matching_profile_view(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        await interaction.response.defer()
        profile_embed = generate_profile_embed(member)
        await interaction.followup.send(embed=profile_embed)




    # ^^^^^ ALL NEW DELETE EVERYTHING BELOW



    
    @matching.command(name="compatible", description="see all the compatiable profiles")
    async def compatible(self, interaction:Interaction, member:Member=None):
        member = member if member else interaction.user
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer()
        state, data = find_compatible_profiles(member.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data)
        profiles = data

        await interaction.followup.send(f"You have `{len(profiles)}` compatible profiles to match with")

    @matching.command(name="unmatch", description="unmatch yourself from your pair")
    async def unmatch(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer(ephemeral=True)

        data:dict = MATCHING.find_one({"user_id":interaction.user.id})

        if not data.get('paired'):
            return await interaction.followup.send("You arent even paired! cant unpair", ephemeral=True)
        
        partner_id = data.get('partner_id', 0)

        partner = interaction.guild.get_member(partner_id) # we should check if they are in the server


        MATCHING.update_many({
            "user_id": {
                "$in": [interaction.user.id, partner_id]
            }
        },{
            "$unset": {
                "paired":"",
                "partner_id":""
            }
        })

        pair_role = interaction.guild.get_role(1306300320443269190)
        unpair_role = interaction.guild.get_role(1306300431303184434)


        await interaction.user.edit(roles=[role for role in interaction.user.roles if role.id != pair_role.id] + [unpair_role])
        await partner.edit(roles=[role for role in partner.roles if role.id != pair_role.id] + [unpair_role])


        await interaction.followup.send(f"You have successfully unpaired from {partner.mention}")
        

        



    @matching.command(name="match", description="match with people and find a pair!")
    async def match(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer(ephemeral=True)
        
        our_data:dict = MATCHING.find_one({'user_id':interaction.user.id})
        if not our_data:
            return await interaction.followup.send("You have no data! use `/matching profile create`")

        if our_data.get('paired'): 
            return await interaction.followup.send("You are already paired, you cant pair again! use `/matching unmatch` to unmatch from your partner!")

        #get our data to compare against
        state, data = find_compatible_profiles(interaction.user.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data)
        profiles = data
         

        # get data from the database to pick randomly from
        
        profile:dict = profiles[random.randint(0,len(profiles)-1)]
        user_id = int(profile.get('user_id'))
        member = interaction.guild.get_member(user_id)
        description, resp_id = generate_profile_description(user_id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.followup.send(embed=profile_embed, view=MatchingView(user_id), ephemeral=True)

    
    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):       

        MATCHING.delete_one({"user_id":interaction.user.id})

        await interaction.response.send_message("Your profile has been deleted! Whoops sorry for no confirm deletion button", ephemeral=True)
    

    @profile.command(name="status",description="See the status of your profile")
    async def profile_status(self, interaction:Interaction):       
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        data:dict = MATCHING.find_one({'user_id':interaction.user.id})
        if not data: return await interaction.response.send_message("You havent even submitted a profile")
        status = data.get('approved')
        if not status: return await interaction.response.send_message("Your profile isnt submitted, use `/matching profile create` to submit it")
        await interaction.response.send_message(f"Your approval status: `{status}`\n\nFalse means it hasnt been approved yet, if its been more then 3 hours @ping the mods to see if it was submitted properly, if not resubmit it\nTrue means it was submitted :thumbsup:")
        
