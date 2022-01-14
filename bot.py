import simplematrixbotlib as botlib
from token_register import RegisterAPI
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)
    print(config)

bot_username = config['bot']['username']
bot_access_token = config['bot']['access_token']
api_base_url = config['api']['base_url']
api_token = config['api']['token']

creds = botlib.Creds("https://synapse.hyteck.de",
                     username = bot_username,
                     access_token = bot_access_token,
                     session_stored_file="session.txt")
bot = botlib.Bot(creds)
PREFIX = '!'

register_api = RegisterAPI(api_base_url, api_token)

@bot.listener.on_message_event
async def list_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("list"):
        token_list = register_api.list_token()
        await bot.api.send_text_message(room.room_id, f"{token_list}")

@bot.listener.on_message_event
async def list_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("create"):
        token_list = register_api.create_token()
        await bot.api.send_text_message(room.room_id, f"{token_list}")

bot.run()

