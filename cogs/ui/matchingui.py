from discord.ui import Select, View, Modal, TextInput, button, DynamicItem
from discord import Button, ButtonStyle, Interaction, TextStyle, Embed, SelectOption
from database.database import matching, generate_profile_description, find_compatible_profiles

import time
import random


class ProfileReasonModal(Modal):
    def __init__(self, status:str, uid:int):
        self.uid = uid
        self.status = status
        super().__init__(title="Reason", timeout=None, custom_id="profile_reason_modal")
        

    
    reason = TextInput(label="Reason/Notes", style=TextStyle.long)

    async def on_submit(self, interaction:Interaction):
        await interaction.response.send_message("Done", ephemeral=True)
        user = interaction.guild.get_member(self.uid)
        try:
            await user.send(f"Your profile was `{self.status}` for: `{self.reason.value}`")
        except:
            await interaction.followup.send("I can't dm the user!")
        

class ProfileApprovalView(View):
    def __init__(self, user_id:int):
        self.user_id = user_id
        super().__init__(timeout=None)
        
    
    @button(label="Approve Profile", style=ButtonStyle.green)
    async def approve_profile(self, interaction:Interaction, button:Button):
        matching.update_one({'user_id':self.user_id}, {"$set":{"approved":True}})
        data:dict = matching.find_one({'user_id':self.user_id})
        await interaction.response.send_modal(ProfileReasonModal("Approved", self.user_id))
        male_chan = interaction.guild.get_channel(1307474580008599663)
        female_chan = interaction.guild.get_channel(1307474598060883968)
        other_chan = interaction.guild.get_channel(1307480874119462952)
        match data.get('gender'):
            case "Male":
                chan = male_chan
            case "Female":
                chan = female_chan
            case "Other":
                chan = other_chan
            case _:
                chan = other_chan
        
        description, resp_id = generate_profile_description(self.user_id)
        user = interaction.guild.get_member(self.user_id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=user.name, icon_url=user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await chan.send(embed=profile_embed)


        await interaction.delete_original_response()
    
    @button(label="Deny Profile", style=ButtonStyle.red)
    async def deny_profile(self, interaction:Interaction, button:Button):
        matching.update_one({'user_id':self.user_id}, {"$set":{"approved":False}})
        await interaction.response.send_modal(ProfileReasonModal("Denied", self.user_id))
        await interaction.delete_original_response()
        
        
# -------------------------------------------------- Approval / Mod stuff ^^^


class ProfileGenderSelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="Male"),
            SelectOption(label="Female"),
            SelectOption(label="Other", description="Please specify in bio"),
        ]
        super().__init__(custom_id="profile_gender", placeholder="Select Your Gender", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        matching.update_one({'user_id':interaction.user.id}, {"$set":{"gender":self.values[0]}}, upsert=True)
        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.edit_message(embed=profile_embed)


class ProfileAgeSelect(Select):
    def __init__(self):
        options = [SelectOption(label=f"{age}") for age in range(13,24)]
        options.append(SelectOption(label="25+"))
        super().__init__(custom_id="profile_age", placeholder="Select Your Age", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        matching.update_one({'user_id':interaction.user.id}, {"$set":{"age":self.values[0]}}, upsert=True)
        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.edit_message(embed=profile_embed)


class ProfileSexualitySelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="Heterosexual"),
            SelectOption(label="Homosexual"),
            SelectOption(label="Bisexual"),
            SelectOption(label="Other"),
        ]
        super().__init__(custom_id="profile_sexuality", placeholder="Select Your Sexuality", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        matching.update_one({'user_id':interaction.user.id}, {"$set":{"sexuality":self.values[0]}}, upsert=True)
        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.edit_message(embed=profile_embed)


class ProfileEditModal(Modal):
    def __init__(self, data:dict):
        super().__init__(title="Edit Profile", timeout=None, custom_id="edit_profile_modal")
        if data:
            self.name.default = data.get('name')
            self.pronouns.default = data.get('pronouns')
            self.bio.default = data.get('bio')

    
    name = TextInput(label="Name", style=TextStyle.short)
    pronouns = TextInput(label="Pronouns", style=TextStyle.short)
    bio = TextInput(label="Bio", style=TextStyle.paragraph)

    async def on_submit(self, interaction:Interaction):
        matching.update_one({'user_id':interaction.user.id}, {"$set":{"name":self.name.value,"pronouns":self.pronouns.value,"bio":self.bio.value}}, upsert=True)

        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.response.edit_message(embed=profile_embed)


class ProfileCreationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProfileSexualitySelect())
        self.add_item(ProfileAgeSelect())
        self.add_item(ProfileGenderSelect())
    
    @button(label="Edit Profile", style=ButtonStyle.gray)
    async def edit_profile(self, interaction:Interaction, button:Button):
        data = matching.find_one({'user_id':interaction.user.id})
        await interaction.response.send_modal(ProfileEditModal(data))
    
    @button(label="Submit Profile", style=ButtonStyle.green)
    async def submit_profile(self, interaction:Interaction, button:Button):
        data:dict = matching.find_one({'user_id':interaction.user.id})
        if not data:
            return await interaction.response.send_message("You have litterally filled out 0 fucking items, try again")
        
        name = data.get('name', None) if data else None
        age = data.get('age', None) if data else None
        gender = data.get('gender', None) if data else None
        pronouns = data.get('pronouns', None) if data else None
        sexuality = data.get('sexuality', None) if data else None 
        bio = data.get('bio', None) if data else None
        values = [name,age,gender,pronouns,sexuality,bio]
        if None in values:
            return await interaction.response.send_message("One or more values is set to `None`!", ephemeral=True)
        
        chan = interaction.guild.get_channel(1307474634559459360) # hard coded should be in config

        description, resp_id = generate_profile_description(interaction.user.id)
        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await chan.send(content="A new profile has been submitted and needs to be approved!", embed=profile_embed, view=ProfileApprovalView(interaction.user.id))
        await interaction.response.send_message("Your Profile has been submitted to be reviewed!", ephemeral=True)
        


# ---------------------------------------------------------------- ^^ profile stuff

class MatchingView(View):
    def __init__(self,user_id):
        self.user_id = user_id
        super().__init__(timeout=None)

    
    ### TODO
    # remove our user_id from paired_with_us for all of our selected pairs
    # delete the selected pairs from us and the user we matched with
    # add polish later
    @button(label="Match", custom_id="matching_match",style=ButtonStyle.green)
    async def match(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        matching.update_one({"user_id":interaction.user.id}, {"$push":{"selected_pairs":{"$each": [self.user_id]}}}) # the people WE __want__ to match with
        matching.update_one({"user_id":self.user_id}, {"$push":{"paired_with_us":{"$each": [interaction.user.id]}}}) # the person we want to match with, and all the other ppl who wanted to match with em
        data:dict = matching.find_one({"user_id":self.user_id})

        if interaction.user.id in data.get('selected_pairs', []): # match condition
            # delete all selected and what not, give them the paired role, send rules and conditions in dms
            pair_role = interaction.guild.get_role(1306300320443269190)
            unpair_role = interaction.guild.get_role(1306300431303184434)

            

            member_a = interaction.guild.get_member(interaction.user.id)
            member_b = interaction.guild.get_member(self.user_id)
            
            data_a:dict = matching.find_one({'user_id':member_a.id})
            data_b:dict = matching.find_one({'user_id':member_b.id})

            selected_a = data_a.get('selected_pairs', []) # Ids of people who member_a matched with
            selected_b = data_b.get('selected_pairs', []) # Ids of people who member_b matched with

            
            matching.update_many({
                "user_id":{
                    "$in": selected_b
                }
            },
            {
                "$pull": {"paired_with_us":member_a.id} # remove member_a id from all the users member_a paired with
            }) 
        
        
            matching.update_many({
                "user_id":{
                    "$in": selected_a
                }
            },
            {
                "$pull": {"paired_with_us":member_b.id} # remove member_b id from all the users member_b paired with
            }) 
        
            # delete selected pairs and paired with us list from both paired members. 
            matching.update_many({"user_id": {"$in":[member_a.id,member_b.id]}}, {
                "$unset": {
                    "selected_pairs": "",
                    "paired_with_us": "",
                    "rejected_pairs": ""
                }
            })
            

            

            await member_a.edit(roles=[role for role in member_a.roles if role.id != unpair_role.id] + [pair_role])
            await member_b.edit(roles=[role for role in member_b.roles if role.id != unpair_role.id] + [pair_role])

            pairs_channel = interaction.guild.get_channel(1308436302999322704)

            matching.update_one({'user_id':member_a.id}, {"$set":{"paired":True, "partner_id":member_b.id, "match_date":int(time.time())}})
            matching.update_one({'user_id':member_b.id}, {"$set":{"paired":True, "partner_id":member_a.id, "match_date":int(time.time())}})

            try:
                await member_a.send(f"you and {member_b.mention} have been matched and paired! this is usually a trial period of 1 week, to get unpaired create an unpair ticket in the server, feel free to dm each other and get to know each other")
            except: pass

            try:
                await member_b.send(f"you and {member_a.mention} have been matched and paired! this is usually a trial period of 1 week, to get unpaired create an unpair ticket in the server, feel free to dm each other and get to know each other")
            except: pass

            await interaction.followup.send("congratulations! you guys matched! you are now paired! read dms!", ephemeral=True)
            await pairs_channel.send(f"✨❤ {member_a.mention} + {member_b.mention} ❤✨")
            return


        # reroll cus not matched
        state, data = find_compatible_profiles(interaction.user.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data, ephemeral=True)
        profiles = data
         
        # get data from the database to pick randomly from
        
        profile:dict = profiles[random.randint(0,len(profiles)-1)]
        user_id = int(profile.get('user_id'))
        member = interaction.guild.get_member(user_id)
        description, resp_id = generate_profile_description(user_id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.delete_original_response()

        await interaction.followup.send(embed=profile_embed, view=MatchingView(user_id), ephemeral=True)

            

        

    @button(label="Reject", custom_id="matching_reject", style=ButtonStyle.red)
    async def reject(self, interaction: Interaction, button: Button):
        matching.update_one(
            {"user_id": interaction.user.id},  # Filter
            {
                "$push": {"rejected_pairs": {"$each": [self.user_id]}},  # Ensure it's treated as a list
            },
            upsert=True  # Create document if it doesn't exist
    )
        
        await interaction.response.defer()
        #get our data to compare against
        state, data = find_compatible_profiles(interaction.user.id, interaction.guild.members)
        if not state:
            return await interaction.followup.send(data, ephemeral=True)
        profiles = data
         


        # get data from the database to pick randomly from
        
        profile:dict = profiles[random.randint(0,len(profiles)-1)]
        user_id = int(profile.get('user_id'))
        member = interaction.guild.get_member(user_id)
        description, resp_id = generate_profile_description(user_id)

        profile_embed = Embed(title="Profile", description=description, color=0xffa1dc)
        profile_embed.set_author(name=member.name, icon_url=member.avatar.url)
        profile_embed.set_footer(text=f"Profile Id: {resp_id}")

        await interaction.delete_original_response()

        await interaction.followup.send(embed=profile_embed, view=MatchingView(user_id), ephemeral=True)
