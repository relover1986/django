#%%
import json
import requests
from django.core.management.base import BaseCommand
from pywebpush import webpush
from app01.models import PushSubscription

import os
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'mailto:admin@bxks.online')


class Command(BaseCommand):
    help = "发送 PWA 推送通知到所有订阅者"

    def add_arguments(self, parser):
        parser.add_argument("--title", type=str, default="辽宁捷祥")
        parser.add_argument("--body", type=str, default="您有新消息")
        parser.add_argument("--url", type=str, default="/")
        parser.add_argument("--icon", type=str, default="/static/pwa/icon-192x192.png")
        parser.add_argument("--dry-run", action="store_true", dest="dry_run")

    def handle(self, *args, **options):
        title = options["title"]
        body = options["body"]
        url = options["url"]
        icon = options["icon"]
        dry_run = options["dry_run"]

        subscriptions = PushSubscription.objects.all()
        sent = 0
        failed = 0
        deleted = 0

        for sub in subscriptions:
            try:
                if dry_run:
                    self.stdout.write(f"[DRY-RUN] {sub.endpoint[:50]}...")
                    continue

                payload = {"title": title, "body": body, "icon": icon, "url": url}

                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=json.dumps(payload),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_public_key=VAPID_PUBLIC_KEY,
                    vapid_claims={"sub": VAPID_CLAIMS_EMAIL},
                )

                sent += 1
                self.stdout.write(f"✓ {sub.endpoint[:50]}...")

            except requests.exceptions.RequestException as e:
                if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                    sub.delete()
                    deleted += 1
                    self.stdout.write(f"✗ 已过期，已删除: {sub.endpoint[:50]}...")
                else:
                    failed += 1
                    self.stdout.write(f"✗ 错误: {e}")
                continue
            except Exception as e:
                failed += 1
                self.stdout.write(f"✗ 异常: {e}")
                continue

        self.stdout.write(
            self.style.SUCCESS(f"=== 汇总: 已发送 {sent} 条，失败 {failed} 条，已删除 {deleted} 条 ===")
        )
