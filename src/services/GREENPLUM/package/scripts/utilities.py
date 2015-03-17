import os
import json

def _lines_contain(haystack, needle):
    for line in haystack:
        if line.strip() == needle.strip():
            return True

    return False

def append_bash_profile(user, to_be_appended, run=False, allow_duplicates=False):
    bashrc = "/home/%s/.bashrc" % user
    command = json.dumps(to_be_appended)[1:-1]

    with open(bashrc, 'a+') as filehandle:
        if not _lines_contain(filehandle.readlines(), command) or allow_duplicates:
            print "Appending " + command
            filehandle.write(format("{to_be_appended}\n"))

    if run:
        Execute(to_be_appended)

def call(*argv, **kwargs):
    def call_fn(fn):
        return fn(*argv, **kwargs)
    return call_fn
