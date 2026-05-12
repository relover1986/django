import os, sys
sys.path.insert(0, "/root/django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lnjx2025.settings")
import django
django.setup()
from app01 import models

deleted = []
for obj in models.IDCard.objects.all():
    has_front = obj.front_image and obj.front_image.storage.exists(obj.front_image.name)
    has_back = obj.back_image and obj.back_image.storage.exists(obj.back_image.name)
    if not has_front or not has_back:
        deleted.append(obj.id)
        obj.delete()
        print("Deleted ID", obj.id, ":", obj.name, "-", obj.id_number)

print("Total deleted:", len(deleted))
print("Remaining:", models.IDCard.objects.count())
