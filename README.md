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

Download the project from GitHub
```bash
$ https://github.com/moan0s/matrix-registration-bot
$ cd matrix-registration-bot
```

then adjust the configuration by copying and editing the example config.

```bash
$ cp example_config.yml config.yml
```

You can then simply start the bot with

```bash
python bot.py
```

# Usage

Open a Direct Message to the bot. The type one of the following commands.

# Supported commands

* `!help`: Shows this help
* `!list`: Lists all registration token
* `!create`: Creates a token that that is valid for one registration for seven days
* `!delete <token>` Deletes the specified token
* `!delete-all` Deletes all token

# Security

The bot in the current state is very unsafe (unchecked input is fed into requests).

# Contibuting

Feel free to contribute or discuss this bot with me. You can reach me via @moanos:hyteck.de. The project is made possible by [Simple-Matrix-Bot-Lib](https://simple-matrix-bot-lib.readthedocs.io).

[Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)
