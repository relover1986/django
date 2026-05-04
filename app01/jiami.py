import hashlib

def md5(str):
    salt='poxcc'
    obj=hashlib.md5(salt.encode('utf-8'))
    obj.update(str.encode('utf-8'))
    return obj.hexdigest()

