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
