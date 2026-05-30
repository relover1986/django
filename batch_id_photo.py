#%% 一寸照批量处理 — RetinaFace 人脸对齐
from PIL import Image as PILImage
import os, sys, glob, cv2, tempfile
import numpy as np
from retinaface import RetinaFace

# 目标参数（一寸照 295×413）
TARGET_LEFT_EYE  = (110, 160)   # 照片左侧的眼
TARGET_RIGHT_EYE = (185, 160)   # 照片右侧的眼
TARGET_EYE_DIST  = 70
OUTPUT_SIZE      = (295, 413)

def _scale_fit(img, out_size):
    """原图按比例缩放到 output_size 内，居中，白底填充"""
    h, w = img.shape[:2]
    tw, th = out_size
    scale = min(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((th, tw, 3), 255, dtype=np.uint8)
    x = (tw - nw) // 2
    y = (th - nh) // 2
    canvas[y:y+nh, x:x+nw] = resized
    return canvas

def _has_blank_edges(img, threshold=10, bright=245):
    """检测图像四边是否有大面积空白（黑色或白色）"""
    h, w = img.shape[:2]
    edge_pixels = np.concatenate([
        img[0, :], img[h-1, :], img[:, 0], img[:, w-1],
    ])
    is_dark = np.all(edge_pixels < threshold, axis=1)
    is_bright = np.all(edge_pixels > bright, axis=1)
    return np.mean(is_dark | is_bright) > 0.15

def align_photo_cv(img_path: str):
    """检测人脸，鼻子判180°倒置，双眼水平+缩放70px+裁295×413"""
    img = cv2.imread(img_path)
    if img is None:
        return None

    temp_path = img_path + ".tmp_detect.jpg"
    cv2.imwrite(temp_path, img)
    resp = RetinaFace.detect_faces(temp_path)
    os.remove(temp_path)
    if not resp:
        return None

    face = list(resp.values())[0]
    lm = face["landmarks"]
    le = np.array(lm["left_eye"], dtype=np.float32)
    re = np.array(lm["right_eye"], dtype=np.float32)
    nose = np.array(lm.get("nose", [0, 0]), dtype=np.float32)

    # 交换使左眼在照片左侧
    if le[0] > re[0]:
        le, re = re, le

    # arctan2 自动处理任意倾斜角，鼻子只判 180° 倒置
    angle = np.degrees(np.arctan2(re[1] - le[1], re[0] - le[0]))
    if nose[1] < min(le[1], re[1]) - 10:
        angle += 180

    # 缩放到眼距 70px，裁到 295×413
    eye_center = (le + re) / 2.0
    orig_dist = np.linalg.norm(re - le)
    scale = TARGET_EYE_DIST / orig_dist
    rot_mat = cv2.getRotationMatrix2D(
        (float(eye_center[0]), float(eye_center[1])), float(angle), float(scale)
    )
    target_center = np.mean([TARGET_LEFT_EYE, TARGET_RIGHT_EYE], axis=0)
    rot_mat[0, 2] += target_center[0] - eye_center[0]
    rot_mat[1, 2] += target_center[1] - eye_center[1]

    aligned = cv2.warpAffine(img, rot_mat, OUTPUT_SIZE, flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return aligned

def align_photo(img_path: str) -> PILImage.Image:
    """对外总接口：对齐后返回 PIL Image (RGB, 295×413)。
    黑边或无人脸时直接返回原图（不缩放、不处理），避免影响后续抠图。
    """
    aligned = align_photo_cv(img_path)
    if aligned is not None and not _has_blank_edges(aligned):
        return PILImage.fromarray(cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB))

    # 黑边或无人脸 → 直接返回原图，不处理
    return PILImage.open(img_path).convert("RGB")

def process_image(img_path, out_path):
    """批量处理：对齐并保存。黑边或无人脸时直接复制原图。"""
    aligned = align_photo_cv(img_path)
    if aligned is not None and not _has_blank_edges(aligned):
        cv2.imwrite(out_path, aligned)
        print(f"   ✅ {os.path.basename(img_path)}")
        return True

    # 降级：直接复制原图（不缩放不处理）
    import shutil
    shutil.copy2(img_path, out_path)
    reason = "未检测到人脸" if aligned is None else "对齐后出现黑边"
    print(f"   ⚠️  {os.path.basename(img_path)} {reason}，已复制原图")
    return True

def main():
    if len(sys.argv) != 3:
        print("用法: python3 batch_id_photo.py <输入目录> <输出目录>")
        sys.exit(1)

    in_dir  = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    exts = ("*.jpg", "*.jpeg", "*.png")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(in_dir, "**", ext), recursive=True))
    skip_dirs = ["/venv/", "/out/", "/一寸照输出/"]
    files = [f for f in files if not any(d in f for d in skip_dirs)]

    if not files:
        print("输入目录中没有图片")
        return

    print(f"处理 {len(files)} 张图片...")
    ok = 0
    for f in files:
        name = os.path.basename(f)
        root, ext = os.path.splitext(name)
        out_path = os.path.join(out_dir, root + "_70" + ext)
        r = process_image(f, out_path)
        if r:
            ok += 1

    print(f"\n完成：{ok}/{len(files)} 成功")

if __name__ == "__main__":
    main()
