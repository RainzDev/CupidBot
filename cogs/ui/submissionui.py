from discord import ButtonStyle, Interaction, TextStyle
from discord.ui import View, Button, button, Modal, TextInput
from database.matchingdb import qet_queued, edit_profile, generate_profile_embed


 


class SubmissionView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    

    @button(label="Approve", style=ButtonStyle.green)
    async def approve(self, interaction:Interaction, button:Button):
        profile = qet_queued(interaction.message.id)
        if not profile:
            await interaction.delete_original_response()
            await interaction.response.send_message("Looks like the profile is no longer in queue!")
            return
        user_id = profile.get('user_id')
        user = interaction.guild.get_member(user_id)
        edit_profile(user, {"$set": {"approved":True}, "$unset": {"message_id":"","date":""}})
        profile_embed = generate_profile_embed(user, color=0xb2f2bb)
        profile_embed.add_field(name="Approved", value=f"Approved by: {interaction.user.mention}")
        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(embed=profile_embed, view=self)
        try:
            await user.send("Your profile was approved! use `/matching match` to start matching with people")
        except: await interaction.followup.send(f"I cant Dm {user.mention}")




        


    @button(label="Deny", style=ButtonStyle.red)
    async def deny(self, interaction:Interaction, button:Button):
        profile = qet_queued(interaction.message.id)
        if not profile:
            await interaction.delete_original_response()
            await interaction.response.send_message("Looks like the profile is no longer in queue!", ephemeral=True)
            return
        user_id = profile.get('user_id')
        user = interaction.guild.get_member(user_id)
        edit_profile(user, {"$set": {"approved":False}, "$unset": {"message_id":"","date":""}})
        profile_embed = generate_profile_embed(user, color=0xff8d8d)
        profile_embed.add_field(name="Denied", value=f"Denied by: {interaction.user.mention}")
        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(embed=profile_embed, view=self)
        try:
            await user.send("Your profile was denied! this is usually because ur bio sucks and you should add more detail to it :)\n\nRun `/matching profile edit` to edit & resubmit your profiile`")
        except: await interaction.followup.send(f"I cant Dm {user.mention}")
    

