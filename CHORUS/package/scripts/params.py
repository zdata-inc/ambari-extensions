from resource_management import *
import os

config = Script.get_config()['configurations']['installation-config']

terms_accepted = config['chorus.termsaccepted'] == 'yes'
security_salt = '' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt']

installer_path = config['chorus.installation.installerpath']
installation_directory = config['chorus.installation.directory']
data_directory = config['chorus.installation.datadirectory']
