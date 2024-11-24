# Matchmaking features for the bot
from discord import Embed, Member, Message, Interaction
from discord.app_commands import command, Group, guild_only
from discord.ext.commands import Cog
from database import matching, generate_profile_description
from matchingui import ProfileCreationView

import random




class Matching(Cog):
    def __init__(self) -> None:
        super().__init__()

    
    matching = Group(name="matching", description="group of matching commands")
    profile = Group(name="profile", description="a subgroup of profile based commands", parent=matching)

    
    @matching.command(name="compatible", description="see all the compatiable profiles")
    async def compatible(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer()
        data:dict = matching.find_one({'user_id':interaction.user.id})
        if not data: return await interaction.followup.send("You have no profile! Create one using `/matching profile create`")
        if not data.get('approved'): return await interaction.followup.send("You havent been approved! please wait for it to be approved/denied")


        age =  int(data.get('age'))
        user_ids = [member.id for member in interaction.guild.members]
        profiles = [profile for profile in matching.find({'approved':True}) if profile.get('user_id') in user_ids and not int(profile.get('age')) > age+2 and not int(profile.get('age')) < age-2 and not int(profile.get('user_id')) == interaction.user.id]

        await interaction.followup.send(f"You have `{len(profiles)}` compatible profiles to match with")


    @matching.command()
    async def match(self, interaction:Interaction):
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        await interaction.response.defer()
        #get our data to compare against
        data:dict = matching.find_one({'user_id':interaction.user.id})
        if not data: return await interaction.followup.send("You have no profile! Create one using `/matching profile create`")
        if not data.get('approved'): return await interaction.followup.send("You havent been approved! please wait for it to be approved/denied")

        age =  int(data.get('age'))

        user_ids = [member.id for member in interaction.guild.members]

        profiles = [profile for profile in matching.find({'approved':True}) if profile.get('user_id') in user_ids and not int(profile.get('age')) > age+2 and not int(profile.get('age')) < age-2 and not int(profile.get('user_id')) == interaction.user.id]

        if not profiles:
            return await interaction.followup.send("their is no one for you to match with, sorry!")
        
         


        # get data from the database to pick randomly from
        
        profile:dict = profiles[random.randint(0,len(profiles)-1)]
        user_id = int(profile.get('user_id'))
        member = interaction.guild.get_member(user_id)
        description, resp_id = generate_profile_description(user_id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.followup.send(embed=profile_embed)


    


    @profile.command(name="create")
    async def profile_create(self, interaction:Interaction):    
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")   

        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.send_message(embed=profile_embed, view=ProfileCreationView(), ephemeral=True)
    
    @profile.command(name="delete")
    async def profile_delete(self, interaction:Interaction):       

        matching.delete_one({"user_id":interaction.user.id})

        await interaction.response.send_message("Your profile has been deleted! Whoops sorry for no confirm deletion button", ephemeral=True)
    

    @profile.command(name="status",description="See the status of your profile")
    async def profile_status(self, interaction:Interaction):       
        if not interaction.guild: return await interaction.response.send_message("you have to use this in a guild!")
        data:dict = matching.find_one({'user_id':interaction.user.id})
        if not data: return await interaction.response.send_message("You havent even submitted a profile")
        status = data.get('approved')
        if not status: return await interaction.response.send_message("Your profile isnt submitted, use `/matching profile create` to submit it")
        await interaction.response.send_message(f"Your approval status: `{status}`\n\nFalse means it hasnt been approved yet, if its been more then 3 hours @ping the mods to see if it was submitted properly, if not resubmit it\nTrue means it was submitted :thumbsup:")
        


