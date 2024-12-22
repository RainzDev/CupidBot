from discord.ui import Select, View, Modal, TextInput, button, DynamicItem
from discord import Button, ButtonStyle, Interaction, TextStyle, Embed, SelectOption, User
from discord.ext.commands import Bot
from database.matchingdb import edit_profile, generate_profile_embed, get_compatible, get_profile
import random
from asyncio import sleep


class SwipeView(View):
    def __init__(self, user:User, bot):
        super().__init__(timeout=None)
        self.user = user
        self.bot:Bot = bot
    
    @button(label='Swipe Left', emoji="⬅️")
    async def swipe_left(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        edit_profile(interaction.user, {'$push': {'rejected_pairs': self.user.id}}) # reject, queue up a new profile

        profiles = get_compatible(interaction.user)
        if len(profiles) == 0: return await interaction.followup.send("You are out of profiles to match with!", ephemeral=True)
        random_profile:dict = profiles[random.randint(0, len(profiles)-1)]
        user = self.bot.get_user(random_profile.get('user_id'))
        if not user:
            return await interaction.followup.send("the user i tried to pull has left the scope of the bot! rerun `/matching match`", ephemeral=True)
        
        random_profile_embed = generate_profile_embed(user=user)


        await interaction.edit_original_response(embed=random_profile_embed, view=SwipeView(user, self.bot))
        
    
    @button(label='Swipe Right', emoji="➡️")
    async def swipe_right(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        edit_profile(interaction.user, {'$push': {'selected_pairs': self.user.id}}) # reject, queue up a new profile
        edit_profile(self.user, {"$push": {'paired_with_us':interaction.user.id}})

        
        their_data = get_profile(self.user)
        
        if interaction.user.id in their_data.get('selected_pairs', []):
            await interaction.followup.send(f"Congrats! you and {self.user.mention} matched! Feel free to dm each other or smth... idfk", ephemeral=True)
            try:
                await self.user.send(f"You matched with {interaction.user.mention}! Feel free to dm each other")
            except: await interaction.followup.send("I couldnt dm them! you'll have to find a way to reach them!", ephemeral=True)
            await sleep(3)


        profiles = get_compatible(interaction.user)
        if len(profiles) == 0: return await interaction.followup.send("You are out of profiles to match with!", ephemeral=True)
        random_profile:dict = profiles[random.randint(0, len(profiles)-1)]
        user = self.bot.get_user(random_profile.get('user_id'))
        if not user:
            return await interaction.followup.send("the user i tried to pull has left the scope of the bot! rerun `/matching match`", ephemeral=True)


        random_profile_embed = generate_profile_embed(user=user)
        await interaction.edit_original_response(embed=random_profile_embed, view=SwipeView(user, self.bot))