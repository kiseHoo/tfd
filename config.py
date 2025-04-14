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
PRIVATE_CHAT_ID = -100  # CHAT WHERE YOU WANT TO STORE VIDEOS
USER_CHANNEL = -100
DUMP_CHANNEL = -100


# Config
COOKIE = environ.get("COOKIE", "")
