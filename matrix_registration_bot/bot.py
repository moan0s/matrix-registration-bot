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

bot_prefix = config['bot']['prefix']

# Load a config file that configures bot behaviour
smbl_config = botlib.Config()
smbl_config.emoji_verify = True
smbl_config.ignore_unverified_devices = True
SIMPLE_MATRIX_BOT_CONFIG_FILE = "config.toml"
try:
    smbl_config.load_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)
    logging.info(f"Loaded the simple-matrix-bot config file {SIMPLE_MATRIX_BOT_CONFIG_FILE}")
except FileNotFoundError:
    logging.info(f"No simple-matrix-bot config file found. Creating {SIMPLE_MATRIX_BOT_CONFIG_FILE}")
    smbl_config.save_toml(SIMPLE_MATRIX_BOT_CONFIG_FILE)

bot = botlib.Bot(creds, smbl_config)

try:
    api_base_url = config['api']['base_url']
except KeyError:
    api_base_url = bot_server

"""
Here we get the configured credentials for the admin API.
We first check if an API token is set, if not we try if there are credentials set in the api section of the config
and after that we use the credentials provided for the bot. Users are encouraged to use the last option, but we allow
to overwrite this.
"""
try:
    api_token = config['api']['token']
    api = RegistrationAPI(api_base_url, api_token)
    logging.info("Using API token from api section of config")
except KeyError:
    try:
        admin_username = config['api']['username']
        admin_password = config['api']['password']
        logging.info("Using username/password from api section of config")
    except KeyError:
        admin_username = config['bot']['username']
        admin_password = config['bot']['password']
        logging.info("Using username/password from bot section of config")
    # The API interface will obtain an API token by itself
    api = RegistrationAPI(api_base_url, username=admin_username, password=admin_password)

help_string = (
    f"""**[Matrix Registration Bot](https://github.com/moan0s/matrix-registration-bot/)** {matrix_registration_bot.__version__}
You can always ask for help in
[#matrix-registration-bot:hyteck.de](https://matrix.to/#/#matrix-registration-bot:hyteck.de)!

**Unrestricted commands**

* `{bot_prefix}help`: Shows this help

**Restricted commands**

* `{bot_prefix}list`: Lists all registration tokens
* `{bot_prefix}show <token>`: Shows token details in human-readable format
* `{bot_prefix}create`: Creates a token that that is valid for one registration for seven days
* `{bot_prefix}delete <token>` Deletes the specified token(s)
* `{bot_prefix}delete-all` Deletes all tokens
* `{bot_prefix}allow @user:example.com` Allows the specified user (or a user matching a regex pattern) to use restricted commands
* `{bot_prefix}disallow @user:example.com` Stops a specified user (or a user matching a regex pattern) from using restricted commands
""")


def allowed_required(func):
    async def wrapper(match, room, *args, **kwargs):
        if match.is_from_allowed_user():
            await func(match, room, *args, **kwargs)
        else:
            logging.info(f"{match.event.sender} tried to execute {func}")
            await bot.api.send_markdown_message(
                room.room_id,
                f'You are not allowed to do that (restricted command). Ask someone to allow you (send `help` to find '
                f'out more)')

    return wrapper


@allowed_required
async def action_list(match, room):
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


@allowed_required
async def action_create_token(match, room):
    try:
        token = await api.create_token()
        logging.info(f"{match.event.sender} created token {token}")
        await bot.api.send_markdown_message(room.room_id, f"{RegistrationAPI.token_to_markdown(token)}")
    except (ConnectionError, PermissionError, FileNotFoundError) as e:
        logging.warning(f"Error while trying to create a token: {e}")
        await error_handler(room, e)


@allowed_required
async def action_delete(match, room):
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


@allowed_required
async def action_delete_all(match, room):
    deleted_tokens = await api.delete_all_token()
    logging.info(f"{match.event.sender} deleted all tokens")
    await send_info_on_deleted_token(room, deleted_tokens)


@allowed_required
async def action_show(match, room):
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


@allowed_required
async def action_allow(match, room):
    sender = match.event.sender
    bot.config.add_allowlist(set(match.args()).union(set([sender,])))
    bot.config.save_toml("config.toml")
    logging.info(f"{match.event.sender} allowed {set(match.args())} (if valid)")
    await bot.api.send_text_message(
        room.room_id,
        f'allowing {", ".join(arg for arg in match.args())} (if valid)')


@allowed_required
async def action_disallow(match, room):
    bot.config.remove_allowlist(set(match.args()))
    bot.config.save_toml("config.toml")
    logging.info(f"{match.event.sender} disallowed {set(match.args())} (if valid)")
    await bot.api.send_text_message(
        room.room_id,
        f'disallowing {", ".join(arg for arg in match.args())} (if valid)')

@bot.listener.on_message_event
async def token_actions(room, message):
    match = botlib.MessageMatch(room, message, bot, bot_prefix)

    if match.is_not_from_this_bot() and match.prefix():
        # Unrestricted commands
        if match.contains("help"):
            """The help command should be accessible even to users that are not allowed"""
            logging.info(f"{match.event.sender} viewed the help")
            await bot.api.send_markdown_message(room.room_id, help_string)

        # Restricted commands
        if match.command("list"):
            await action_list(match, room)
        elif match.command("create"):
            await action_create_token(match, room)
        elif match.command("delete-all"):
            await action_delete_all(match, room)
        elif match.command("delete"):
            await action_delete(match, room)
        elif match.command("show"):
            await action_show(match, room)
        elif match.command("allow"):
            await action_allow(match, room)
        elif match.command("disallow"):
            await action_disallow(match, room)


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
