from resource_management import Script

config = Script.get_config()['configurations']

TERMS_ACCEPTED = config['chorus-env']['chorus.termsaccepted'] == 'yes'
SECURITY_SALT = '' if config['chorus-env']['chorus.security.salt'] == 'generate' else config['chorus-env']['chorus.security.salt']

INSTALLER_PATH = config['chorus-env']['chorus.installation.installerpath']
INSTALLATION_DIRECTORY = config['chorus-env']['chorus.installation.directory']
DATA_DIRECTORY = config['chorus-env']['chorus.installation.datadirectory']

SERVER_PORT = config['chorus-env']['chorus.server.port']
SERVER_TIMEOUT = config['chorus-env']['chorus.server.timeout']
DEFAULT_PREVIEW_ROW_LIMIT = config['chorus-env']['chorus.server.defaultpreviewrowlimit']
EXECUTION_TIMEOUT = config['chorus-env']['chorus.server.executiontimeout']
LOG_LEVEL = config['chorus-env']['chorus.server.loglevel']
MAIL_ENABLED = config['chorus-env']['chorus.server.mailenabled']

minimum_memory = '512M'
maximum_memory = '2048M'

# minimum_memory = config['chorus-tuning']['chorus.minimum_memory']
# maximum_memory = config['chorus-tuning']['chorus.maximum_memory']