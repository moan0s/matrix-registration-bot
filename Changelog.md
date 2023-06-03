# 1.2.2

Updating dependencies

**New docker versioning**
We also introduce a new docker version scheme. Docker versions should follow the versioning
of `<package-version>-0` where 0 ist the docker iteration and is increased by one for each docker build of the same
package version. This helps if the package is okay but the docker build has an error. Docker tag `1.2.2` can be seen as
`1.2.2-0` but you should use `1.2.2-1` or newer.

# 1.2.0

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