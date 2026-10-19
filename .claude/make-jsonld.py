#!/usr/bin/env python3
"""검색엔진·AI가 읽는 '업체 정보 꼬리표'(구조화 데이터, JSON-LD)를 세 페이지에 다시 만들어 넣는다.

화면에 보이는 내용(부스 카드 가격, 자주 묻는 질문)을 페이지에서 그대로 읽어 만들기 때문에
자주 묻는 질문·가격·연락처를 고친 뒤 한 번만 실행하면 된다:  python3 .claude/make-jsonld.py

각 페이지 <head> 안 <!-- jsonld:start --> ~ <!-- jsonld:end --> 사이를 통째로 바꾼다.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://saebyeok0711.co.kr/'
BIZ_ID = SITE + '#business'

# 화면(연락처 칸·바닥글)에 적힌 업체 정보 — 바뀌면 여기도 고칠 것
BUSINESS = {
    '@type': 'HomeAndConstructionBusiness',
    '@id': BIZ_ID,
    'name': '새벽방음',
    'description': '경기 안산에 본사를 둔 방음부스 업체. 현직 음악PD가 직접 제작·시공하는 조립식 고정형 방음부스. 방 크기에 맞춰 mm 단위로 설계하고, 집 손상을 최소화해 월세·전세집에도 시공해요.',
    'url': SITE,
    'logo': SITE + 'apple-touch-icon.png',
    'image': SITE + 'og.jpg',
    'telephone': '+82-10-4189-4529',
    'email': 'saebyeok0711@naver.com',
    'address': {'@type': 'PostalAddress', 'streetAddress': '화랑로 170', 'addressLocality': '안산시 단원구',
                'addressRegion': '경기도', 'addressCountry': 'KR'},
    'areaServed': {'@type': 'Country', 'name': '대한민국'},
    'founder': {'@type': 'Person', 'name': '정태평', 'jobTitle': '음악 PD'},
    'sameAs': ['https://blog.naver.com/saebyeok0711', 'https://www.youtube.com/@saebyeok0711',
               'https://pf.kakao.com/_TGWFX'],
    'knowsAbout': ['방음부스', '조립식 방음부스', '가정용 방음부스', '방음부스 이전', '방음부스 증축', '방음부스 철거'],
}


def text(fragment):
    fragment = re.sub(r'<a class="more"[^>]*>.*?</a>', '', fragment, flags=re.S)   # '자세히 보기 →' 링크는 뺌
    fragment = re.sub(r'<(br|/p|/li|/div)\s*/?>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


def faq_page(src, url):
    items = []
    for m in re.finditer(r'<details class="faq[^"]*">\s*<summary>(.*?)</summary>\s*<div class="faq-a">(.*?)</div>\s*</details>', src, re.S):
        q = text(m.group(1).replace('<span class="q">Q</span>', ''))
        a = text(m.group(2))
        if q and a:
            items.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return {'@type': 'FAQPage', '@id': url + '#faq', 'about': {'@id': BIZ_ID}, 'mainEntity': items} if items else None


def booth_offers(src):
    """메인 부스 카드(이름 · 용도 한 줄 · 'OOO만원 부터' · '0.5평 · 부가세 포함')를 그대로 읽는다."""
    offers = []
    for m in re.finditer(r'<article class="booth">(.*?)</article>', src, re.S):
        card = m.group(1)
        name = text(re.search(r'<h3>(.*?)</h3>', card).group(1))
        use = text(re.search(r'<p>(.*?)</p>', card).group(1))
        man = int(re.search(r'<b>(\d+)만원</b>', card).group(1))
        basis = text(re.search(r'<small>(.*?)</small>', card).group(1))
        offers.append({'@type': 'Offer', 'name': name, 'description': f'{use} ({basis}, {man}만원부터)',
                       'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': man * 10000,
                                              'priceCurrency': 'KRW', 'valueAddedTaxIncluded': True},
                       'url': SITE + 'price/'})
    return offers


def graph(path, src):
    url = SITE + ('' if path == 'index.html' else path.replace('index.html', ''))
    g = []
    if path == 'index.html':
        g.append({'@type': 'WebSite', '@id': SITE + '#website', 'name': '새벽방음', 'alternateName': '새벽 방음',
                  'url': SITE, 'publisher': {'@id': BIZ_ID}})
        biz = dict(BUSINESS)
        offers = booth_offers(src)
        if offers:
            biz['priceRange'] = f"{min(o['priceSpecification']['minPrice'] for o in offers) // 10000}만원부터 (부가세 포함)"
            biz['makesOffer'] = offers
        g.append(biz)
    elif path == 'move/index.html':
        desc = re.search(r'<meta name="description" content="([^"]+)"', src).group(1)
        g.append({'@type': 'Service', '@id': url + '#service', 'name': '방음부스 이전·증축·철거', 'serviceType': '방음부스 이전',
                  'description': html.unescape(desc), 'url': url, 'provider': {'@id': BIZ_ID},
                  'areaServed': {'@type': 'Country', 'name': '대한민국'}})
    faq = faq_page(src, url)
    if faq:
        g.append(faq)
    return {'@context': 'https://schema.org', '@graph': g}


def main():
    for path in ['index.html', 'price/index.html', 'move/index.html']:
        f = ROOT / path
        src = f.read_text(encoding='utf-8')
        block = ('<!-- jsonld:start  검색엔진·AI용 업체 정보 꼬리표. 직접 고치지 말고 python3 .claude/make-jsonld.py 로 다시 만들 것 -->\n'
                 '<script type="application/ld+json">\n'
                 + json.dumps(graph(path, src), ensure_ascii=False, indent=1) +
                 '\n</script>\n<!-- jsonld:end -->')
        if '<!-- jsonld:start' not in src:
            sys.exit(f'{path}: <!-- jsonld:start --> 표시가 없어요')
        new = re.sub(r'<!-- jsonld:start.*?<!-- jsonld:end -->', lambda _: block, src, flags=re.S)
        f.write_text(new, encoding='utf-8')
        print(path, '완료')


if __name__ == '__main__':
    main()
