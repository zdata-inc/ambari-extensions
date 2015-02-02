from resource_management import *
import os

config = Script.get_config()['configurations']['installation-config']

termsAccepted = config['chorus.termsaccepted'] == 'yes'
securitySalt = '' if config['chorus.security.salt'] == 'generate' else config['chorus.security.salt']

installerPath = config['chorus.installation.installerpath']
installationDirectory = config['chorus.installation.directory']
dataDirectory = config['chorus.installation.datadirectory']
