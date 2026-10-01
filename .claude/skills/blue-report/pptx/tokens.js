'use strict';
/**
 * blue-report.css 의 커스텀 속성을 읽어 PPTX 생성기에 넘긴다.
 *
 * 색·크기 값을 여기 다시 적지 않는다. CSS 한 곳만 고치면 HTML 덱과 PPTX가 함께 바뀐다.
 * pptxgenjs 는 '#' 없는 6자리 hex 만 받으므로 변환도 여기서 한다.
 */
const fs = require('fs');
const path = require('path');

const CSS = path.join(__dirname, '..', 'assets', 'blue-report.css');

function parse() {
  const css = fs.readFileSync(CSS, 'utf8');
  const root = css.slice(css.indexOf(':root'), css.indexOf('/* ====', css.indexOf(':root')));
  const out = {};
  for (const m of root.matchAll(/--br-([a-z0-9-]+)\s*:\s*([^;]+);/g)) {
    out[m[1]] = m[2].trim();
  }
  if (!out['page'] || !out['cobalt']) {
    throw new Error('토큰을 읽지 못했다. blue-report.css 의 :root 블록을 확인한다.');
  }
  return out;
}

const RAW = parse();

/** '#2f4a9c' → '2F4A9C'. pptxgenjs 는 # 과 알파를 받으면 파일이 깨진다. */
function hex(name) {
  const v = RAW[name];
  if (!v) throw new Error(`토큰 없음: --br-${name}`);
  const m = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.exec(v.trim());
  if (!m) throw new Error(`hex 가 아님: --br-${name} = ${v}`);
  const h = m[1].length === 3 ? m[1].split('').map((c) => c + c).join('') : m[1];
  return h.toUpperCase();
}

/** HTML 캔버스 1920x1080 → 슬라이드 13.333x7.5in. 1in = 144px, 1pt = 2px. */
const PX_PER_IN = 144;
const px = (n) => n / PX_PER_IN;      // px → inch
const pt = (n) => n / 2;              // css px → pt (같은 물리 크기)

const C = {
  page: hex('page'), card: hex('card'), cardLine: hex('card-line'),
  tint: hex('tint'),        // 대조군 카드 · 막대 트랙
  hairline: hex('hairline'), chipLine: hex('chip-line'),
  text: hex('text'), text2: hex('text-2'), text3: hex('text-3'),
  cobalt: hex('cobalt'), cyan: hex('cyan'), navy: hex('navy'), coral: hex('coral'),
  okLine: hex('ok-line'), okBg: hex('ok-bg'), okText: hex('ok-text'),
  warnLine: hex('warn-line'), warnBg: hex('warn-bg'), warnText: hex('warn-text'),
  alertLine: hex('alert-line'), alertBg: hex('alert-bg'), alertText: hex('alert-text'),
  okOnDark: hex('ok-on-dark'), warnOnDark: hex('warn-on-dark'), alertOnDark: hex('alert-on-dark'),
  // 계열색 — 순서가 없는 항목(부서 · 제품)을 가른다. data 램프와 쓰임이 다르다.
  cat: [hex('cat-1'), hex('cat-2'), hex('cat-3'),
        hex('cat-4'), hex('cat-5'), hex('cat-6')],
  catDark: [hex('cat-dark-1'), hex('cat-dark-2'), hex('cat-dark-3'),
            hex('cat-dark-4'), hex('cat-dark-5'), hex('cat-dark-6')],
  cover: hex('cover'), dark: hex('dark'), darkLine: hex('dark-line'),
  onDark: hex('on-dark'), onDark2: hex('on-dark-2'), onDark3: hex('on-dark-3'),
  onCover2: hex('on-cover-2'), onCover3: hex('on-cover-3'),
  accentOnDark: hex('accent-on-dark'), amber: hex('amber'),
  data: [hex('data-1'), hex('data-2'), hex('data-3'), hex('data-4'), hex('data-5')],
  bar: [hex('bar-1'), hex('bar-2'), hex('bar-3'), hex('bar-4'),
        hex('bar-5'), hex('bar-6'), hex('bar-7')],
  soft: [hex('soft-1'), hex('soft-2'), hex('soft-3')],
  white: 'FFFFFF',
};

/**
 * 폰트. HTML 은 저장소가 들고 있는 프리텐다드 서브셋을 본문에 심어 쓰지만,
 * PowerPoint 는 그 파일을 볼 수 없다 — PC 에 설치된 폰트만 쓴다.
 *
 * 그래서 이름으로 프리텐다드를 지목하되, 설치되지 않은 PC 에서 무엇으로 떨어질지를
 * 정해 둔다. pptxgenjs 는 대체 목록을 받지 않으므로 한 이름만 적을 수 있고,
 * PowerPoint 는 없는 폰트를 만나면 제멋대로 고른다. 사내 배포가 끝나기 전까지는
 * 그 위험을 안는 대신 화면과 같은 글자를 얻는다.
 *
 *   사내 PC 에 프리텐다드를 배포했다면  → 이대로 둔다
 *   아직 배포 전이라 깨짐이 걱정되면    → 세 줄을 '맑은 고딕' 으로 되돌린다
 *
 * 배포 파일은 https://github.com/orioncactus/pretendard 의 릴리스에서 받는다.
 * assets/fonts/ 의 것은 KS X 1001 로 잘라 낸 웹용이라 설치용으로 쓰지 않는다.
 */
const F = { kr: 'Pretendard', num: 'Pretendard', label: 'Pretendard' };

/** 슬라이드 격자 — HTML 의 --br-pad-slide 등과 같은 비율 */
const G = {
  W: 13.333, H: 7.5,
  M: px(96),                     // 좌우 여백 96px
  get CW() { return this.W - this.M * 2; },
  TOP: px(84),
  BOTTOM: px(60),
  coverPad: px(120),
  coverTop: px(110),
};

module.exports = { RAW, C, F, G, px, pt, hex };
