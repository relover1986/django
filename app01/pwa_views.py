#%%
"""PWA views: manifest, sw.js, push subscription"""
import json
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import PushSubscription
import logging

logger = logging.getLogger(__name__)

import os
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'mailto:admin@bxks.online')


def manifest_json(request):
    manifest = {
        "name": "\u8fbd\u5b81\u6377\u7965\u4fe1\u606f\u7ba1\u7406\u7cfb\u7edf",
        "short_name": "\u6377\u7965\u7cfb\u7edf",
        "description": "\u8fbd\u5b81\u6377\u7965\u4fe1\u606f\u7ba1\u7406\u7cfb\u7edf - \u6c11\u7206\u884c\u4e1a\u4fe1\u606f\u5316\u7ba1\u7406\u5e73\u53f0",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#198754",
        "theme_color": "#198754",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/pwa/icon-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/pwa/icon-512x512.png", "sizes": "512x512", "type": "image/png"}
        ],
        "categories": ["business", "productivity"],
        "prefer_related_applications": False
    }
    return JsonResponse(manifest)


def service_worker(request):
    sw_path = settings.BASE_DIR / "static" / "sw.js"
    with open(sw_path, "r") as f:
        return HttpResponse(f.read(), content_type="application/javascript")


@csrf_exempt
def push_subscribe(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body)
        endpoint = data.get("endpoint")
        keys = data.get("keys", {})
        p256dh = keys.get("p256dh", "")
        auth = keys.get("auth", "")
        if not endpoint:
            return JsonResponse({"error": "endpoint required"}, status=400)
        sub, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={"p256dh": p256dh, "auth": auth,
                      "user_agent": request.META.get("HTTP_USER_AGENT", "")}
        )
        return JsonResponse({"status": "created" if created else "updated"})
    except Exception as e:
        logger.error(f"Push subscribe error: {e}")
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def push_unsubscribe(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body)
        endpoint = data.get("endpoint")
        if endpoint:
            PushSubscription.objects.filter(endpoint=endpoint).delete()
        return JsonResponse({"status": "deleted"})
    except Exception as e:
        logger.error(f"Push unsubscribe error: {e}")
        return JsonResponse({"error": str(e)}, status=400)


def push_public_key(request):
    return JsonResponse({"publicKey": VAPID_PUBLIC_KEY})
