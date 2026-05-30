#%% Fix mine_card_update_photo to add align_photo
import re, os

views_path = "/root/django/app01/views.py"

with open(views_path, "r") as f:
    content = f.read()

old = '''def mine_card_update_photo(request, worker_id):
    """单行上传照片"""
    worker = get_object_or_404(models.Worker, id=worker_id)
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES, instance=worker)
        if form.is_valid():
            form.save()
    return redirect("mine_card_index")'''

new = '''def mine_card_update_photo(request, worker_id):
    """单行上传照片（上传时自动 retina-face 人脸对齐）"""
    worker = get_object_or_404(models.Worker, id=worker_id)
    if request.method == "POST":
        # --- 上传时自动 retina-face 人脸对齐 ---
        if "photo" in request.FILES:
            from django.core.files.uploadedfile import InMemoryUploadedFile
            from batch_id_photo import align_photo
            import tempfile

            uploaded = request.FILES["photo"]
            file_content = uploaded.read()

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                aligned = align_photo(tmp_path)
                buf = io.BytesIO()
                aligned.save(buf, format="JPEG", quality=95)
                buf.seek(0)
                request.FILES["photo"] = InMemoryUploadedFile(
                    buf, "photo", uploaded.name, uploaded.content_type,
                    buf.getbuffer().nbytes, None
                )
            finally:
                os.unlink(tmp_path)

        form = PhotoForm(request.POST, request.FILES, instance=worker)
        if form.is_valid():
            form.save()
    return redirect("mine_card_index")'''

if old in content:
    content = content.replace(old, new)
    with open(views_path, "w") as f:
        f.write(content)
    print("mine_card_update_photo fixed")
else:
    print("Original function not found - checking other versions...")
    # debug: show what's around that line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'mine_card_update_photo' in line:
            for j in range(max(0,i-1), min(len(lines), i+15)):
                print(f"{j+1}: {lines[j]}")
            break
