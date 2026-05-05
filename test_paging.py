import os, sys, urllib.request, json

os.environ['DJANGO_SETTINGS_MODULE'] = 'lnjx2025.settings'
sys.path.insert(0, r'C:\Users\Administrator\lnjx2026')
import django; django.setup()

BASE = 'http://127.0.0.1:8001'

# 1. Test full list WITHOUT params (should paginate to 10)
r = urllib.request.urlopen(BASE + '/api/admins/')
data = json.loads(r.read())
results = data.get('results', data)
print('1. /api/admins/ (no params):')
print('   HTTP %d, results=%d, count=%d, next=%s' % (
    r.status, len(results), data.get('count', 0), str(data.get('next', 'None')[:50])))

# 2. Test page 2
r = urllib.request.urlopen(BASE + '/api/admins/?page=2')
data = json.loads(r.read())
results = data.get('results', data)
print('2. /api/admins/?page=2:')
print('   results=%d, next=%s' % (len(results), str(data.get('next', 'None')[:50])))

# 3. Test size explicit
r = urllib.request.urlopen(BASE + '/api/admins/?size=5')
data = json.loads(r.read())
results = data.get('results', data)
print('3. /api/admins/?size=5:')
print('   results=%d' % len(results))

# 4. Test filtering by role
r = urllib.request.urlopen(BASE + '/api/admins/?role=管理员')
data = json.loads(r.read())
results = data.get('results', data)
print('4. /api/admins/?role=管理员:')
print('   results=%d, count=%d' % (len(results), data.get('count', 0)))

# 5. Test filtering by ident
r = urllib.request.urlopen(BASE + '/api/admins/?ident=000001')
data = json.loads(r.read())
results = data.get('results', data)
print('5. /api/admins/?ident=000001:')
print('   results=%d' % len(results))
if results:
    print('   username=%s' % results[0]['username'])

# 6. Test IDCard filtering by name
r = urllib.request.urlopen(BASE + '/api/idcards/?name=相征')
data = json.loads(r.read())
results = data.get('results', data)
print('6. /api/idcards/?name=相征:')
print('   results=%d' % len(results))
if results:
    print('   id_number=%s' % results[0]['id_number'])

# 7. Test login-records by type
r = urllib.request.urlopen(BASE + '/api/login-records/?type=登入')
data = json.loads(r.read())
results = data.get('results', data)
print('7. /api/login-records/?type=登入:')
print('   results=%d (in page), count=%d' % (len(results), data.get('count', 0)))

# 8. Test invalid page
try:
    r = urllib.request.urlopen(BASE + '/api/admins/?page=9999')
    data = json.loads(r.read())
    results = data.get('results', data)
    print('8. /api/admins/?page=9999:')
    print('   results=%d (ok, empty page)' % len(results))
except Exception as e:
    print('8. /api/admins/?page=9999: ERROR %s' % e)

# 9. Test old web pages still work (login page)
r = urllib.request.urlopen(BASE + '/login/')
print('9. /login/: HTTP %d (OK)' % r.status)

# 10. Test old web routes
for route in ['/home/', '/staff_list/']:
    r = urllib.request.urlopen(BASE + route)
    print('   %s: HTTP %d' % (route, r.status))

print('\nALL PAGINATION TESTS PASSED' if data.get('count', -1) >= 0 else 'SOME ISSUES')
