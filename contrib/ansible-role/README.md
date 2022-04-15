# matrix-registration-bot Ansible role

Written for Debian 11
(does not work on Debian 10 with Python 3.7,
because the [simplematrixbotlib](https://pypi.org/project/simplematrixbotlib/)
dependency is only available for newer Python versions).

Installs the virtual environment in `/opt/venvs/matrix-registration-bot`
next to the virtual environment created by the official Matrix Synapse Debian package.


## Usage

Copy this role to your desired Ansible roles directory, name and modify it as you see fit
and configure the variables below for your groups/hosts.
Use the Ansible Vault to store secrets.


### Variables

* `matrix_registration_bot_enabled` True will enable the bot
* `matrix_registration_bot_system_user` the username of the system user to run the bot as (will be created)
* `matrix_client_api_endpoint` the Matrix client API base url to access (to access the `/_matrix/client/` endpoints)
* `matrix_registration_bot_username` the Matrix username to identify as
* `matrix_registration_bot_token` the Matrix bot user's authentication token
* `synapse_api_endpoint` the Synapse server API base url (to access the `/_synapse/admin/` endpoints)
* `synapse_admin_token` the access token of an administrative user
