import string
import random

def crypt_password(plaintext):
    import crypt
    salt = '$6$' + create_salt() + '$'
    return crypt.crypt(plaintext, salt)

def create_salt():
    output = ""
    for i in range(16):
        output += random.choice(string.letters + string.digits)
    return output
