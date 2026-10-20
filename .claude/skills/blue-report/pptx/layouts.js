'use strict';
/**
 * 블루 리포트 슬라이드 레이아웃 — PowerPoint 판.
 *
 * HTML 덱과 같은 격자를 쓴다. 1920x1080px 캔버스를 13.333x7.5in 로 옮기므로
 * 1in = 144px, 1pt = 2px 다. 좌표는 전부 px 로 적고 X()/Y() 로 변환한다.
 *
 * pptxgenjs 주의:
 *  - option 객체를 재사용하면 두 번째 호출부터 좌표가 깨진다. 매번 새로 만든다.
 *  - 색은 '#' 없는 6자리 hex 만. 알파를 섞으면 파일이 깨진다.
 *  - addText 에는 항상 isTextBox: true.
 */
const { C, F, G, px, pt } = require('./tokens');

const X = px;                       // px → inch (가로·세로 동일 배율)
const SLIDE_W = 13.333, SLIDE_H = 7.5;

// HTML 의 --br-pad-slide: 84px 96px 60px
const PAD = { top: 84, side: 96, bottom: 60 };
const COVER_PAD = { top: 110, side: 120, bottom: 80 };
const CW = 1920 - PAD.side * 2;     // 본문 폭 1728px

/* ─────────────────────────────── 원자 helper ─────────────────────────────── */

const txt = (slide, text, o) =>
  slide.addText(text, Object.assign({ isTextBox: true, margin: 0 }, o));

/** 카드 — 흰 배경 + 얇은 테두리 + 은은한 그림자.
 *
 * 다크면에서는 판을 그리지 않는다. 짙은 지면 위에 짙은 판을 얹으면 경계가
 * 대비 1.12:1 로 뭉개진다. HTML 의 .br-slide--dark .br-card 와 같은 처리로,
 * 상단 괘선 2px 만 긋는다. 두 판이 갈라지면 안 되므로 여기도 같이 바꾼다. */
function card(slide, { x, y, w, h, dark = false, fill, line, topBar }) {
  if (dark && !fill) {
    slide.addShape('rect', {
      x: X(x), y: X(y), w: X(w), h: X(2),
      fill: { color: line || C.accentOnDark }, line: { type: 'none' },
    });
    return;
  }
  // 테두리를 두르지 않는다 — HTML 과 같은 규칙이다. 테두리와 그림자를 함께 쓰면
  // 그림자가 하는 일이 사라지고 카드가 「떠 있는 면」이 아니라 「상자」로 읽힌다.
  // rectRadius 0.19 ≈ 28px (X() 가 px→inch 이므로 높이 대비 비율이 아니라 절대값이다).
  slide.addShape('roundRect', {
    x: X(x), y: X(y), w: X(w), h: X(h), rectRadius: 0.19,
    fill: { color: fill || C.card },
    line: { type: 'none' },
    shadow: { type: 'outer', color: '101828', opacity: 0.12,
              blur: 20, offset: 7, angle: 90 },
  });
  if (topBar) {
    // 단계 강조 카드에만 허용하는 상단 굵은 선 (HTML 의 .br-card--step)
    slide.addShape('rect', {
      x: X(x), y: X(y), w: X(w), h: X(8),
      fill: { color: topBar }, line: { type: 'none' },
    });
  }
}

/** 배경 워터마크 — 다크면 가운데에 회사 마크를 아주 옅게 깐다.
 *
 * HTML 의 .br-watermark 와 같은 크기(720px)·같은 불투명도(5%)다. 슬라이드에
 * 가장 먼저 그려야 본문 뒤에 깔린다 — pptxgenjs 는 z-index 가 없고 추가 순서가
 * 곧 쌓임 순서다. */
function watermark(slide, brand, dark = true) {
  const src = dark ? brand.watermarkPath : brand.watermarkPathOnLight;
  if (!src) return;
  const w = X(720);
  const ratio = (dark ? brand.watermarkRatio : brand.watermarkRatioOnLight)
    || brand.logoRatio || 3.07;
  const h = w / ratio;
  // 밝은 지면은 잉크가 진해 더 옅게 깐다. HTML 의 3% / 5% 와 같다.
  slide.addImage({ path: src, x: (SLIDE_W - w) / 2, y: (SLIDE_H - h) / 2, w, h,
    transparency: dark ? 95 : 97 });
}

/** 알약 칩 — 그림자 없음. HTML 의 .br-chip */
function chip(slide, { x, y, w, h, text, solid, fillColor, lineColor, color, fontSize }) {
  slide.addShape('roundRect', {
    x: X(x), y: X(y), w: X(w), h: X(h), rectRadius: 0.5,
    fill: { color: fillColor || (solid ? C.cobalt : C.card) },
    line: { color: lineColor || (solid ? C.cobalt : C.chipLine), width: 0.75 },
  });
  txt(slide, text, {
    x: X(x), y: X(y), w: X(w), h: X(h), align: 'center', valign: 'middle',
    fontFace: F.kr, fontSize: pt(fontSize || 25), bold: !!solid,
    color: color || (solid ? C.white : '45505C'),
  });
}

/** 섹션 라벨 + 제목. 제목 밑줄은 쓰지 않는다. */
function header(slide, { eyebrow, title, titleBold, dark = false, y = PAD.top }) {
  let cy = y;
  if (eyebrow) {
    txt(slide, eyebrow.toUpperCase(), {
      x: X(PAD.side), y: X(cy), w: X(CW), h: X(30),
      fontFace: F.label, fontSize: pt(26), bold: true, charSpacing: 3,
      color: dark ? C.accentOnDark : C.navy, valign: 'middle',
    });
    cy += 46;
  }
  const runs = titleBold
    ? [{ text: title + ' ', options: { bold: false } },
       { text: titleBold, options: { bold: true } }]
    : [{ text: title, options: { bold: true } }];
  slide.addText(runs, {
    isTextBox: true, margin: 0,
    x: X(PAD.side), y: X(cy), w: X(CW), h: X(78),
    fontFace: F.kr, fontSize: pt(62), color: dark ? C.onDark : C.text,
    valign: 'middle', charSpacing: -1,
  });
  return cy + 78;
}

/** 제목 아래 요약 문장. 줄바꿈은 배열로 넘긴다. */
function lede(slide, lines, { y, dark = false }) {
  const runs = [];
  lines.forEach((ln, i) => {
    (Array.isArray(ln) ? ln : [ln]).forEach((seg) => {
      if (typeof seg === 'string') runs.push({ text: seg, options: {} });
      else runs.push({ text: seg.k, options: { bold: true, color: dark ? C.onDark : C.navy } });
    });
    if (i < lines.length - 1) runs[runs.length - 1].options.breakLine = true;
  });
  slide.addText(runs, {
    isTextBox: true, margin: 0,
    x: X(PAD.side), y: X(y), w: X(CW), h: X(lines.length * 46),
    fontFace: F.kr, fontSize: pt(28), color: dark ? C.onCover2 : C.text2,
    lineSpacingMultiple: 1.5, valign: 'top',
  });
  return y + lines.length * 46;
}

/** 꼬리말 — 문서명 + 두 자리 쪽번호. HTML 뷰어가 하던 일을 여기서 한다. */
function footer(slide, { docTitle, page, dark = false }) {
  const runs = [
    { text: docTitle + ' ', options: {} },
    { text: String(page).padStart(2, '0'), options: { bold: true, color: dark ? C.onDark2 : C.text2 } },
  ];
  slide.addText(runs, {
    isTextBox: true, margin: 0,
    x: X(PAD.side), y: X(1080 - PAD.bottom - 34), w: X(CW), h: X(34),
    align: 'right', valign: 'middle',
    fontFace: F.kr, fontSize: pt(24), color: dark ? C.onDark3 : C.text3,
  });
}

/** 6자리 hex 의 상대 광도. HTML 판 check_deck.py 와 같은 식을 쓴다. */
function luminance(hex) {
  const v = [0, 2, 4].map(i => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
}

/**
 * 브랜드 마크 — 모든 슬라이드의 우측 상단 모서리. HTML 판 .br-mark 와 같은 자리다.
 * 배경 광도를 직접 재서 로고 변형을 고르므로, 배경색을 바꿔도 규칙이 따라온다.
 *   어두운 면 → logo(흰색 녹아웃) · 밝은 면 → logoOnLight(원색)
 * 여백 띠 안에 넣어 본문과 겹치지 않게 한다 (일반 top 26 · 표지 top 38).
 */
function mark(slide, brand) {
  const bg = ((slide.background && slide.background.color) || 'FFFFFF').replace('#', '');
  const dark = luminance(bg) < 0.5;
  const cover = bg.toUpperCase() === String(C.cover).replace('#', '').toUpperCase();
  const top = cover ? 38 : 26;
  const side = cover ? COVER_PAD.side : PAD.side;
  const logo = dark ? brand.logoPath : brand.logoPathOnLight;

  if (logo) {
    const h = X(brand.logoHeight || 40);
    const iw = h * (brand.logoRatio || 3.07);
    slide.addImage({ path: logo, y: X(top), x: X(1920 - side) - iw, w: iw, h });
    return;
  }
  const w = 420, size = 28;
  txt(slide, brand.wordmark, {
    x: X(1920 - side - w), y: X(top), w: X(w), h: X(size * 1.4),
    align: 'right', valign: 'middle', fontFace: F.label, fontSize: pt(size),
    bold: true, charSpacing: 6, color: dark ? C.onDark : C.cobalt,
  });
}

module.exports = { X, SLIDE_W, SLIDE_H, PAD, COVER_PAD, CW, txt, card, chip, header, lede, footer, mark, watermark };
