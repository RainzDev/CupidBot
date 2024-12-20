from discord.ui import Select, View, Modal, TextInput, button, DynamicItem
from discord import Button, ButtonStyle, Interaction, TextStyle, Embed, SelectOption, User
from database.matchingdb import edit_profile, fetch_random_user, generate_profile_embed, get_compatible


class SwipeView(View):
    def __init__(self, user:User, bot):
        super().__init__(timeout=None)
        self.user = user
        self.bot = bot
    
    @button(label='Swipe Left', emoji="⬅️")
    async def swipe_left(self, interaction:Interaction, button:Button):
        edit_profile(interaction.user, {'$push': {'rejected_pairs': self.user.id}}) # reject, queue up a new profile

        profiles = get_compatible(interaction.user)
        user = fetch_random_user(self.bot, profiles) # gets a user we can see
        random_profile_embed = generate_profile_embed(user=user)
        await interaction.response.edit_message(embed=random_profile_embed, view=SwipeView(user, self.bot))
        
    
    @button(label='Swipe Right', emoji="➡️")
    async def swipe_right(self, interaction:Interaction, button:Button):
        edit_profile(interaction.user, {'$push': {'selected_pairs': self.user.id}}) # reject, queue up a new profile
        edit_profile(self.user, {"$push": {'paired_with_us':interaction.user.id}})

        # TODO
            # CHECK MATCH Condition

        profiles = get_compatible(interaction.user)
        user = fetch_random_user(self.bot, profiles) # gets a user we can see
        random_profile_embed = generate_profile_embed(user=user)
        await interaction.response.edit_message(embed=random_profile_embed, view=SwipeView(user, self.bot))