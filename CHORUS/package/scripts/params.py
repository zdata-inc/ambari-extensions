from resource_management import Script

config = Script.get_config()['configurations']['installation-config']

TERMS_ACCEPTED = config['chorus.termsaccepted'] == 'yes'
SECURITY_SALT = '' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt']

INSTALLER_PATH = config['chorus.installation.installerpath']
INSTALLATION_DIRECTORY = config['chorus.installation.directory']
DATA_DIRECTORY = config['chorus.installation.datadirectory']
