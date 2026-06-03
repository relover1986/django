"""身份证OCR服务 - 图片回正、OCR识别、双面合成"""
import io
import cv2
import numpy as np
from PIL import Image
from app01.photo import sfz, combine_a4_images


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

        _md = os.path.expanduser('~/.hermes/models')
        _cls_path = os.path.join(_md, 'cls.onnx')
        _det_path = os.path.join(_md, 'det.onnx')

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
        import traceback; traceback.print_exc()
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

def batch_process_idcard(image_bytes):
    """接收正反面拼图二进制 → AI分割/矫正/OCR → 返回 {name, id_number, front_image, back_image, combined_image}"""
    import tempfile, cv2, math, numpy as np, io, os, shutil
    from PIL import Image as PILImage
    from microwink import SegModel
    import onnxruntime as ort
    from rapidocr_onnxruntime.ch_ppocr_det.text_detect import TextDetector
    from django.core.files.base import ContentFile

    _md = os.path.expanduser('~/.hermes/models')
    for p in ['seg_model.onnx', 'det.onnx', 'rec.onnx', 'cls.onnx']:
        if not os.path.exists(os.path.join(_md, p)):
            return None

    segp = os.path.join(_md, 'seg_model.onnx')
    detp = os.path.join(_md, 'det.onnx')
    recp = os.path.join(_md, 'rec.onnx')
    clsp = os.path.join(_md, 'cls.onnx')

    td = tempfile.mkdtemp()
    try:
        ip = os.path.join(td, 'in.jpg')
        with open(ip, 'wb') as f:
            f.write(image_bytes)
        img = cv2.imread(ip)
        if img is None:
            return None

        # split_smart
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bi = cv2.threshold(gray, 240, 1, cv2.THRESH_BINARY_INV)
        tp = np.sum(bi)
        h = img.shape[0]
        sy = int(h*0.2)+int(np.argmin(np.sum(bi, axis=1)[int(h*0.2):int(h*0.8)]))
        up = np.sum(bi[:sy,:])
        dn = np.sum(bi[sy:,:])
        sp = sy if (up>=tp*0.15 and dn>=tp*0.15) else h//2
        tc, bc = img[:sp], img[sp:]

        # microwink crop (透视矫正)
        def _mcrop_img(im):
            cards = seg.apply(PILImage.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
            if not cards:
                return None
            mask = (cards[0].mask>0.5).astype(np.uint8)*255
            cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                return None
            ct = max(cnts, key=cv2.contourArea)
            ap = cv2.approxPolyDP(ct, 0.02*cv2.arcLength(ct,True),True).reshape(4,2)
            pts = sorted(ap, key=lambda x:(x[1],x[0]))
            if pts[0][0]>pts[1][0]: pts[0],pts[1]=pts[1],pts[0]
            if pts[2][0]>pts[3][0]: pts[2],pts[3]=pts[3],pts[2]
            src = np.array([pts[0],pts[1],pts[3],pts[2]], dtype=np.float32)
            dst = np.array([[0,0],[856,0],[856,540],[0,540]], dtype=np.float32)
            return cv2.warpPerspective(im, cv2.getPerspectiveTransform(src,dst),(856,540),
                                       borderMode=cv2.BORDER_REPLICATE)

        # models
        seg = SegModel.from_path(segp)
        _tc_crop = _mcrop_img(tc)
        if _tc_crop is not None:
            tc = _tc_crop
        _bc_crop = _mcrop_img(bc)
        if _bc_crop is not None:
            bc = _bc_crop
        det = TextDetector({'model_path':detp, 'use_cuda':False, 'limit_side_len':736,
            'limit_type':'min', 'std':[0.5]*3,'mean':[0.5]*3,'thresh':0.3,
            'box_thresh':0.5, 'use_dilation':True, 'score_mode':'fast'})
        cs = ort.InferenceSession(clsp, providers=['CPUExecutionProvider'])
        rs = ort.InferenceSession(recp, providers=['CPUExecutionProvider'])
        meta = rs.get_modelmeta().custom_metadata_map
        chs = ['blank'] + meta['character'].splitlines() + [' ']

        def mcrop(im, tw=856, th=540):
            cards = seg.apply(PILImage.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
            if not cards:
                return None
            mask = (cards[0].mask>0.5).astype(np.uint8)*255
            cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                return None
            ct = max(cnts, key=cv2.contourArea)
            ap = cv2.approxPolyDP(ct, 0.02*cv2.arcLength(ct,True),True).reshape(4,2)
            pts = sorted(ap, key=lambda x:(x[1],x[0]))
            if pts[0][0]>pts[1][0]: pts[0],pts[1]=pts[1],pts[0]
            if pts[2][0]>pts[3][0]: pts[2],pts[3]=pts[3],pts[2]
            src = np.array([pts[0],pts[1],pts[3],pts[2]], dtype=np.float32)
            dst = np.array([[0,0],[tw,0],[tw,th],[0,th]], dtype=np.float32)
            return cv2.warpPerspective(im, cv2.getPerspectiveTransform(src,dst),(tw,th),
                                       borderMode=cv2.BORDER_REPLICATE)

        def ocr_one(cv_img):
            hh, ww = 48, 192
            def cr(im):
                rh, rw = im.shape[:2]
                rw2 = ww if math.ceil(hh*rw/rh)>ww else int(math.ceil(hh*rw/rh))
                n = cv2.resize(im,(rw2,hh)).astype('float32').transpose(2,0,1)/255
                n = (n-0.5)/0.5
                p = np.zeros((3,hh,ww), dtype=np.float32)
                p[:,:,:rw2]=n
                return p
            boxes,_ = det(cv_img)
            if boxes is None or len(boxes)==0:
                return ''
            sb = sorted(enumerate(boxes), key=lambda x:(x[1][0][1],x[1][0][0]))
            crops = []
            for i,bx in sb:
                bw = int(max(np.linalg.norm(bx[0]-bx[1]),np.linalg.norm(bx[2]-bx[3])))
                bh = int(max(np.linalg.norm(bx[0]-bx[3]),np.linalg.norm(bx[1]-bx[2])))
                M = cv2.getPerspectiveTransform(bx.astype(np.float32),
                    np.array([[0,0],[bw,0],[bw,bh],[0,bh]], dtype=np.float32))
                crop = cv2.warpPerspective(cv_img,M,(bw,bh),borderMode=cv2.BORDER_REPLICATE)
                prob = cs.run(None, {'x':cr(crop)[np.newaxis,:].astype(np.float32)})[0]
                if prob[0][1]>=0.9:
                    crop = cv2.rotate(crop, cv2.ROTATE_180)
                crops.append(crop)
            ws = [c.shape[1]/c.shape[0] for c in crops]
            idx = np.argsort(ws)
            results = [('',0.0)]*len(crops)
            for b in range(0,len(crops),6):
                bi = idx[b:min(len(crops),b+6)]
                mw = max(max(ws[i] for i in bi), 320/48)
                iw = int(48*mw)
                batch = []
                for i in bi:
                    rw = min(iw, int(math.ceil(48*crops[i].shape[1]/crops[i].shape[0])))
                    n = cv2.resize(crops[i],(rw,48)).astype('float32').transpose(2,0,1)/255
                    n = (n-0.5)/0.5
                    p = np.zeros((3,48,iw), dtype=np.float32)
                    p[:,:,:rw]=n
                    batch.append(p[np.newaxis,:])
                preds = rs.run(None, {'x':np.concatenate(batch).astype(np.float32)})[0]
                for rno in range(preds.shape[0]):
                    ix, pr = preds[rno].argmax(1), preds[rno].max(1)
                    ch_list, cn, pv = [], [], -1
                    for j,cid in enumerate(ix):
                        if cid!=0 and cid!=pv:
                            ch_list.append(chs[cid] if cid<len(chs) else '')
                            cn.append(float(pr[j]))
                        pv = int(cid)
                    results[bi[rno]] = (''.join(ch_list), float(np.mean(cn)) if cn else 0.0)
            return ' '.join(t for t,s in results if s>=0.5 and t.strip())

        tt = ocr_one(tc)
        bt = ocr_one(bc)
        renyi_kw = ['姓名','公民身份号码']
        def hk(t):
            return any(k in t for k in renyi_kw)
        fc = tc if hk(tt) else (bc if hk(bt) else tc)
        bkc = bc if hk(tt) else (tc if hk(bt) else bc)

        fbytes = cv2.imencode('.jpg',fc,[cv2.IMWRITE_JPEG_QUALITY,95])[1].tobytes()
        bkbytes = cv2.imencode('.jpg',bkc,[cv2.IMWRITE_JPEG_QUALITY,95])[1].tobytes()

        fp = os.path.join(td,'f.jpg')
        with open(fp,'wb') as f:
            f.write(fbytes)
        from app01.photo import sfz, combine_a4_images
        name, idno = sfz(fp)
        i1 = PILImage.open(fp)
        i2 = PILImage.open(io.BytesIO(bkbytes))
        combined = combine_a4_images(i1, i2)
        cio = io.BytesIO()
        combined.save(cio, format='JPEG', quality=90)

        return {
            'name': name, 'id_number': idno,
            'front_image': ContentFile(fbytes, name=f'{idno}.jpg'),
            'back_image': ContentFile(bkbytes, name=f'{idno}_rotated.jpg'),
            'combined_image': ContentFile(cio.getvalue(), name=f'{idno}_双面.jpg'),
        }
    except Exception:
        import traceback; traceback.print_exc()
        return None
    finally:
        shutil.rmtree(td, ignore_errors=True)
