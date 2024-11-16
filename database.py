# Database Features for the bot
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
cupid = client.get_database("cupid")
levels = cupid.get_collection('levels')
infractions = cupid.get_collection('infractions')
config = cupid.get_collection('config')
matching = cupid.get_collection('matching')



def generate_profile_description(user_id:int):
    data:dict = matching.find_one({'user_id':user_id})
    name = data.get('name', None) if data else None
    age = data.get('age', None) if data else None
    gender = data.get('gender', None) if data else None
    pronouns = data.get('pronouns', None) if data else None
    sexuality = data.get('sexuality', None) if data else None 
    bio = data.get('bio', None) if data else None
    resp_id = str(data.get('_id')) if data else None

    return f"❥﹒Name: `{name}`\n❥﹒Pronouns: `{pronouns}`\n❥﹒Gender: `{gender}`\n❥﹒Age: `{age}`\n❥﹒Sexuality: `{sexuality}`\n❥﹒Bio:\n```{bio}```", resp_id