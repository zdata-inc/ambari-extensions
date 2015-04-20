from __future__ import with_statement
import os
import random
import string

from resource_management import *
from textwrap import dedent

def append_bash_profile(user, to_be_appended, run=False, allow_duplicates=False):
    """Append a given line to a user's bashrc file.

    user -- The user whose bashrc file will have the given line appended to it.
    to_be_appended -- Line to append to the bashrc file.
    run -- Should the line also be executed?
    allow_duplicates -- If the line already exists in the file, should it be appended anyways?  Whitespace is ignored.
    """

    bashrc = "/home/%s/.bashrc" % user

    with open(bashrc, 'a+') as filehandle:
        if to_be_appended.strip() not in map(lambda line: line.strip(), filehandle.readlines()) or allow_duplicates:
            Logger.info(format("Appending {to_be_appended} to {bashrc}"))
            filehandle.write(format("{to_be_appended}\n"))

    if run:
        Execute(to_be_appended, user=user

