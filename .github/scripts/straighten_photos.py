# 사진의 세로선(벽 모서리·문틀·패널 줄눈)이 모두 평행하게 서도록 원근을 맞추고, 빈 테두리만 잘라낸다.
# 기울기(돌아감)와 위아래로 좁아지는 원근을 함께 바로잡는다. 색·밝기 보정은 하지 않는다.
# 세로선을 못 찾는 사진(위에서 내려다본 사진 등)은 그대로 둔다.
# 사용: pip install opencv-python-headless && python3 .github/scripts/straighten_photos.py photos/case1/*.jpg
import sys, math
import cv2, numpy as np

def vertical_segments(g):
    L = cv2.createLineSegmentDetector(0).detect(g)[0]
    if L is None: return np.zeros((0, 4))
    out = []
    for x1, y1, x2, y2 in L.reshape(-1, 4):
        if math.hypot(x2-x1, y2-y1) < max(g.shape)*0.07: continue
        a = math.degrees(math.atan2(x2-x1, y2-y1))
        if a > 90: a -= 180
        if a < -90: a += 180
        if abs(a) < 25: out.append((x1, y1, x2, y2))
    return np.array(out)

def vanishing_point(V):
    # 세로선들이 모이는 점(동차좌표) — 길이 가중 최소제곱
    A = []
    for x1, y1, x2, y2 in V:
        l = np.cross([x1, y1, 1.0], [x2, y2, 1.0])
        A.append(l/np.hypot(l[0], l[1])*math.hypot(x2-x1, y2-y1))
    return np.linalg.svd(np.array(A))[2][-1]

def keystone(vp, w, h):
    # 소실점을 세로축 위로 돌린 뒤 무한대로 보내 세로선을 평행하게 만든다 (사진 가운데 기준)
    T = np.array([[1, 0, -w/2], [0, 1, -h/2], [0, 0, 1]], float)
    v = T @ vp
    vx, vy = (v[0]/v[2], v[1]/v[2]) if abs(v[2]) > 1e-9 else (v[0]*1e9, v[1]*1e9)
    ang = math.atan2(vx, vy) if vy >= 0 else math.atan2(-vx, -vy)
    c, s = math.cos(ang), math.sin(ang)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)
    p = R @ np.array([vx, vy, 1.0]); d = p[1]/p[2]
    P = np.eye(3)
    if abs(d) > 1e-6: P[2, 1] = -1/d
    return np.linalg.inv(T) @ P @ R @ T

def largest_crop(mask, w, h):
    # 빈 테두리가 안 들어가는, 원래 비율 그대로의 가장 큰 사각형
    best = None
    for cy in np.linspace(0.40, 0.60, 11):
        for cx in np.linspace(0.44, 0.56, 7):
            lo, hi = 0.2, 1.0
            for _ in range(20):
                m = (lo+hi)/2; ww, hh = w*m, h*m
                x0, y0 = int(cx*w - ww/2), int(cy*h - hh/2); x1, y1 = int(x0+ww), int(y0+hh)
                ok = x0 >= 0 and y0 >= 0 and x1 <= w and y1 <= h and mask[y0:y1:4, x0:x1:4].min() == 255
                lo, hi = (m, hi) if ok else (lo, m)
            if best is None or lo > best[0]: best = (lo, cx, cy)
    m, cx, cy = best; ww, hh = int(w*m), int(h*m)
    return int(cx*w - ww/2), int(cy*h - hh/2), ww, hh

for f in sys.argv[1:]:
    im = cv2.imread(f); h, w = im.shape[:2]
    V = vertical_segments(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
    if len(V) < 6:
        print('그대로(세로선 부족):', f); continue
    H = keystone(vanishing_point(V), w, h)
    out = cv2.warpPerspective(im, H, (w, h), flags=cv2.INTER_CUBIC)
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), H, (w, h), flags=cv2.INTER_NEAREST)
    mask = cv2.erode(mask, np.ones((7, 7), np.uint8))
    x0, y0, ww, hh = largest_crop(mask, w, h)
    cv2.imwrite(f, out[y0:y0+hh, x0:x0+ww], [cv2.IMWRITE_JPEG_QUALITY, 88, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
    print('바로 세움 (%.0f%% 남김):' % (ww/w*100), f)
