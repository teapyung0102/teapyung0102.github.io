# 사진 가운데 쪽 세로선(벽 모서리·문틀·패널 줄눈)을 찾아 기울기를 재고, 똑바로 세운 뒤 빈 모서리만 잘라낸다.
# 색·밝기 보정은 하지 않는다. 0.8° 미만은 그대로 둔다.
# 사용: pip install opencv-python-headless pillow && python3 .github/scripts/straighten_photos.py photos/case1/*.jpg
import sys, math
import cv2, numpy as np
from PIL import Image, ImageOps

def tilt(path):
    im = cv2.imread(path); h, w = im.shape[:2]; s = 1000/max(h, w)
    g = cv2.cvtColor(cv2.resize(im, None, fx=s, fy=s), cv2.COLOR_BGR2GRAY)
    L = cv2.createLineSegmentDetector(0).detect(g)[0]
    if L is None: return None
    H, W = g.shape; angs = []; ws = []
    for x1, y1, x2, y2 in L.reshape(-1, 4):
        dx, dy = x2-x1, y2-y1; ln = math.hypot(dx, dy)
        if ln < H*0.08: continue
        a = math.degrees(math.atan2(dx, dy))
        if a > 90: a -= 180
        if a < -90: a += 180
        if abs(a) > 12: continue
        if abs(((x1+x2)/2 - W/2)/(W/2)) > 0.4: continue   # 광각 가장자리는 원근으로 원래 기운다
        angs.append(a); ws.append(ln)
    if len(angs) < 4: return None
    angs = np.array(angs); ws = np.array(ws); o = np.argsort(angs); c = np.cumsum(ws[o])
    return float(angs[o][np.searchsorted(c, c[-1]/2)])

def rot_crop(im, deg):
    w, h = im.size; r = im.rotate(deg, resample=Image.BICUBIC)
    t = math.radians(abs(deg)); c, s = math.cos(t), math.sin(t)
    k = min(w/(w*c + h*s), h/(w*s + h*c))
    nw, nh = w*k, h*k; x0, y0 = (w-nw)/2, (h-nh)/2
    return r.crop((round(x0), round(y0), round(x0+nw), round(y0+nh)))

for f in sys.argv[1:]:
    a = tilt(f)
    if a is None or abs(a) < 0.8:
        print('그대로:', f, a); continue
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    rot_crop(im, -a).save(f, 'JPEG', quality=88, optimize=True, progressive=True)
    print('바로 세움 %.1f°:' % a, f)
