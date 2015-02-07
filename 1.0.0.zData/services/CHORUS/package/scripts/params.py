from resource_management import Script

allConfigurations = Script.get_config()


config = allConfigurations['configurations']['chorus-env']

TERMS_ACCEPTED = config['chorus.termsaccepted'] == 'yes'
SECURITY_SALT = '' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt']

INSTALLER_PATH = config['chorus.installation.installerpath']
INSTALLATION_DIRECTORY = config['chorus.installation.directory']
DATA_DIRECTORY = config['chorus.installation.datadirectory']

SERVER_PORT = config['chorus.server.port']
SERVER_TIMEOUT = config['chorus.server.timeout']
DEFAULT_PREVIEW_ROW_LIMIT = config['chorus.server.defaultpreviewrowlimit']
EXECUTION_TIMEOUT = config['chorus.server.executiontimeout']
LOG_LEVEL = config['chorus.server.loglevel']
MAIL_ENABLED = config['chorus.server.mailenabled']