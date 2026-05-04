#%% 批量身份证 OCR 完整流水线（Windows 服务器版）
import os, sys, math, cv2
import numpy as np
from PIL import Image
from microwink import SegModel
import onnxruntime as ort
from rapidocr_onnxruntime.ch_ppocr_v3_det.text_detect import TextDetector

# ========== 模型路径 ==========
_MODEL_DIR = os.path.expanduser("~/.hermes/models")
SEG_PATH = os.path.join(_MODEL_DIR, "seg_model.onnx")
DET_PATH = os.path.join(_MODEL_DIR, "det.onnx")
REC_PATH = os.path.join(_MODEL_DIR, "rec.onnx")
CLS_PATH = os.path.join(_MODEL_DIR, "cls.onnx")
for p in [SEG_PATH, DET_PATH, REC_PATH, CLS_PATH]:
    assert os.path.exists(p), f"模型文件不存在: {p}"

# ========== ① split ==========
def find_balance_split_line(mask, thresh=0.5, step=2, min_ratio=0.15):
    h, w = mask.shape
    binary = (mask > thresh).astype(np.uint8)
    total_pixels = np.sum(binary)
    min_side_pixels = total_pixels * min_ratio
    valid = []
    for y in range(0, h, step):
        up_pixels = np.sum(binary[:y, :])
        down_pixels = np.sum(binary[y:, :])
        if up_pixels >= min_side_pixels and down_pixels >= min_side_pixels:
            valid.append((y, np.sum(binary[y, :])))
    if not valid:
        return h // 2
    return min(valid, key=lambda x: x[1])[0]

def split_smart(img, thresh=240, min_ratio=0.15):
    h = img.shape[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, thresh, 1, cv2.THRESH_BINARY_INV)
    total_pixels = np.sum(binary)
    min_side = total_pixels * min_ratio
    # ① 找拼缝
    row_sum = np.sum(binary, axis=1)
    seam_y = int(h * 0.2) + int(np.argmin(row_sum[int(h*0.2):int(h*0.8)]))
    up_pixels = np.sum(binary[:seam_y, :])
    down_pixels = np.sum(binary[seam_y:, :])
    if up_pixels >= min_side and down_pixels >= min_side:
        split_y = seam_y
        method = "seam"
    else:
        split_y = find_balance_split_line(binary)
        method = "balance"
    return img[:split_y], img[split_y:], split_y, method

# ========== ③ microwink ==========
def microwink_crop(img_cv, seg, tw=856, th=540):
    cards = seg.apply(Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)))
    if not cards: return None
    mask = (cards[0].mask > 0.5).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return None
    cnt = max(cnts, key=cv2.contourArea)
    approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True).reshape(4, 2)
    pts = sorted(approx, key=lambda x: (x[1], x[0]))
    if pts[0][0] > pts[1][0]: pts[0], pts[1] = pts[1], pts[0]
    if pts[2][0] > pts[3][0]: pts[2], pts[3] = pts[3], pts[2]
    src = np.array([pts[0], pts[1], pts[3], pts[2]], dtype=np.float32)
    dst = np.array([[0, 0], [tw, 0], [tw, th], [0, th]], dtype=np.float32)
    return cv2.warpPerspective(img_cv, cv2.getPerspectiveTransform(src, dst), (tw, th),
                                borderMode=cv2.BORDER_REPLICATE)

def rotate_crop(img, points):
    w = int(max(np.linalg.norm(points[0]-points[1]), np.linalg.norm(points[2]-points[3])))
    h = int(max(np.linalg.norm(points[0]-points[3]), np.linalg.norm(points[1]-points[2])))
    M = cv2.getPerspectiveTransform(points.astype(np.float32),
        np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32))
    return cv2.warpPerspective(img, M, (w,h), borderMode=cv2.BORDER_REPLICATE)

# ========== 模型类 ==========
class ClsModel:
    def __init__(self, path):
        self.s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        self.imgH, self.imgW, self.thresh = 48, 192, 0.9
    def resize(self, img):
        h, w = img.shape[:2]
        rw = self.imgW if math.ceil(self.imgH*w/h) > self.imgW else int(math.ceil(self.imgH*w/h))
        n = cv2.resize(img, (rw, self.imgH)).astype("float32").transpose(2,0,1)/255
        n = (n-0.5)/0.5
        p = np.zeros((3, self.imgH, self.imgW), dtype=np.float32)
        p[:,:,:rw] = n
        return p
    def predict(self, crop):
        prob = self.s.run(None, {"x": self.resize(crop)[np.newaxis,:].astype(np.float32)})[0]
        return float(prob[0][0]), float(prob[0][1])
    def orient_page(self, img, det):
        dt_boxes, _ = det(img)
        if dt_boxes is None or len(dt_boxes) == 0:
            return img, False
        flipped = 0
        for box in dt_boxes:
            crop = rotate_crop(img, box)
            p0, p1 = self.predict(crop)
            if p1 >= self.thresh: flipped += 1
        if flipped > len(dt_boxes) // 2:
            return cv2.rotate(img, cv2.ROTATE_180), True
        return img, False
    def __call__(self, crop):
        prob = self.s.run(None, {"x": self.resize(crop)[np.newaxis,:].astype(np.float32)})[0]
        return cv2.rotate(crop, cv2.ROTATE_180) if prob[0][1] >= self.thresh else crop

class RecModel:
    def __init__(self, path):
        self.s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        meta = self.s.get_modelmeta().custom_metadata_map
        self.chars = ["blank"] + meta["character"].splitlines() + [" "]
        self.imgH = 48
    def __call__(self, img_list):
        if not img_list: return []
        ws = [i.shape[1]/i.shape[0] for i in img_list]
        idx = np.argsort(ws)
        res = [("", 0.0)] * len(img_list)
        for b in range(0, len(img_list), 6):
            bi = idx[b:min(len(img_list), b+6)]
            mw = max(max(ws[i] for i in bi), 320/48)
            iw = int(48*mw)
            batch = []
            for i in bi:
                rw = min(iw, int(math.ceil(48*img_list[i].shape[1]/img_list[i].shape[0])))
                n = cv2.resize(img_list[i], (rw, 48)).astype("float32").transpose(2,0,1)/255
                n = (n-0.5)/0.5
                p = np.zeros((3,48,iw), dtype=np.float32)
                p[:,:,:rw] = n
                batch.append(p[np.newaxis,:])
            preds = self.s.run(None, {"x": np.concatenate(batch).astype(np.float32)})[0]
            for rno in range(preds.shape[0]):
                ix, pr = preds[rno].argmax(1), preds[rno].max(1)
                cs, cn, pv = [], [], -1
                for j, cid in enumerate(ix):
                    if cid != 0 and cid != pv:
                        cs.append(self.chars[cid] if cid < len(self.chars) else "")
                        cn.append(float(pr[j]))
                    pv = int(cid)
                res[bi[rno]] = ("".join(cs), np.mean(cn) if cn else 0.0)
        return res

# ========== OCR单张 ==========
def ocr_half(img, det, rec, cls_model):
    dt_boxes, _ = det(img)
    if dt_boxes is None or len(dt_boxes) == 0:
        return []
    crop_list = [cls_model(rotate_crop(img, box)) for box in dt_boxes]
    rec_res = rec(crop_list)
    sboxes = sorted(enumerate(dt_boxes), key=lambda x: (x[1][0][1], x[1][0][0]))
    lines = [(rec_res[i][0], rec_res[i][1]) for i, box in sboxes
             if rec_res[i][1] >= 0.5 and rec_res[i][0].strip()]
    return lines

def determine_side(upper_text, lower_text):
    renyi_keywords = ["姓名", "公民身份号码"]
    upper_is_renyi = any(kw in upper_text for kw in renyi_keywords)
    lower_is_renyi = any(kw in lower_text for kw in renyi_keywords)
    if upper_is_renyi:
        return "上", "下"
    elif lower_is_renyi:
        return "下", "上"
    return "上", "下"

# ========== 批量处理 ==========
def process_batch(image_paths, out_dir="身份证结果"):
    os.makedirs(out_dir, exist_ok=True)
    seg = SegModel.from_path(SEG_PATH)
    det = TextDetector({"model_path": DET_PATH, "use_cuda": False, "limit_side_len": 736, "limit_type": "min",
        "std":[0.5]*3,"mean":[0.5]*3,"thresh":0.3,"box_thresh":0.5,"use_dilation":True,"score_mode":"fast"})
    rec = RecModel(REC_PATH)
    cls_model = ClsModel(CLS_PATH)

    all_data = {}
    for img_path in image_paths:
        base = os.path.splitext(os.path.basename(img_path))[0]
        img = cv2.imread(img_path)
        if img is None:
            print(f"  ⚠️ 无法读取: {img_path}")
            continue
        print(f"\n=== {base} ===")

        # ① split
        top, bottom, y, method = split_smart(img)
        print(f"split y={y} ({method})")

        # ② microwink + 方向修正
        halves = {}
        for side, half in [("上", top), ("下", bottom)]:
            cropped = microwink_crop(half, seg)
            if cropped is None:
                print(f"  {side}半: microwink 未检测到"); continue
            cropped, _ = cls_model.orient_page(cropped, det)
            halves[side] = cropped

        if "上" not in halves or "下" not in halves:
            print("  ⚠️ 缺一半，跳过"); continue

        # ③ OCR后内容判断
        ocr_results = {}
        for side_name in ["上", "下"]:
            lines = ocr_half(halves[side_name], det, rec, cls_model)
            text = " ".join(t for t, s in lines)
            ocr_results[side_name] = {"lines": lines, "text": text}

        renyi_side, guohui_side = determine_side(
            ocr_results["上"]["text"], ocr_results["下"]["text"])
        print(f"  判断: 人像面={renyi_side}半, 国徽面={guohui_side}半")

        # ④ 输出
        results = {}
        for i, (side_name, label) in enumerate([
            (renyi_side, "人像面"), (guohui_side, "国徽面")
        ]):
            cropped = halves[side_name]
            lines = ocr_results[side_name]["lines"]
            cv2.imwrite(os.path.join(out_dir, f"{base}_{label}.jpg"), cropped)
            results[label] = lines
            for t, s in lines:
                print(f"    [{s:.1%}] {t}")
        all_data[base] = results

    with open(os.path.join(out_dir, "ocr结果.txt"), "w", encoding="utf-8") as f:
        for base, sides in all_data.items():
            f.write(f"=== {base} ===\n")
            for side in ["人像面", "国徽面"]:
                f.write(f"--- {side} ---\n")
                for t,s in sides.get(side, []):
                    f.write(f"  {t} ({s:.1%})\n")
                f.write("\n")
    print(f"\n✅ 全部完成，结果保存至: {out_dir}")
    return all_data

if __name__ == "__main__":
    import glob
    images = sorted(glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.jpeg"))
    if not images:
        print("当前目录下没有图片文件，请将身份证图片放到此目录")
        print("支持的格式: .jpg .png .jpeg")
        print(f"\n脚本所在目录: {os.getcwd()}")
        print(f"模型目录: {_MODEL_DIR}")
        sys.exit(1)
    print(f"找到 {len(images)} 张图片")
    process_batch(images[:10])
