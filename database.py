# Database Features for the bot
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
cupid = client.get_database("cupid")
levels = cupid.get_collection('levels')
infractions = cupid.get_collection('infractions')