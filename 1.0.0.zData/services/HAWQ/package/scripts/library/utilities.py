from resource_management import *
import json

def appendBashProfile(user, toBeAppended, run=False):
    Execute('echo % >> "/home/%s/.bashrc"' % json.dumps(toBeAppended), user)

    if run:
        Execute(toBeAppended)