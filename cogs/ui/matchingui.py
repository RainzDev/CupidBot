from discord.ui import Select, View, Modal, TextInput, button, DynamicItem
from discord import Button, ButtonStyle, Interaction, TextStyle, Embed, SelectOption
from database.database import matching, generate_profile_description, find_compatible_profiles


class SwipeView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label='Swipe Left', emoji="⬅️")
    async def swipe_left(self, interaction:Interaction, button:Button):
        await interaction.response.send_message('test')
    
    @button(label='Swipe Right', emoji="➡️")
    async def swipe_right(self, interaction:Interaction, button:Button):
        await interaction.response.send_message('test')