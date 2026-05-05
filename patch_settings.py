"""Add django_filters to INSTALLED_APPS and configure DRF pagination + filtering"""
import pathlib

p = pathlib.Path(r'C:\Users\Administrator\lnjx2026\lnjx2025\settings.py')
content = p.read_text(encoding='utf-8')

# Add django_filters to INSTALLED_APPS
old = "    'rest_framework', \n]"
new = "    'rest_framework',\n    'django_filters',\n]"
if old in content:
    content = content.replace(old, new)
    print('Added django_filters to INSTALLED_APPS')

# Update REST_FRAMEWORK config with pagination + filtering
old_rf = "REST_FRAMEWORK = {\n    'DEFAULT_RENDERER_CLASSES': [\n        'rest_framework.renderers.JSONRenderer',\n        'rest_framework.renderers.BrowsableAPIRenderer',\n    ],\n    'DEFAULT_PERMISSION_CLASSES': [\n        'rest_framework.permissions.AllowAny',\n    ],\n    'DEFAULT_AUTHENTICATION_CLASSES': [\n    ]\n}"
new_rf = """REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'MAX_PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}"""
if old_rf in content:
    content = content.replace(old_rf, new_rf)
    print('Updated REST_FRAMEWORK config with pagination + filtering')
else:
    print('WARN: pattern not found, check content')

p.write_text(content, encoding='utf-8')
print('Done')
