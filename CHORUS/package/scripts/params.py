from resource_management import Script

allConfigurations = Script.get_config()


config = allConfigurations['configurations']['installation-config']

TERMS_ACCEPTED = config['chorus.termsaccepted'] == 'yes'
SECURITY_SALT = '' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt']

INSTALLER_PATH = config['chorus.installation.installerpath']
INSTALLATION_DIRECTORY = config['chorus.installation.directory']
DATA_DIRECTORY = config['chorus.installation.datadirectory']
