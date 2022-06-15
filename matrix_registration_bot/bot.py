import cryptography
import simplematrixbotlib as botlib
import matrix_registration_bot
from matrix_registration_bot.registration_api import RegistrationAPI
from matrix_registration_bot.config import Config
import logging
import argparse

parser = argparse.ArgumentParser(description='Start the matrix-registration-bot.')

parser.add_argument('--config', default=None, help='Specify a configuration file to use')

args = parser.parse_args()
if args.config is None:
    config_path = 'config.yml'
else:
    config_path = args.config
config = Config(args.config)

bot_server = config['bot']['server']
bot_username = config['bot']['username']
try:
    bot_access_token = config['bot']['access_token']
    creds = botlib.Creds(bot_server,
                         username=bot_username,
                         access_token=bot_access_token)
except KeyError:
    logging.info("Using password based authentication for the bot")
    try:
        bot_access_password = config['bot']['password']
    except KeyError:
        error = "No access token or password for the bot provided"
        logging.error(error)
        raise KeyError(error)
    creds = botlib.Creds(bot_server,
                         username=bot_username,
                         password=bot_access_password)
api_base_url = config['api']['base_url']
api_endpoint = '/_synapse/admin/v1/registration_tokens'
api_token = config['api']['token']

# Load a config file that configures bot behaviour
smbl_config = botlib.Config()
SIMPLE_MATRIX_BOT_CONFIG_FILE = "config.toml"
try:
    smbl_config.load_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)
    logging.info(f"Loaded the simple-matrix-bot config file {SIMPLE_MATRIX_BOT_CONFIG_FILE}")
except FileNotFoundError:
    logging.info(f"No simple-matrix-bot config file found. Creating {SIMPLE_MATRIX_BOT_CONFIG_FILE}")
    smbl_config.save_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)

bot = botlib.Bot(creds, smbl_config)

api = RegistrationAPI(api_base_url, api_endpoint, api_token)

help_string = (
    f"""**[Matrix Registration Bot](https://github.com/moan0s/matrix-registration-bot/)** {matrix_registration_bot.__version__}
You can always ask for help in
[#matrix-registration-bot:hyteck.de](https://matrix.to/#/#matrix-registration-bot:hyteck.de)!

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
        logging.info(f"{match.event.sender} viewed the help")
        await bot.api.send_markdown_message(room.room_id, help_string)
    # Restricted commands
    elif match.is_not_from_this_bot() and match.is_from_allowed_user():
        if match.command("list"):
            logging.info(f"{match.event.sender} listed all tokens")
            try:
                token_list = await api.list_tokens()
            except ConnectionError as e:
                logging.warning(f"Error while trying to list all tokens: {e}")
                await error_handler(room, e)
                return
            if len(token_list) < 10:
                message = "\n".join([RegistrationAPI.token_to_markdown(token) for token in token_list])
            else:
                tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
                message = f"All tokens: {', '.join(tokens_as_string)}"
            await bot.api.send_markdown_message(room.room_id, message)

        if match.command("create"):
            try:
                token = await api.create_token()
                logging.info(f"{match.event.sender} created token {token}")
                await bot.api.send_markdown_message(room.room_id, f"{RegistrationAPI.token_to_markdown(token)}")
            except (ConnectionError, PermissionError, FileNotFoundError) as e:
                logging.warning(f"Error while trying to create a token: {e}")
                await error_handler(room, e)

        if match.command("delete-all"):
            deleted_tokens = await api.delete_all_token()
            logging.info(f"{match.event.sender} deleted all tokens")
            await send_info_on_deleted_token(room, deleted_tokens)

        if match.command("delete"):
            deleted_tokens = []
            logging.info(f"{match.event.sender} tries to delete {match.args()}")
            if not len(match.args()) > 0:
                await bot.api.send_markdown_message(room.room_id, "You must give a token!")
            for token in match.args():
                token = token.strip()
                try:
                    deleted_tokens.append(await api.delete_token(token))
                except ValueError as e:
                    logging.info(f"Token {token} given by {match.event.sender} to delete was not in correct format")
                    await error_handler(room, e)
                except FileNotFoundError as e:
                    logging.info(f"Token {token} given by {match.event.sender} to delete was not found")
                    await error_handler(room, e)
                except ConnectionError as e:
                    logging.warning(f"Error: {e} while trying to get a token")
                    await error_handler(room, e)
            logging.info(f"{match.event.sender} deleted token {deleted_tokens}")
            await send_info_on_deleted_token(room, deleted_tokens)

        if match.command("show"):
            tokens_info = []
            logging.info(f"{match.event.sender} tries to show {match.args()}")
            if not len(match.args()) > 0:
                await bot.api.send_markdown_message(room.room_id, "You must give a token!")
                return
            for token in match.args():
                token = token.strip()
                try:
                    token_info = await api.get_token(token)
                    logging.info(f"Showing {token} to {match.event.sender}")
                    tokens_info.append(RegistrationAPI.token_to_markdown(token_info))
                except ConnectionError as e:
                    logging.warning(f"Error while trying to get a token: {e}")
                    await error_handler(room, e)
                except FileNotFoundError as e:
                    logging.info(f"Token {token} given by {match.event.sender} to show was not found")
                    await error_handler(room, e)
                except TypeError as e:
                    logging.info(f"Token {token} given by {match.event.sender} to show was not in correct format")
                    await error_handler(room, e)
            if len(tokens_info) > 0:
                await bot.api.send_markdown_message(room.room_id, "\n".join(tokens_info))

        if match.command("allow"):
            bot.config.add_allowlist(set(match.args()))
            bot.config.save_toml("config.toml")
            logging.info(f"{match.event.sender} allowed {set(match.args())} (if valid)")
            await bot.api.send_text_message(
                room.room_id,
                f'allowing {", ".join(arg for arg in match.args())} (if valid)')

        if match.command("disallow"):
            bot.config.remove_allowlist(set(match.args()))
            logging.info(f"{match.event.sender} disallowed {set(match.args())} (if valid)")
            await bot.api.send_text_message(
                room.room_id,
                f'disallowing {", ".join(arg for arg in match.args())} (if valid)')


async def send_info_on_deleted_token(room, token_list):
    if len(token_list) > 0:
        message = f"Deleted the following token(s): "
        tokens_as_string = [RegistrationAPI.token_to_short_markdown(token) for token in token_list]
        message += ", ".join(tokens_as_string)
    else:
        message = "No token deleted"
    await bot.api.send_markdown_message(room.room_id, message)


async def error_handler(room, error):
    message = f"The bot encountered the following error:\n"
    message += error.args[0]
    await bot.api.send_markdown_message(room.room_id, message)


def run_bot():
    try:
        bot.run()
    except cryptography.fernet.InvalidToken:
        logging.error("The token does not seem to fit the saved session. this can happen if you change the bot user."
                      "If this is the case, deleting the session.txt and restarting the bot might help")
        exit(1)


if __name__ == "__main__":
    run_bot()
