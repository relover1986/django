"""
URL configuration for lnjx2025 project.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import re_path
from django.views.static import serve
from schema_graph.views import Schema
from lnjx2025.urls_tail import architecture_diagram_view, kanban_view, mine_safety_checklist_view
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
    path('home/quiz/', include('quiz_platform.urls')),

    # Info Collect
    path('', include('app01.urls.info_collect')),

    # PWA
    path('', include('app01.urls.pwa')),

    # DB Schema (schematic package broken, disabled)
    # path('schema-db/', include('schematic.urls')),

    # API
    path('api/', include('app01.api_urls')),

    # Fallback app01.urls (currently empty)
    path('', include('app01.urls')),

    # Schema ER 图
    # Architecture diagram
    path('arch/', architecture_diagram_view),
    path('kanban/', kanban_view),
    path('mine-safety/', mine_safety_checklist_view),
    path('schema/', Schema.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.shortcuts import render
def page_not_found(request, exception):
    return render(request, '404.html', status=404)

handler404 = page_not_found
