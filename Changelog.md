# 1.1.8

**NO user action needed**

## Enhancements

* **Encryption support 🥳**: The bot can now use encryption by default. This is possible thanks to the work of [simple-matrix-bot-lib](https://codeberg.org/imbev/simplematrixbotlib)
  (the framework this bot uses) and @noobping that added the support in this bot.

* **Bot Prefix is now configurable:** The bot uses no prefix by default. To make the bot respond (only) when using a specific prefix (e.g. `!`) you can use
    ```yaml
    bot:
        prefix: "!"
    ```

## Bugfixes

*  @olivercoad discovered and fixed a case where we don't safe the config correctly after disallowing a person/pattern