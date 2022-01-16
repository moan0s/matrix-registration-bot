import simplematrixbotlib as botlib
import matrix_registration_bot
from matrix_registration_bot.registration_api import RegistrationAPI
import yaml

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

bot_server = config['bot']['server']
bot_username = config['bot']['username']
bot_access_token = config['bot']['access_token']
api_base_url = config['api']['base_url']
api_endpoint = config['api']['endpoint']
api_token = config['api']['token']

creds = botlib.Creds(bot_server,
                     username=bot_username,
                     access_token=bot_access_token,
                     session_stored_file="../session.txt")
bot = botlib.Bot(creds)
PREFIX = '!'

api = RegistrationAPI(api_base_url, api_endpoint, api_token)


@bot.listener.on_message_event
async def list_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)
    if match.is_not_from_this_bot() and match.prefix() and match.command("list"):
        token_list = await api.list_tokens()
        if len(token_list) < 10:
            message = "\n".join([RegistrationAPI.token_to_markdown(token) for token in token_list])
        else:
            tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
            message = f"All tokens: {', '.join(tokens_as_string)}"
        await bot.api.send_markdown_message(room.room_id, message)


@bot.listener.on_message_event
async def create_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("create"):
        token = await api.create_token()
        await bot.api.send_markdown_message(room.room_id, f"{RegistrationAPI.token_to_markdown(token)}")


async def send_info_on_deleted_token(room, token_list):
    if len(token_list) > 0:
        message = f"Deleted the following token(s): "
        tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
        message += ", ".join(tokens_as_string)
    else:
        message = "No token deleted"
    await bot.api.send_markdown_message(room.room_id, message)


@bot.listener.on_message_event
async def delete_all_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("delete-all"):
        deleted_tokens = await api.delete_all_token()
        await send_info_on_deleted_token(room, deleted_tokens)


@bot.listener.on_message_event
async def delete_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("delete"):
        deleted_tokens = []
        for token in match.args():
            token = token.strip()
            try:
                deleted_tokens.append(await api.delete_token(token))
            except ValueError as e:
                await bot.api.send_text_message(room.room_id, f"Error: {e.args[0]}")
            except FileNotFoundError as e:
                await bot.api.send_text_message(room.room_id, f"Error: {e.args[0]}")
        await send_info_on_deleted_token(room, deleted_tokens)


@bot.listener.on_message_event
async def show_token(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("show"):
        tokens_info = []
        for token in match.args():
            token = token.strip()
            try:
                token_info = await api.get_token(token)
                tokens_info.append(RegistrationAPI.token_to_markdown(token_info))
            except FileNotFoundError as e:
                await bot.api.send_text_message(room.room_id, f"Error: {e.args[0]}")
            except TypeError as e:
                await bot.api.send_text_message(room.room_id, f"Error: {e.args[0]}")
        await bot.api.send_markdown_message(room.room_id, "\n".join(tokens_info))


help_string = (f"""**[Matrix Registration Bot](https://github.com/moan0s/matrix-registration-bot/)** {matrix_registration_bot.__version__}
You can always message my creator [@moanos:hyteck.de](https://matrix.to/#/@moanos:hyteck.de) if you have questions

* `!help`: Shows this help
* `!list`: Lists all registration tokens
* `!show <token>`: Shows token details in human-readable format
* `!create`: Creates a token that that is valid for one registration for seven days
* `!delete <token>` Deletes the specified token(s)
* `!delete-all` Deletes all tokens
""")


@bot.listener.on_message_event
async def bot_help(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.contains("help"):
        await bot.api.send_markdown_message(room.room_id, help_string)

bot.run()
