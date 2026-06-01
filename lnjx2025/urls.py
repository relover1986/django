"""
URL configuration for lnjx2025 project.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import re_path
from django.views.static import serve
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = [
    path('', lambda request: redirect('/login/')),

    re_path(r'^.well-known/acme-challenge/(?P<path>.*)$', serve, {
        'document_root': os.path.join(BASE_DIR, '.well-known/acme-challenge'),
    }),

    # Auth
    path('', include('app01.urls.auth')),

    # Home
    path('', include('app01.urls.home')),

    # Staff management
    path('', include('app01.urls.staff')),

    # Contract labor
    path('', include('app01.urls.contract_labor')),

    # Mine card
    path('', include('app01.urls.mine_card')),

    # Photo management
    path('', include('app01.urls.photo')),

    # Blasting site
    path('', include('app01.urls.blasting_site')),

    # Blasting certificate
    path('', include('app01.urls.blasting_certificate')),

    # Blasting stats
    path('', include('app01.urls.blasting_stats')),

    # ID card
    path('', include('app01.urls.idcard')),

    # Explosive staff
    path('', include('app01.urls.explosive_staff')),

    # Other CRUD
    path('', include('app01.urls.other')),

    # Quiz
    path('', include('app01.urls.quiz')),

    # PWA
    path('', include('app01.urls.pwa')),

    # API
    path('api/', include('app01.api_urls')),

    # Fallback app01.urls (currently empty)
    path('', include('app01.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
