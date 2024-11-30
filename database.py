# Database Features for the bot
from pymongo import MongoClient
from discord import Member

client = MongoClient("mongodb://localhost:27017/")
cupid = client.get_database("cupid")
levels = cupid.get_collection('levels')
infractions = cupid.get_collection('infractions')
config = cupid.get_collection('config')
matching = cupid.get_collection('matching')

def generate_profile_description(user_id: int):
    data: dict = matching.find_one({'user_id': user_id})
    if not data:
        return "Profile not found.", None
    
    name = data['name']
    age = data['age']
    gender = data['gender']
    pronouns = data['pronouns']
    sexuality = data['sexuality']
    bio = data['bio']
    resp_id = str(data['_id'])

    return f"❥﹒Name: `{name}`\n❥﹒Pronouns: `{pronouns}`\n❥﹒Gender: `{gender}`\n❥﹒Age: `{age}`\n❥﹒Sexuality: `{sexuality}`\n❥﹒Bio:\n```{bio}```", resp_id

def find_compatible_profiles(user_id: int, members: list[Member]):
    data: dict = matching.find_one({'user_id': user_id})
    if not data: return False, "You have no profile! Create one using `/matching profile create`"
    if not data.get('approved'): return False, "You haven't been approved! Please wait for it to be approved/denied"

    age = int(data['age'])
    user_ids = [member.id for member in members]
    rejected_ids = data.get('rejected_pairs', [])
    selected_ids = data.get('selected_pairs', [])

    profiles = []

    for profile in matching.find({'approved': True}):
        if (
            int(profile['user_id']) == user_id
            or profile['user_id'] not in user_ids
            or int(profile['age']) > age + 2
            or int(profile['age']) < age - 2
            or profile.get('paired') is True
            or profile['user_id'] in rejected_ids
        ):
            continue
        
        profiles.append(profile)

    if not profiles:
        return False, "There is no one for you to match with, sorry!"
    
    return True, profiles
