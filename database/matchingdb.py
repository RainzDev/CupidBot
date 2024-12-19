from discord import Embed, Member, Message
from database.databasev2 import MATCHING, NoProfileException
from time import time

# puts the profile in a queue to be verifed
def queue_profile(user:Member, message:Message) -> None:
    """
    Adds the users queue message to be verified
    this stores their user_id and message_id for the profilesubmission buttons

    Parameters
    ----------
    user : discord.Member
        the user of the profile you wish to queue
    message : discord.Message
        the message for the id we want to store

    Returns
    -------
    none
        returns None
    """
    edit_profile(user, {"$set": {"approved":"waiting", "message_id":message.id,"date":int(time())}})



def qet_queued(message_id:int) -> dict | None:
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
    return data



def generate_profile_embed(user:Member, color:int=0xffa1dc) -> Embed:
    """
    Creates a discord.Embed using profile information from the provided user_id

    Parameters
    ----------
    user : discord.Member
        the user of the profile you wish to generate an embed of
    color : int (base 16)
        the color of the embed

    Returns
    -------
    discord.Embed
        returns a discord.Embed using the provided user_id to generate a description an embed
    """
    
    # grabs profile data, checks if it exists, if not return exception
    profile_data:dict = MATCHING.find_one({'user_id': user.id})
    if not profile_data:
        raise NoProfileException()
    
    # grab the profile data store it in vars
    name = profile_data.get('name')
    age = profile_data.get('age')
    gender = profile_data.get('gender')
    pronouns = profile_data.get('pronouns')
    sexuality = profile_data.get('sexuality')
    bio = profile_data.get('bio')
    resp_id = str(profile_data['_id'])

    # self explainitory
    description = f"""
    ❥﹒User: {user.mention}
    ❥﹒Name: `{name}`
    ❥﹒Pronouns: `{pronouns}`
    ❥﹒Gender: `{gender}`
    ❥﹒Age: `{age}`
    ❥﹒Sexuality: `{sexuality}`
    ❥﹒Bio:\n```{bio}```
    """
    # creates the profile embed
    profile_embed = Embed(
        title="Profile",
        description=description,
        color=color)
    profile_embed.set_footer(text=f'Profile Id: {resp_id}')
    profile_embed.set_author(name=user.global_name, icon_url=user.avatar.url)

    return profile_embed



def edit_profile(user:Member, data:dict, upsert:bool=False) -> None:
    """
    Edits the users provided data with the provided value

    Parameters
    ----------
    user : discord.Member
        the user of the profile you wish to edit
    data : dict
        the data you want to edit
    upsert : str
        weather or not to update the data AND insert or not

    Returns
    -------
    None
        returns None
    """

    MATCHING.update_one({'user_id':user.id}, data, upsert=upsert)
    


def get_profile(user:Member) -> dict | None:
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

    data = MATCHING.find_one({'user_id':user.id}) or None
    return data



def compatibility_check(user_a_id:int, user_b_id:int) -> bool:
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


    if (
        data_a != data_b
        and data_b.get('approved') == True
        and data_a.get('approved') == True
        and range >= 0 and range <=4
        and data_a.get('user_id') not in data_b.get('selected_pairs', [])
        and data_b.get('user_id') not in data_a.get('selected_pairs', [])
    ):
        return True
    else:
        return False



def get_compatible(user:Member, server_only=False) -> list[int] | None:
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
    if user_data.get('approved') != True: return None

    profiles = []

    for profile in MATCHING.find({'approved': True}):
        if not compatibility_check(user.id, profile.get('user_id')): continue
        profiles.append(profile)
    
    return profiles
