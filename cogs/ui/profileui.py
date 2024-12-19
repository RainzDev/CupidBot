from discord.ui import View, Button, button, Modal, TextInput, Select
from discord import ButtonStyle, Member, Interaction, TextStyle, Embed, SelectOption
from database.matchingdb import edit_profile, generate_profile_embed, get_profile, queue_profile
from cogs.ui.submissionui import SubmissionView


class TosConfirmationView(View):
    def __init__(self, user:Member):
        self.user = user
        self.responded = False
        super().__init__(timeout=180)

    
    @button(label="Confirm",custom_id="confirm_tos_button", style = ButtonStyle.green)
    async def tos_confirm(self, interaction:Interaction, button:Button):
        if self.responded:
            return await interaction.response.send_message("You already responded to this!")
        if interaction.user != self.user:
            return await interaction.response.send_message("Only the original user can respond to this tos agreement!", ephemeral=True)
            
        
        self.responded = True
        edit_profile(interaction.user, {"$set": {"tos_agreed":True}}, True)
        await interaction.response.send_message("Done! Feel free to re-run the command")


# TODO
## 1.)  move to 1 select menu with custom name and stuff, just take in options as kwarg
class ProfileGenderSelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="Male"),
            SelectOption(label="Female"),
            SelectOption(label="Other", description="Please specify in bio"),
        ]
        super().__init__(custom_id="profile_gender", placeholder="Select Your Gender", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        edit_profile(interaction.user, {"$set":{"gender":self.values[0]}})
        profile_embed = generate_profile_embed(user=interaction.user)
        await interaction.response.edit_message(embed=profile_embed)


class ProfileAgeSelect(Select):
    def __init__(self):
        options = [SelectOption(label=f"{age}") for age in range(13,24)]
        options.append(SelectOption(label="25+"))
        super().__init__(custom_id="profile_age", placeholder="Select Your Age", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        edit_profile(interaction.user, {"$set":{"age":self.values[0]}})
        profile_embed = generate_profile_embed(user=interaction.user)
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
        edit_profile(interaction.user, {"$set":{"sexuality":self.values[0]}})
        profile_embed = generate_profile_embed(user=interaction.user)
        await interaction.response.edit_message(embed=profile_embed)



class ProfileEditModal(Modal):
    def __init__(self, user:Member):
        super().__init__(title="Edit Profile", timeout=None, custom_id="edit_profile_modal")
        profile_data:dict = get_profile(user)
        if profile_data:
            self.name.default = profile_data.get('name')
            self.pronouns.default = profile_data.get('pronouns')
            self.bio.default = profile_data.get('bio')
        

    
    name = TextInput(label="Name", style=TextStyle.short)
    pronouns = TextInput(label="Pronouns", style=TextStyle.short)
    bio = TextInput(label="Bio", style=TextStyle.paragraph)

    async def on_submit(self, interaction:Interaction):
        edit_profile(interaction.user, {"$set":{"name":self.name.value,"pronouns":self.pronouns.value,"bio":self.bio.value}})

        profile_embed = generate_profile_embed(user=interaction.user)

        await interaction.response.edit_message(embed=profile_embed)



class ProfileCreationView(View):
    def __init__(self, editing=False):
        super().__init__(timeout=None)
        self.add_item(ProfileSexualitySelect())
        self.add_item(ProfileAgeSelect())
        self.add_item(ProfileGenderSelect())
        self.edit = editing
        if editing:
            self.children[1].label = "Resubmit"
    
    @button(label="Edit Profile", style=ButtonStyle.gray)
    async def edit_profile(self, interaction:Interaction, button:Button):
        await interaction.response.send_modal(ProfileEditModal(interaction.user))

    
    @button(label="Submit Profile", style=ButtonStyle.green)
    async def submit_profile(self, interaction:Interaction, button:Button):
        # send profile to home server, and wait for verifcation
        profile_embed = generate_profile_embed(user=interaction.user, color=0xfffacd)
        profile_data = get_profile(interaction.user)
        status = profile_data.get('approved')
        if status == "Waiting" or status == False and not self.edit:
            return await interaction.response.send_message('Your profile was already submitted!', ephemeral=True)
        verifcation_channel = interaction.guild.get_channel(1307474634559459360)
        msg = await verifcation_channel.send("Waiting..")
        await msg.edit(content="", embed=profile_embed, view=SubmissionView())
        queue_profile(interaction.user, msg)
        await interaction.response.send_message("Submitted!", ephemeral=True)

