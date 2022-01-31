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
                     access_token=bot_access_token)

# Load a config file that configures bot behaviour
config = botlib.Config()
SIMPLE_MATRIX_BOT_CONFIG_FILE = "config.toml"
try:
    config.load_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)
except FileNotFoundError:
    config.save_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)

bot = botlib.Bot(creds, config)

api = RegistrationAPI(api_base_url, api_endpoint, api_token)

help_string = (
    f"""**[Matrix Registration Bot](https://github.com/moan0s/matrix-registration-bot/)** {matrix_registration_bot.__version__}
You can always message my creator [@moanos:hyteck.de](https://matrix.to/#/@moanos:hyteck.de) if you have questions

**Unrestricted commands**

* `help`: Shows this help

**Restricted commands**

* `list`: Lists all registration tokens
* `show <token>`: Shows token details in human-readable format
* `create`: Creates a token that that is valid for one registration for seven days
* `delete <token>` Deletes the specified token(s)
* `delete-all` Deletes all tokens
* `allow @user:example.com` Allows the specified user (or a user matching a regex pattern) to use restricted commands
* `disallow @user:example.com` Stops a specified user (or a user matching a regex pattern) from using restricted commands
""")


@bot.listener.on_message_event
async def token_actions(room, message):
    match = botlib.MessageMatch(room, message, bot)
    # Unrestricted commands
    if match.is_not_from_this_bot() and match.contains("help"):
        """The help command should be accessible even to users that are not allowed"""
        await bot.api.send_markdown_message(room.room_id, help_string)
    # Restricted commands
    elif match.is_not_from_this_bot() and match.is_from_allowed_user():
        if match.command("list"):
            token_list = await api.list_tokens()
            if len(token_list) < 10:
                message = "\n".join([RegistrationAPI.token_to_markdown(token) for token in token_list])
            else:
                tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
                message = f"All tokens: {', '.join(tokens_as_string)}"
            await bot.api.send_markdown_message(room.room_id, message)

        if match.command("create"):
            token = await api.create_token()
            await bot.api.send_markdown_message(room.room_id, f"{RegistrationAPI.token_to_markdown(token)}")

        if match.command("delete-all"):
            deleted_tokens = await api.delete_all_token()
            await send_info_on_deleted_token(room, deleted_tokens)

        if match.command("delete"):
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

        if match.command("show"):
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

        if match.command("allow"):
            bot.config.add_allowlist(set(match.args()))
            bot.config.save_toml("config.toml")
            await bot.api.send_text_message(
                room.room_id,
                f'allowing {", ".join(arg for arg in match.args())}')

        if match.command("disallow"):
            bot.config.remove_allowlist(set(match.args()))
            await bot.api.send_text_message(
                room.room_id,
                f'disallowing {", ".join(arg for arg in match.args())}')


async def send_info_on_deleted_token(room, token_list):
    if len(token_list) > 0:
        message = f"Deleted the following token(s): "
        tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
        message += ", ".join(tokens_as_string)
    else:
        message = "No token deleted"
    await bot.api.send_markdown_message(room.room_id, message)


bot.run()
