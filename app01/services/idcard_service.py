"""身份证OCR服务 - 图片回正、OCR识别、双面合成"""
import io
import cv2
import numpy as np
from PIL import Image
from app01.func import sfz, combine_a4_images


def straighten_idcard(uploaded_file):
    """使用 microwink SegModel 回正身份证图片"""
    raw_bytes = uploaded_file.read()
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_cv is None:
        raise ValueError('图片解析失败')

    from microwink import SegModel
    seg = SegModel.from_path(os.path.expanduser('~/.hermes/models/seg_model.onnx'))
    cards = seg.apply(Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)))
    if cards:
        mask = (cards[0].mask > 0.5).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            cnt = max(cnts, key=cv2.contourArea)
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2)
                pts = sorted(pts, key=lambda x: (x[1], x[0]))
                if pts[0][0] > pts[1][0]:
                    pts[0], pts[1] = pts[1], pts[0]
                if pts[2][0] > pts[3][0]:
                    pts[2], pts[3] = pts[3], pts[2]
                src = np.array([pts[0], pts[1], pts[3], pts[2]], dtype=np.float32)
                dst = np.array([[0, 0], [856, 0], [856, 540], [0, 540]], dtype=np.float32)
                M = cv2.getPerspectiveTransform(src, dst)
                img_cv = cv2.warpPerspective(img_cv, M, (856, 540),
                                              borderMode=cv2.BORDER_REPLICATE)

    # cls 方向判别（检测180°翻转）
    try:
        import math
        import onnxruntime as ort
        from rapidocr_onnxruntime.ch_ppocr_det.text_detect import TextDetector

        _cls_path = r'C:\Users\Administrator\.hermes\models\cls.onnx'
        _det_path = r'C:\Users\Administrator\.hermes\models\det.onnx'

        if os.path.exists(_cls_path) and os.path.exists(_det_path):
            _det = TextDetector({
                "model_path": _det_path, "limit_side_len": 736,
                "limit_type": "min", "std": [0.5]*3, "mean": [0.5]*3,
                "thresh": 0.3, "box_thresh": 0.5, "use_dilation": True,
                "score_mode": "fast", "use_cuda": False,
            })
            _cls = ort.InferenceSession(_cls_path, providers=["CPUExecutionProvider"])

            def _rotate_crop(img, pts):
                w = int(max(np.linalg.norm(pts[0]-pts[1]), np.linalg.norm(pts[2]-pts[3])))
                h = int(max(np.linalg.norm(pts[0]-pts[3]), np.linalg.norm(pts[1]-pts[2])))
                M2 = cv2.getPerspectiveTransform(pts.astype(np.float32),
                    np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32))
                return cv2.warpPerspective(img, M2, (w,h), borderMode=cv2.BORDER_REPLICATE)

            def _cls_resize(crop, imgW=192, imgH=48):
                h, w = crop.shape[:2]
                rw = imgW if math.ceil(imgH*w/h) > imgW else int(math.ceil(imgH*w/h))
                n = cv2.resize(crop, (rw, imgH)).astype("float32").transpose(2,0,1)/255
                n = (n-0.5)/0.5
                p = np.zeros((3, imgH, imgW), dtype=np.float32)
                p[:,:,:rw] = n
                return p

            _boxes, _ = _det(img_cv)
            if _boxes is not None and len(_boxes) > 0:
                _flipped = 0
                for _box in _boxes:
                    _crop = _rotate_crop(img_cv, _box)
                    _prob = _cls.run(None, {"x": _cls_resize(_crop)[np.newaxis,:].astype(np.float32)})[0]
                    if _prob[0][1] >= 0.9:
                        _flipped += 1
                if _flipped > len(_boxes) // 2:
                    img_cv = cv2.rotate(img_cv, cv2.ROTATE_180)
    except Exception:
        pass

    img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    img_pil.save(buf, format='JPEG', quality=90)
    return buf.getvalue()


def ocr_idcard(front_file):
    """OCR识别身份证人像面，返回 (姓名, 身份证号码)"""
    return sfz(front_file)


def combine_images(img1, img2):
    """合成双面A4图片"""
    return combine_a4_images(img1, img2)
