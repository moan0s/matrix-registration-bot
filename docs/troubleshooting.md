# Troubleshooting

This document tries to help you with common problems. If you would rather ask a human or this document does not help you
come join [#matrix-registration-bot:hyteck.de](https://matrix.to/#/#matrix-registration-bot:hyteck.de). If you believe
that you found a bug please report it on [GitHub](https://github.com/moan0s/matrix-registration-bot/issues).

## Bot does not accept invite

This indicates that the bot is not working properly. Check if the bot is still running and what the logs say. Usually
this is a misconfiguration of the bot in `config.yml`.

## Bot accepts invite but does not answer

Check if the chat with the bot is encrypted. The bot does not yet support encryption, therefore it will not work in such
a room. You can circumvent this problem by creating an unencrypted room and invite the bot to it.
