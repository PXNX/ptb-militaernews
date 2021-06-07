import os

##########################################
# Contains variables used throughout the project
##########################################

PORT = int(os.environ.get('PORT', 5000))
DATABASE_URL = os.environ['DATABASE_URL'].replace('postgres', 'postgresql', 1)
TOKEN = os.environ['TOKEN']

CHANNEL_MEME = -1001486678205
CHANNEL_MAIN = -1001240262412

GROUP_MAIN = -1001277960773
GROUP_SHITPOST = -1001284212903


ADMINS = (703453307,  # Nyx
          466451473,  # Maxe
          )

VERIFIED_USERS = set(ADMINS + (

))
