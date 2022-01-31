# Matrix Registration Bot

This bot aims to create and manage registration tokens for a matrix server. It wants to help invitation based servers to maintain usability.
It does not create a user itself, but rather aims to make use of [MSC3231](https://github.com/matrix-org/matrix-doc/blob/main/proposals/3231-token-authenticated-registration.md).
The feature is still experimental. More information can be found in the [Synapse Documentation](https://matrix-org.github.io/synapse/latest/usage/administration/admin_api/registration_tokens.html).

# Getting started

## Prerequisites

**Server configuration**

Your server should be configured to a token restricted registration. Add the following to your `homeserver.yaml`:

```yaml
enable_registration: true
registration_requires_token: true
```

**Create a bot account**

Then you need to create an account for the bot on the server, like you would do with any other account.
A good username is `registration-bot`. Also note the access token of the bot. One way to get the token is to login as 
the bot and got to Settings -> Help & About -> Access Token in Element.

Once you are finished you can start the installation of the bot.

## Installation

The installation can easily be done via [PyPi](https://pypi.org/project/matrix-registration-bot/)
```bash
$ pip install matrix-registration-bot
```

## Configuration

Configure the bot with a file named `config.yml`. It should look like this

```yaml
bot:
  server: "https://synapse.example.com"
  username: "registerbot"
  access_token: "verysecret"
api:
  # API endpoint of the registration tokens
  base_url: 'https://synapse.example.com'
  endpoint: '/_synapse/admin/v1/registration_tokens'
  # Access token of an administrator on the server
  token: "supersecret"


```



# Usage

Start the bot with 
```bash
python -m matrix_registration_bot.bot
```

and then open a Direct Message to the bot. The type one of the following commands.

# Supported commands

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

# Permissions

By default, any user on the homeserver of the bot is allowed to use restricted commands. You can change that,
by using the `allow` command to configure one (or multiple) specific user. Read the [simple-matrix-bot documentation](https://simple-matrix-bot-lib.readthedocs.io/en/latest/manual.html#allowlist)
for more information. If you get locked out for any reason, simply modify the config.toml that is created in the bots
working directory.

# Contributing

Feel free to contribute or discuss this bot with me. You can reach me via @moanos:hyteck.de. The project is made possible by [Simple-Matrix-Bot-Lib](https://simple-matrix-bot-lib.readthedocs.io).

[Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)
