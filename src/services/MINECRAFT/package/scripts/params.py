from resource_management.libraries.functions.default import default
from resource_management import *
import utilities
from os import path

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

eula_accepted = default('/configurations/minecraft-env/accept_eula', 'false')
minecraft_user = default('/configurations/minecraft-env/minecraft_user', 'minecraft')
installation_path = default('/configurations/minecraft-env/installation_path', '/srv/minecraft')
installation_source = default('/configurations/minecraft-env/installation_source', None)
minimum_ram = default('/configurations/minecraft-env/minimum_ram', '1024M')
maximum_ram = default('/configurations/minecraft-env/maximum_ram', '2048M')

permissions = default('/configurations/minecraft-permissions/minecraft_permissions', None)

minecraft_password = default('/configurations/minecraft-env/admin_password', None)
hashed_minecraft_password = utilities.crypt_password(minecraft_password)
