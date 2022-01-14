# Registerbot

This bot aims to create and manage registration tokens for a matrix server. It wants to help invitation based servers to maintain usability.

# Supported commands

* `!list`: Lists all registration token
* `!create`: Creates a token that that is valid for one registration for seven days
* `!delete <token>` Deletes the specified token
* `!delete-all` Deletes all token

# Security

The bot in the current state is very unsafe (unchecked input is fed into requests).
