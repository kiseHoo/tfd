from os import environ


# BOT CONFIG
API_ID = environ.get("API_ID", "14050586")  # api id
API_HASH = environ.get("API_HASH", "42a60d9c657b106370c79bb0a8ac560c")  # api hash
BOT_TOKEN = environ.get("BOT_TOKEN", "")  # bot token

# REDIS
REDIS_HOST = environ.get("REDIS_HOST", "http://redis-11377.c15.us-east-1-4.ec2.redns.redis-cloud.com")  # redis host uri
REDIS_PORT = environ.get("REDIS_PORT", "11377")  # redis port
REDIS_PASSWORD = environ.get(
    "REDIS_PASSWORD", "9ehjpwclZQfeIwE0lAt9SJ2nh7KG9gus"
)  # redis password


ADMINS = [5738579437]
OWNER_ID = 5738579437  # Replace with your Telegram user ID
PRIVATE_CHAT_ID = -1002561334306  # CHAT WHERE YOU WANT TO STORE VIDEOS
USER_CHANNEL = -1002508586242
DUMP_CHANNEL = -1002561334306


# Config
COOKIE = environ.get("COOKIE", "PANWEB=1; csrfToken=SlG3EHVGdauCDO4Rl8YJkRF4; browserid=me9b3gO3KyIcbje9j0HeWmSC-u_Vty-TzJBElBySlbVLAuJko3Kz_wQKPzw=; lang=en; bid_n=18f753c1c3635204fd4207; ab_sr=1.0.1_Y2IwMDcxNDc1Yjc5NmM2NzRjMDA1NjRhN2YzYjk3MjQwZDAxMjMzZmRjNjViMzdmY2IxN2VmNGU2MWE1MjE3MDA5MTRhMjc4ZjM1NDI1NWQ1MmRkZGY0Y2JmOTkwZDFmMmI3NGUzZjFlNTUyZTdiYzRiNWZhZDA2MDI0MGNlYmYxYmNkZjExNzFmOWZhYmRlZjY5MmZkNWIzODQyMDQ0OQ==; ndus=Yfoxfv7teHuiIHLB5W1wSoAP8G7_l8pAhmWIAYFu; ndut_fmt=F973758CA4D9E5B17CDC91EEF01BFAE050E4FF332F993ECC9E849F9304680D55")
