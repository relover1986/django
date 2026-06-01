from django.urls import path
from app01.pwa_views import manifest_json, service_worker, push_subscribe, push_unsubscribe, push_public_key

urlpatterns = [
    path("manifest.json", manifest_json, name="manifest_json"),
    path("sw.js", service_worker, name="service_worker"),
    path("api/push/subscribe/", push_subscribe, name="push_subscribe"),
    path("api/push/unsubscribe/", push_unsubscribe, name="push_unsubscribe"),
    path("api/push/public-key/", push_public_key, name="push_public_key"),
]
