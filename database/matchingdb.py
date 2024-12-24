from discord import Embed, Member, Message, User
from discord.ext.commands import Bot
from database.databasev2 import MATCHING, NoProfileException
from time import time

from typing import List

# puts the profile in a queue to be verifed

class UserNotFoundException(BaseException):
    def __init__(self, message="The discord user is out of scope of the bot"):
        self.message = message
        super().__init__(self.message)

class Profile():
    def __init__(self, bot:Bot, data:dict):
        self.bot = bot
        if data == None:
            raise NoProfileException()
        self.id = data.get('user_id')
        self.user = bot.get_user(self.id)
        if not self.user: raise UserNotFoundException()
        self.name:str = data.get('name')
        self.pronouns:str = data.get('pronouns')
        self.gender:str = data.get('gender')
        self.age:int = data.get('age')
        self.sexuality:str = data.get('sexuality')
        self.bio:str = data.get('bio')
        self._id = data.get('_id')
        self.approved:bool = data.get('approved')
        self.selected_pairs = data.get('selected_pairs', [])
        self.rejected_pairs = data.get('rejected_pairs', [])
        self.paired_with_us = data.get('paired_with_us', [])
        self.tos = data.get('tos_agreed')
        self.data:dict = data
    
    def __call__(self):
        profiles = []

        for profile in get_compatible(self.user):
            try:
                get_profile(profile.get('user_id'), self.bot)
                profiles.append(profile)
            except UserNotFoundException:
                continue
        return profiles[:10]

    def fetch_data(self):
        return MATCHING.find_one({'_id':self._id})

    def edit(self, data, upsert=False):
        result = MATCHING.update_one({'_id':self._id}, data, upsert=upsert)
        return result
    
    def generate_embed(self, color=0xffa1dc):
        description = f"""
        ❥﹒User: {self.user.mention} | `{self.user.global_name}`
        ❥﹒Name: `{self.name}`
        ❥﹒Pronouns: `{self.pronouns}`
        ❥﹒Gender: `{self.gender}`
        ❥﹒Age: `{self.age}`
        ❥﹒Sexuality: `{self.sexuality}`
        ❥﹒Bio:\n```{self.bio}```
        """

        profile_embed = Embed(
        title="Profile",
        description=description,
        color=color)
        profile_embed.set_footer(text=f'Profile Id: {self._id}')
        profile_embed.set_author(name=self.user.global_name, icon_url=self.user.avatar.url)

        return profile_embed
    
    def queue_profile(self, message_id:int):
        return self.edit({"$set": {"approved":"waiting", "message_id":message_id,"date":int(time())}})
        
        




def qet_queued(message_id:int, bot) -> Profile:
    """
    gets the profile of a user if they are queued

    Parameters
    ----------
    user : int
        the message_id to get the queued data on

    Returns
    -------
    dict | none
        returns a dict of the users profile
    """
    data = MATCHING.find_one({'message_id':message_id}) or None
    return Profile(bot, data)




def get_profile(user:Member, bot:Bot) -> Profile:
    """
    gets a users profile

    Parameters
    ----------
    user : discord.Member
        the user of the profile you wish to edit
    
    Returns
    -------
    dict | None
        returns a dict of the users profile data or None
    """
    if not user:
        raise UserNotFoundException()
    data = MATCHING.find_one({'user_id':user.id}) or None
    return Profile(bot, data)




# TODO
### MAKE THESE PART OF PROFILE
def compatibility_check(user_a_id:int, user_b_id:int, ignore_selected:bool=False) -> bool:
    """
    checks the compatibility of 2 users

    compatibility params:
    age is within 2 years of each other
    profiles are both approved
    profiles havent already selected each other

    Parameters
    ----------
    user_a : int
        the id of first user to check
    user_b : discord.Member
        the id of second user to check 
    
    Returns
    -------
    bool 
        returns true if compatible, false if not
    """

    data_a:dict = MATCHING.find_one({'user_id': user_a_id})
    data_b:dict = MATCHING.find_one({'user_id': user_b_id})

    age_a = int(data_a.get('age', 0))
    age_b = int(data_b.get('age', 100))

    # if between 0-4 then we compatible
    range = age_a + 2 - age_b

    if ignore_selected:
        if (
            data_a != data_b
            and data_b.get('approved') == True
            and data_a.get('approved') == True
            and range >= 0 and range <=4   
            and data_b.get('user_id') not in data_a.get('rejected_pairs')   
        ):
            return True
        else:
            return False
        

    if (
        data_a != data_b
        and data_b.get('approved') == True
        and data_a.get('approved') == True
        and range >= 0 and range <=4
        and data_a.get('user_id') not in data_b.get('selected_pairs', [])
        and data_b.get('user_id') not in data_a.get('selected_pairs', [])
        and data_b.get('user_id') not in data_a.get('rejected_pairs')
    ):
        return True
    else:
        return False



def get_compatible(user:Member, server_only=False, ignore_selected=False) -> list[dict] | None:
    """
    gets all the compatible users for our user

    Parameters
    ----------
    user : discord.Member
        the user to generate the compatibility list
    
    Returns
    -------
    list[discord.Member] | False
        returns a list of all discord.Members that are compatible, or false is current user isnt approved
    """
    user_data = get_profile(user)
    if not user_data or user_data.get('approved') != True: return []

    profiles = []

    for profile in MATCHING.find({'approved': True}):
        if not compatibility_check(user.id, profile.get('user_id'), ignore_selected=ignore_selected): continue
        profiles.append(profile)
    
    return profiles


