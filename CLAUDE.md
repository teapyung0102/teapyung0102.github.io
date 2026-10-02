# 새벽방음 홈페이지

- `index.html`: 홈페이지, `simulator.html`: 방음부스 시뮬레이터 (index.html 안에 iframe으로 들어감)
- 사용자에게 설명은 항상 한국어로, 쉽게.
- simulator.html을 고치면 index.html의 iframe 주소 `simulator.html?v=...` 값도 바꿀 것 (브라우저가 예전 시뮬레이터를 기억하지 않게)
- 수정하면 main에 바로 push (GitHub Pages로 바로 반영됨). push가 안 되면 사용자가 뭘 눌러야 하는지만 쉽게 안내.

## 줄바꿈 규칙 (항상 지킬 것)
- 모바일·PC 모두에서 문장 끝 1~2글자(예: "지.", "요.")만 다음 줄로 튀어나오면 안 됨.
- 문구를 바꾸거나 레이아웃을 건드리면 반드시 검사하고, 걸리면 알아서 폰트 크기·줄나눔을 조정할 것.
- 검사: `NODE_PATH=$(npm root -g) node .claude/check-orphans.js`
  (360~1440px 폭에서 마지막 줄이 2글자 이하인 곳을 출력. `H4. ... 4색/3색`은 작은 글씨 배지라 무시해도 됨)
- 기본 장치: body에 `word-break:keep-all`(단어 중간에서 안 끊김), 본문에 `text-wrap:pretty`.

## 사진
- `photos/[칸이름]/` 폴더에 아무 이름으로 올리면 자동으로 뜸 (hero, single, supersingle, double, case1~6).
- 큰 사진은 `.github/workflows/shrink-photos.yml`이 main에 올라올 때 자동으로 긴 변 1920px로 줄임.
  사진을 직접 넣을 때도 `python3 .github/scripts/shrink_photos.py`로 줄여서 올릴 것.
- 사진이 기울어 보이면 `python3 .github/scripts/straighten_photos.py photos/폴더/*.jpg` (세로선 기준으로 바로 세우고 빈 모서리만 자름, 색 보정 없음). 위에서 내려다본 사진처럼 세로선이 없는 사진은 결과를 눈으로 확인할 것.
