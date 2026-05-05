import urllib.request
import json

# 1. Test login page
r = urllib.request.urlopen('http://127.0.0.1:8001/login/')
print('LOGIN: %d %d bytes' % (r.status, len(r.read())))

# 2. Test API users
r = urllib.request.urlopen('http://127.0.0.1:8001/api/users/')
body = r.read().decode('utf-8')
print('API_USERS: %d' % r.status)
if body.startswith('{'):
    data = json.loads(body)
    results = data.get('results', [])
    print('  JSON, %d users, keys: %s' % (len(results), list(data.keys())[:5]))
elif body.startswith('['):
    data = json.loads(body)
    print('  JSON list, %d items' % len(data))
else:
    print('  NOT JSON: %s' % body[:200])

# 3. Test API idcards
r = urllib.request.urlopen('http://127.0.0.1:8001/api/idcards/')
body = r.read().decode('utf-8')
print('API_IDCARDS: %d' % r.status)
if body.startswith('{') or body.startswith('['):
    data = json.loads(body)
    print('  JSON OK')
else:
    print('  NOT JSON: %s' % body[:200])

# 4. Test API login-records
r = urllib.request.urlopen('http://127.0.0.1:8001/api/login-records/')
body = r.read().decode('utf-8')
print('API_LOGIN_RECORDS: %d' % r.status)
if body.startswith('{') or body.startswith('['):
    data = json.loads(body)
    print('  JSON OK')
else:
    print('  NOT JSON: %s' % body[:200])
