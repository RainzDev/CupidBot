#Custom role mennus
from discord import SelectOption
from discord.utils import get
from discord.ui import View, Select
from database.database import infractions

class RoleColorSelect(Select):
    def __init__(self):
        options = [
            SelectOption(label="White", emoji="<:White:1307861241536057385>"),
            SelectOption(label="Pink", emoji="<:Pink:1307861237719240868>"),
            SelectOption(label="Red", emoji="<:Red:1307861240684478614>"),
            SelectOption(label="Orange", emoji="<:Orange:1307861236431589468>"),
            SelectOption(label="Yellow", emoji="<:Yellow:1307861278336749588>"),
            SelectOption(label="Green", emoji="<:Green:1307861235177492501>"),
            SelectOption(label="Blue", emoji="<:Blue:1307861233873195148>"),
            SelectOption(label="Purple", emoji="<:Purple:1307861239413604383>"),
            SelectOption(label="Black", emoji="<:Black:1307861232887267358>"),
        ]
        
        super().__init__(custom_id="role_select", placeholder="Select a color role", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction):
        await interaction.response.defer()
        
        selected_role = get(interaction.guild.roles, name=self.values[0])
        color_roles = [
            get(interaction.guild.roles, name=option.label)
            for option in self.options
            if get(interaction.guild.roles, name=option.label)
        ]
        
    
        new_roles = set(interaction.user.roles) - set(color_roles) | {selected_role}
        await interaction.user.edit(roles=new_roles)
        await interaction.followup.send("Role updated successfully!", ephemeral=True)



class RoleView(View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(RoleColorSelect())
    


