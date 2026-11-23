#!/usr/bin/env python3
"""사장님 가격표가 바뀌었을 때 홈페이지 가격을 한 번에 고친다.

준비: 가격표 아티팩트(새벽방음 부스 가격표)의 계산식으로 0.5~7평 0.1평 단위 공급가(부가세 별도, 높이 2000) 표를 JSON으로 만든다.
      {"single":[0.5평, 0.6평, … 7평], "super":[…], "double":[…]}  (각 66칸, 원 단위)
실행: python3 .claude/apply-prices.py 표.json --og-v 20261123 --sim-v 20261123
그다음: python3 .claude/make-jsonld.py → og.html을 크롬으로 1200×630 캡처해 og.jpg 다시 만들기(시작가가 바뀐 경우) → 줄바꿈 검사

화면 표시(2026-11-23 사장님 요청): 부가세 별도 금액을 크게 먼저, 부가세 포함 금액을 그 아래 작게. 만원 단위 반올림.
시작가는 모두 1평 기준. 크기별 표는 1·1.5·2·3평.
"""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = ['single', 'super', 'double']
ROWS = [(1, '1평'), (1.5, '1.5평'), (2, '2평'), (3, '3평')]


def man(won):
    return int(won / 10000 + 0.5)          # 만원 단위 반올림 (시뮬레이터의 Math.round와 같게)


def sub(path, pat, rep, count):
    f = ROOT / path
    s, k = re.subn(pat, rep, f.read_text(encoding='utf-8'))
    if k != count:
        raise SystemExit(f'{path}: "{pat[:50]}" 를 {count}곳에서 찾아야 하는데 {k}곳 — 화면 구조가 바뀌었는지 확인')
    f.write_text(s, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('table')
    ap.add_argument('--og-v', required=True, help="og.jpg?v= 값 (시작가가 그대로면 지금 값을 그대로 넣기)")
    ap.add_argument('--sim-v', required=True, help='simulator.html?v= 값')
    a = ap.parse_args()
    T = json.load(open(a.table, encoding='utf-8'))
    for k in KINDS:
        if len(T[k]) != 66:
            raise SystemExit(f'{k}: 0.5~7평 66칸이어야 하는데 {len(T[k])}칸')
    at = lambda k, py: T[k][round(py * 10) - 5]
    sep = {k: man(at(k, 1)) for k in KINDS}
    inc = {k: man(at(k, 1) * 1.1) for k in KINDS}

    # 부스 카드 3개 (메인·가격 페이지 같은 모양)
    for path in ['index.html', 'price/index.html']:
        it = iter(KINDS)
        f = ROOT / path
        s, k = re.subn(r'<b>\d+만원</b><span>부터</span><small>1평 · 부가세 별도</small><small class="vat">부가세 포함 \d+만원</small>',
                       lambda m: (lambda kind: f'<b>{sep[kind]}만원</b><span>부터</span><small>1평 · 부가세 별도</small>'
                                               f'<small class="vat">부가세 포함 {inc[kind]}만원</small>')(next(it)),
                       f.read_text(encoding='utf-8'))
        if k != 3:
            raise SystemExit(f'{path}: 부스 카드 3개를 못 찾음({k}개)')
        f.write_text(s, encoding='utf-8')

    s1, i1 = sep['single'], inc['single']
    sub('index.html', r'<span class="hp-top"><b>1평 \d+만원부터</b>부가세 별도 →</span><small>부가세 포함 \d+만원</small>',
        f'<span class="hp-top"><b>1평 {s1}만원부터</b>부가세 별도 →</span><small>부가세 포함 {i1}만원</small>', 1)
    sub('index.html', r'og\.jpg\?v=[0-9-]+"', f'og.jpg?v={a.og_v}"', 2)
    sub('index.html', r'simulator\.html\?v=[0-9-]+"', f'simulator.html?v={a.sim_v}"', 1)

    for py, lab in ROWS:
        cells = ''.join(f'<td>{man(at(k, py))}만<small>{man(at(k, py) * 1.1)}만</small></td>' for k in KINDS)
        sub('price/index.html', r'(<tr><th>' + re.escape(lab) + r'<small>[^<]*</small></th>)(?:<td>.*?</td>){3}</tr>',
            lambda m, c=cells: m.group(1) + c + '</tr>', 1)
    sub('price/index.html', r'싱글부스 \d+만원부터, 슈퍼싱글 \d+만원부터, 더블 \d+만원부터\(1평 기준, 부가세 별도\)\.',
        f'싱글부스 {s1}만원부터, 슈퍼싱글 {sep["super"]}만원부터, 더블 {sep["double"]}만원부터(1평 기준, 부가세 별도).', 1)
    sub('price/index.html', r'1평 싱글 \d+만원부터\(부가세 별도, 포함 \d+만원\)',
        f'1평 싱글 {s1}만원부터(부가세 별도, 포함 {i1}만원)', 1)
    sub('price/index.html', r'og\.jpg\?v=[0-9-]+"', f'og.jpg?v={a.og_v}"', 1)
    sub('move/index.html', r'og\.jpg\?v=[0-9-]+"', f'og.jpg?v={a.og_v}"', 1)
    sub('.github/og/og.html', r'<b>1평 \d+만원부터</b>부가세 별도 · 포함 \d+만원',
        f'<b>1평 {s1}만원부터</b>부가세 별도 · 포함 {i1}만원', 1)

    # 시뮬레이터 '이 부스로 상담받기' 예상 가격 표 (공급가 그대로)
    arr = lambda v: '[' + ', '.join(str(x) for x in v) + ']'
    for k, pad in [('single', ' '), ('super', '  '), ('double', ' ')]:
        sub('simulator.html', r'(\n    ' + k + ':' + pad + r')\[[0-9, ]+\]', lambda m, v=T[k]: m.group(1) + arr(v), 1)

    sub('CLAUDE.md', r'가격 배지\(1평 \d+만원부터', f'가격 배지(1평 {s1}만원부터', 1)
    sub('CLAUDE.md', r'\(바깥 1800×1800 → 약 \d+만원\)', f'(바깥 1800×1800 → 약 {s1}만원)', 1)

    print('시작가(부가세 별도/포함):', {k: (sep[k], inc[k]) for k in KINDS})
    for py, lab in ROWS:
        print(lab, [(man(at(k, py)), man(at(k, py) * 1.1)) for k in KINDS])
    print('다음: python3 .claude/make-jsonld.py / og.jpg 다시 찍기(시작가가 바뀌었으면) / 줄바꿈 검사')


if __name__ == '__main__':
    main()
