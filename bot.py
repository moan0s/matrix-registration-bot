import simplematrixbotlib as botlib
from registration_api import RegistrationAPI
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

api = RegistrationAPI(api_base_url, api_token)

@bot.listener.on_message_event
async def list_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("list"):
        token_list = api.list_tokens()
        await bot.api.send_text_message(room.room_id, f"{token_list}")

@bot.listener.on_message_event
async def create_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("create"):
        token_list = api.create_token()
        await bot.api.send_text_message(room.room_id, f"{token_list}")

@bot.listener.on_message_event
async def delete_all_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("delete-all"):
        token_list = api.delete_all_token()
        await bot.api.send_text_message(room.room_id, f"Deleted the following token {token_list}")

@bot.listener.on_message_event
async def delete_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("delete"):
        deleted_tokens = []
        for token in match.args():
            api.delete_token(token)
            deleted_tokens.append(token)
        await bot.api.send_text_message(room.room_id, f"Deleted the following token {deleted_tokens}")


bot.run()

