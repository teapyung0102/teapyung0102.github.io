# photos/ 안의 큰 사진을 긴 변 1920px, JPEG 품질 82로 줄인다 (이미 작은 사진은 그대로 둔다)
import glob, os
from PIL import Image, ImageOps

MAX = 1920
LIMIT = 1500 * 1024  # 크기가 1920 이하인데도 1.5MB 넘으면 다시 저장 (이미 줄인 사진을 거듭 압축하지 않게)

for f in glob.glob('photos/**/*', recursive=True):
    ext = os.path.splitext(f)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
        continue
    im = Image.open(f)
    if max(im.size) <= MAX and os.path.getsize(f) <= LIMIT:
        continue
    im = ImageOps.exif_transpose(im)
    im.thumbnail((MAX, MAX), Image.LANCZOS)
    if ext == '.png':
        im.save(f, 'PNG', optimize=True)
    elif ext == '.webp':
        im.save(f, 'WEBP', quality=82)
    else:
        im.convert('RGB').save(f, 'JPEG', quality=82, optimize=True, progressive=True)
    print('줄임:', f, im.size, os.path.getsize(f) // 1024, 'KB')
