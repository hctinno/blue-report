'use strict';
/** 블루 리포트 슬라이드 종류별 생성기 (PowerPoint 판) */
const { C, F, G, px, pt } = require('./tokens');
const L = require('./layouts');
const { X, PAD, COVER_PAD, CW, txt, card, chip, header, lede, footer } = L;

const W = 1920, H = 1080;

/* ── 표지 ─────────────────────────────────────────────────────────────── */
function cover(pres, s, brand) {
  const sl = pres.addSlide();
  sl.background = { color: C.cover };
  // 표지에는 워터마크를 깔지 않는다. 본문이 왼쪽에 몰려 있어 가운데 마크와 제목이 겹친다.
  txt(sl, s.eyebrow, { x: X(COVER_PAD.side), y: X(112), w: X(1200), h: X(40),
    fontFace: F.kr, fontSize: pt(30), color: C.soft[1], valign: 'middle' });
  txt(sl, s.titleLight, { x: X(COVER_PAD.side), y: X(168), w: X(1400), h: X(132),
    fontFace: F.kr, fontSize: pt(108), color: C.onDark, valign: 'middle', charSpacing: -3 });
  txt(sl, s.titleBold, { x: X(COVER_PAD.side), y: X(300), w: X(1500), h: X(132),
    fontFace: F.kr, fontSize: pt(108), bold: true, color: C.onDark, valign: 'middle', charSpacing: -3 });

  if (s.metaLabel) {
    const bw = 30 + s.metaLabel.length * 30 + s.metaValue.length * 17;
    sl.addShape('rect', { x: X(COVER_PAD.side), y: X(466), w: X(bw), h: X(70),
      fill: { type: 'none' }, line: { color: C.onCover3, width: 0.75 } });
    txt(sl, [
      { text: s.metaLabel + '   ', options: { color: C.soft[1] } },
      { text: s.metaValue, options: { fontFace: F.num, color: C.onDark } },
    ], { x: X(COVER_PAD.side + 26), y: X(466), w: X(bw - 52), h: X(70),
      fontFace: F.kr, fontSize: pt(24), valign: 'middle' });
  }

  if (brand.email) {
    txt(sl, brand.email, { x: X(COVER_PAD.side), y: X(1000), w: X(700), h: X(30),
      fontFace: F.num, fontSize: pt(24), color: C.soft[1], valign: 'middle' });
  }
  txt(sl, `© ${brand.copyrightYear} ${brand.company} · All rights reserved`, {
    x: X(W - COVER_PAD.side - 900), y: X(950), w: X(900), h: X(30),
    align: 'right', valign: 'middle', fontFace: F.num, fontSize: pt(24), color: C.onCover3 });
  return sl;
}

/* ── 목차 ─────────────────────────────────────────────────────────────── */
function agenda(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  txt(sl, s.heading || 'Contents', { x: X(PAD.side), y: X(PAD.top), w: X(420), h: X(110),
    fontFace: F.label, fontSize: pt(92), bold: true, color: C.cobalt, valign: 'top' });

  const left = PAD.side + 460;
  const availH = H - PAD.top - PAD.bottom - 60;
  const ITEM_H = 140;                                  // 번호+제목+설명 2줄
  const step = s.items.length > 1
    ? (availH - ITEM_H - (s.callout ? 150 : 0)) / (s.items.length - 1)
    : 0;
  s.items.forEach((it, i) => {
    const y = PAD.top + i * step;
    txt(sl, it.no, { x: X(left), y: X(y), w: X(96), h: X(50),
      fontFace: F.num, fontSize: pt(40), bold: true, color: C.cobalt, valign: 'top' });
    txt(sl, it.title, { x: X(left + 110), y: X(y - 4), w: X(980), h: X(54),
      fontFace: F.kr, fontSize: pt(38), bold: true, color: C.text, valign: 'top', charSpacing: -1 });
    txt(sl, it.desc.join('\n'), { x: X(left + 110), y: X(y + 54), w: X(1000), h: X(80),
      fontFace: F.kr, fontSize: pt(25), color: C.text2, valign: 'top', lineSpacingMultiple: 1.6 });
    txt(sl, it.page, { x: X(W - PAD.side - 140), y: X(y + 6), w: X(140), h: X(40),
      align: 'right', fontFace: F.num, fontSize: pt(26), color: C.text3, valign: 'top' });
  });
  if (s.callout) {
    const cy = H - PAD.bottom - 150;
    sl.addShape('roundRect', { x: X(left), y: X(cy), w: X(W - PAD.side - left), h: X(90),
      rectRadius: 0.125, fill: { color: C.warnBg }, line: { color: C.warnLine, width: 0.75 } });
    txt(sl, [{ text: s.callout.k + ' — ', options: { bold: true } },
             { text: s.callout.v, options: {} }], {
      x: X(left + 30), y: X(cy), w: X(W - PAD.side - left - 60), h: X(90),
      fontFace: F.kr, fontSize: pt(25), color: C.warnText, valign: 'middle', lineSpacingMultiple: 1.4 });
  }
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 핵심 정리 (다크, 카드 6개까지) ───────────────────────────────────── */
function darkSummary(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.dark };
  L.watermark(sl, brand, true);
  const y0 = header(sl, { eyebrow: s.eyebrow, title: s.title, dark: true }) + 40;

  const cols = 2, gapX = 34, gapY = 30;
  const cw = (CW - gapX) / cols;
  const rows = Math.ceil(s.cards.length / cols);
  const availH = H - y0 - PAD.bottom - 50;
  const ch = (availH - gapY * (rows - 1)) / rows;

  s.cards.forEach((c, i) => {
    const cx = PAD.side + (i % cols) * (cw + gapX);
    const cy = y0 + Math.floor(i / cols) * (ch + gapY);
    card(sl, { x: cx, y: cy, w: cw, h: ch, dark: true });
    sl.addShape('rect', { x: X(cx + 34), y: X(cy + 34), w: X(64), h: X(52),
      fill: { type: 'none' }, line: { color: C.darkLine, width: 0.75 } });
    txt(sl, c.no, { x: X(cx + 34), y: X(cy + 34), w: X(64), h: X(52),
      align: 'center', valign: 'middle', fontFace: F.num, fontSize: pt(24), bold: true, color: C.onDark2 });
    txt(sl, c.title, { x: X(cx + 120), y: X(cy + 30), w: X(cw - 300), h: X(50),
      fontFace: F.kr, fontSize: pt(32), bold: true, color: C.onDark, valign: 'middle' });
    txt(sl, c.desc.join('\n'), { x: X(cx + 120), y: X(cy + 86), w: X(cw - 300), h: X(ch - 116),
      fontFace: F.kr, fontSize: pt(24), color: C.onDark2, valign: 'top', lineSpacingMultiple: 1.5 });
    txt(sl, [
      { text: c.stat, options: {} },
      ...(c.sup ? [{ text: c.sup, options: { fontSize: pt(28) } }] : []),
    ], { x: X(cx + cw - 170), y: X(cy), w: X(140), h: X(ch),
      align: 'right', valign: 'middle', fontFace: F.num, fontSize: pt(56), bold: true,
      color: c.warn ? C.amber : C.accentOnDark });
  });
  footer(sl, { docTitle: brand.docTitle, page, dark: true });
  return sl;
}

/* ── 지표 표 ──────────────────────────────────────────────────────────── */
function tableSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 34;

  const head = s.head.map((h, i) => ({
    text: h.t,
    options: { bold: true, color: C.navy, fontFace: F.kr, fontSize: pt(24),
      align: h.num ? 'right' : 'left', valign: 'bottom',
      margin: [2, 10, 9, 10], border: [
        { type: 'none' }, { type: 'none' },
        { type: 'solid', color: C.navy, pt: 2 }, { type: 'none' }] },
  }));
  const body = s.rows.map((r) => r.map((cell, i) => {
    const c = typeof cell === 'string' ? { t: cell } : cell;
    const h = s.head[i];
    return { text: c.t, options: {
      color: c.status ? statusColor(c.status).fg : (i === 0 ? C.text : C.text2),
      bold: i === 0 || h.num || !!c.strong,
      fontFace: h.num ? F.num : F.kr, fontSize: pt(25),
      align: h.num ? 'right' : 'left', valign: 'middle',
      fill: { color: C.card }, margin: [10, 10, 10, 10],
      border: [{ type: 'none' }, { type: 'none' },
               { type: 'solid', color: C.cardLine, pt: 0.75 }, { type: 'none' }],
    } };
  }));
  sl.addTable([head, ...body], {
    x: X(PAD.side), y: X(y), w: X(CW),
    colW: s.head.map((h) => X(CW * h.w)),
    rowH: X(s.rowH || 76), autoPage: false,
  });
  if (s.note) {
    txt(sl, s.note, { x: X(PAD.side), y: X(y + 76 * (s.rows.length + 1) + 20), w: X(CW), h: X(36),
      fontFace: F.kr, fontSize: pt(25), color: C.text3, valign: 'middle' });
  }
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

// HTML 의 .br-status--ok / --warn / --late 와 같은 값을 쓴다. 토큰이 한곳이므로
// blue-report.css 를 고치면 PowerPoint 판도 같이 바뀐다.
// 정상이 회색이던 시절에는 표를 훑을 때 좋은 신호와 나쁜 신호가 갈리지 않았다.
function statusColor(kind) {
  if (kind === 'warn') return { fg: C.warnText, bg: C.warnBg, line: C.warnLine };
  if (kind === 'late') return { fg: C.alertText, bg: C.alertBg, line: C.alertLine };
  return { fg: C.okText, bg: C.okBg, line: C.okLine };
}


/* ── 막대 차트 (네이티브) ─────────────────────────────────────────────── */
function barSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 34;

  // 값이 클수록 진한 단조 램프. 구간이 6개 이상이면 7단계 보간 램프를 쓴다.
  const ramp = s.values.length > 5 ? C.bar : C.data;
  const colors = s.values.map((_, i) => ramp[Math.min(i, ramp.length - 1)]);

  const h = H - y - PAD.bottom - 60 - (s.callout ? 120 : 0);
  sl.addChart(pres.ChartType.bar, [{ name: s.seriesName || '값', labels: s.categories, values: s.values }], {
    x: X(PAD.side), y: X(y), w: X(CW), h: X(h),
    barDir: 'col', barGapWidthPct: 40,
    chartColors: colors,
    showValue: true, dataLabelPosition: 'outEnd',
    dataLabelFontFace: F.num, dataLabelFontSize: pt(32), dataLabelColor: C.text,
    dataLabelFormatCode: s.labelFormat || '0.#',
    showLegend: false, showTitle: false,
    catAxisLabelFontFace: F.kr, catAxisLabelFontSize: pt(25), catAxisLabelColor: C.text,
    catAxisLineShow: false, catGridLine: { style: 'none' },
    valAxisHidden: true, valGridLine: { style: 'none' },
    valAxisMaxVal: s.max, valAxisMinVal: 0,
    border: { pt: 0, color: C.page }, fill: C.page,
  });
  // 막대만으로 말할 수 없는 단서 — 값이 0 이 아니라 측정 자체가 없다는 것 같은 —
  // 를 붙인다. HTML 덱은 같은 자리에 .br-callout 을 둔다.
  if (s.callout) {
    const cy = y + h + 10;
    sl.addShape('roundRect', { x: X(PAD.side), y: X(cy), w: X(CW), h: X(96), rectRadius: 0.1,
      fill: { color: C.warnBg }, line: { color: C.warnLine, width: 0.75 } });
    txt(sl, s.callout, { x: X(PAD.side + 30), y: X(cy), w: X(CW - 60), h: X(96),
      fontFace: F.kr, fontSize: pt(25), color: C.warnText, valign: 'middle', lineSpacingMultiple: 1.4 });
  }
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 도넛 차트 (네이티브) + 도넛 밖 범례 ──────────────────────────────── */
function donutSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 34;

  const colH = H - y - PAD.bottom - 50;
  const half = (CW - 34) / 2;

  card(sl, { x: PAD.side, y, w: half, h: colH });
  txt(sl, s.chartTitle, { x: X(PAD.side), y: X(y + 34), w: X(half), h: X(40),
    align: 'center', valign: 'middle', fontFace: F.kr, fontSize: pt(30), bold: true, color: C.text });

  const d = Math.min(half - 200, colH - 220);
  sl.addChart(pres.ChartType.doughnut,
    [{ name: s.chartTitle, labels: s.segments.map((g) => g.name), values: s.segments.map((g) => g.value) }], {
      x: X(PAD.side) + (X(half) - X(d)) / 2, y: X(y + 90), w: X(d), h: X(d),
      chartColors: s.segments.map((_, i) => C.data[i]),
      holeSize: 55, showLegend: false, showTitle: false, showValue: false,
      dataBorder: { pt: 1, color: C.card },
    });

  // 범례는 도넛 밖. 좁은 홀에 텍스트를 넣지 않는다.
  const segW = half / s.segments.length;
  s.segments.forEach((g, i) => {
    const gx = PAD.side + i * segW;
    const ly = y + colH - 130;
    sl.addShape('ellipse', { x: X(gx + segW / 2 - 60), y: X(ly + 10), w: X(16), h: X(16),
      fill: { color: C.data[i] }, line: { type: 'none' } });
    txt(sl, g.name, { x: X(gx + segW / 2 - 36), y: X(ly), w: X(segW / 2 + 100), h: X(36),
      fontFace: F.kr, fontSize: pt(24), bold: true, color: C.text, valign: 'middle' });
    txt(sl, [{ text: String(g.value), options: {} }, { text: '%', options: { fontSize: pt(16) } }], {
      x: X(gx), y: X(ly + 40), w: X(segW), h: X(36),
      align: 'center', fontFace: F.num, fontSize: pt(24), bold: true, color: C.cobalt, valign: 'middle' });
  });

  // 오른쪽 해설 + 주의 콜아웃
  const rx = PAD.side + half + 34;
  const noteH = s.callout ? 190 : 0;
  const panelH = colH - (noteH ? noteH + 26 : 0);
  card(sl, { x: rx, y, w: half, h: panelH });
  txt(sl, s.asideTitle, { x: X(rx + 34), y: X(y + 40), w: X(half - 68), h: X(40),
    fontFace: F.kr, fontSize: pt(30), bold: true, color: C.text, valign: 'middle' });
  s.aside.forEach((a, i) => {
    const ay = y + 110 + i * ((panelH - 130) / s.aside.length);
    sl.addShape('line', { x: X(rx + 34), y: X(ay), w: X(half - 68), h: 0,
      line: { color: C.cardLine, width: 0.75 } });
    txt(sl, [{ text: a.k + ' — ', options: {} }, { text: a.v, options: { bold: true, color: C.text } }], {
      x: X(rx + 34), y: X(ay + 12), w: X(half - 68), h: X(56),
      fontFace: F.kr, fontSize: pt(25), color: C.text2, valign: 'middle' });
  });
  if (s.callout) {
    const cy = y + panelH + 26;
    sl.addShape('roundRect', { x: X(rx), y: X(cy), w: X(half), h: X(noteH), rectRadius: 0.125,
      fill: { color: C.warnBg }, line: { color: C.warnLine, width: 0.75 } });
    txt(sl, s.callout, { x: X(rx + 30), y: X(cy), w: X(half - 60), h: X(noteH),
      fontFace: F.kr, fontSize: pt(25), color: C.warnText, valign: 'middle', lineSpacingMultiple: 1.4 });
  }
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 비교 2열 ─────────────────────────────────────────────────────────── */
/* 공유 트랙형 — 계획 대비 실적.
   카드 둘로 갈라 좌우를 오가게 하지 않는다. 트랙 전체가 계획, 채워진 부분이 실적이다.
   HTML 판(.br-bars-h + .br-bar-sub)과 같은 조판이다. */
function progressSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 40;

  // 합계 두 개를 나란히. 계획은 물리고 실적만 브랜드색으로 세운다.
  let tx = PAD.side;
  (s.totals || []).forEach((t) => {
    txt(sl, t.label, { x: X(tx), y: X(y), w: X(300), h: X(34),
      fontFace: F.kr, fontSize: pt(24), bold: true, color: C.text2, valign: 'middle' });
    txt(sl, [{ text: t.value, options: {} },
             ...(t.sup ? [{ text: t.sup, options: { fontSize: pt(28) } }] : [])], {
      x: X(tx), y: X(y + 46), w: X(300), h: X(80),
      fontFace: F.num, fontSize: pt(64), bold: true, valign: 'middle',
      color: t.muted ? C.text3 : C.cobalt });
    tx += 300;
  });
  if (s.caption) {
    txt(sl, s.caption, { x: X(tx), y: X(y + 60), w: X(CW - (tx - PAD.side)), h: X(50),
      fontFace: F.kr, fontSize: pt(25), color: C.text2, valign: 'middle' });
  }

  const top = y + 170;
  const avail = H - top - PAD.bottom - 40;
  const gap = avail / s.bars.length;
  const nameW = 320, valW = 260;
  const trackX = PAD.side + nameW + 30;
  const trackW = CW - nameW - valW - 60;
  s.bars.forEach((b, i) => {
    const by = top + i * gap;
    txt(sl, b.name, { x: X(PAD.side), y: X(by), w: X(nameW), h: X(44),
      fontFace: F.kr, fontSize: pt(25), bold: true, color: C.text, valign: 'middle' });
    sl.addShape('roundRect', { x: X(trackX), y: X(by + 8), w: X(trackW), h: X(26),
      rectRadius: 0.5, fill: { color: C.tint }, line: { type: 'none' } });
    sl.addShape('roundRect', { x: X(trackX), y: X(by + 8), w: X(trackW * b.pct / 100), h: X(26),
      rectRadius: 0.5, fill: { color: b.alert ? C.alertText : C.cobalt }, line: { type: 'none' } });
    txt(sl, [{ text: b.val, options: {} },
             { text: ' / ' + b.of, options: { fontSize: pt(20), color: C.text3 } }], {
      x: X(trackX + trackW + 20), y: X(by), w: X(valW - 20), h: X(40), align: 'right',
      fontFace: F.num, fontSize: pt(32), bold: true,
      color: b.alert ? C.alertText : C.cobalt, valign: 'middle' });
    txt(sl, b.sub, { x: X(trackX + trackW + 20), y: X(by + 42), w: X(valW - 20), h: X(30),
      align: 'right', fontFace: F.num, fontSize: pt(24),
      color: b.alert ? C.alertText : C.text3, valign: 'middle' });
  });
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

function compareSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 34;

  const colH = H - y - PAD.bottom - 50;
  const half = (CW - 34) / 2;
  [s.left, s.right].forEach((col, ci) => {
    const cx = PAD.side + ci * (half + 34);
    card(sl, { x: cx, y, w: half, h: colH });
    chip(sl, { x: cx + 34, y: y + 30, w: 30 + col.chip.length * 30, h: 58,
      text: col.chip, solid: col.solid !== undefined ? col.solid : ci === 1 });
    txt(sl, [{ text: col.stat, options: {} },
              ...(col.sup ? [{ text: col.sup, options: { fontSize: pt(32) } }] : [])], {
      x: X(cx + 34), y: X(y + 110), w: X(half - 68), h: X(90),
      fontFace: F.num, fontSize: pt(72), bold: true, valign: 'middle',
      color: (col.solid !== undefined ? col.solid : ci === 1) ? C.cobalt : C.text2 });
    txt(sl, col.sub, { x: X(cx + 34), y: X(y + 204), w: X(half - 68), h: X(40),
      fontFace: F.kr, fontSize: pt(25), color: C.text2, valign: 'middle' });

    if (col.items) {
      // 목록형 — 막대 대신 글머리 목록. 범위 · 항목 나열에 쓴다.
      const runs = col.items.map((it, k) => ([
        { text: it.k, options: { bold: true, color: C.text, paraSpaceAfter: 10 } },
        { text: ' — ' + it.v, options: { color: '45505C', breakLine: k < col.items.length - 1 } },
      ])).flat();
      sl.addText(runs, { isTextBox: true, margin: 0,
        x: X(cx + 34), y: X(y + 268), w: X(half - 68), h: X(colH - 300 - (col.note ? 120 : 0)),
        fontFace: F.kr, fontSize: pt(25), lineSpacingMultiple: 1.8, valign: 'top' });
      if (col.note) {
        const ny = y + colH - 130;
        sl.addShape('roundRect', { x: X(cx + 34), y: X(ny), w: X(half - 68), h: X(96),
          rectRadius: 0.125, fill: { color: C.warnBg }, line: { color: C.warnLine, width: 0.75 } });
        txt(sl, col.note, { x: X(cx + 60), y: X(ny), w: X(half - 120), h: X(96),
          fontFace: F.kr, fontSize: pt(25), color: C.warnText, valign: 'middle', lineSpacingMultiple: 1.4 });
      }
      return;
    }
    txt(sl, '지표별 상세', { x: X(cx + 34), y: X(y + 268), w: X(half - 68), h: X(40),
      fontFace: F.kr, fontSize: pt(26), bold: true, color: C.text2, valign: 'middle' });
    sl.addShape('line', { x: X(cx + 34), y: X(y + 316), w: X(half - 68), h: 0,
      line: { color: C.cardLine, width: 0.75 } });

    const rowTop = y + 352;
    const rowGap = (colH - (rowTop - y) - 40) / col.bars.length;
    const nameW = 240, valW = 120;
    const trackX = cx + 34 + nameW + 24;
    const trackW = half - 68 - nameW - valW - 48;
    col.bars.forEach((b, i) => {
      const by = rowTop + i * rowGap;
      txt(sl, b.name, { x: X(cx + 34), y: X(by), w: X(nameW), h: X(40),
        fontFace: F.kr, fontSize: pt(25), color: C.text, valign: 'middle' });
      sl.addShape('roundRect', { x: X(trackX), y: X(by + 6), w: X(trackW), h: X(28),
        rectRadius: 0.02, fill: { color: C.tint }, line: { type: 'none' } });
      sl.addShape('roundRect', { x: X(trackX), y: X(by + 6), w: X(trackW * b.pct / 100), h: X(28),
        rectRadius: 0.02, fill: { color: ci === 1 ? C.data[1] : C.data[3] }, line: { type: 'none' } });
      txt(sl, [{ text: b.val, options: {} },
                ...(b.sup ? [{ text: b.sup, options: { fontSize: pt(16) } }] : [])], {
        x: X(cx + half - 34 - valW), y: X(by), w: X(valW), h: X(40),
        align: 'right', valign: 'middle', fontFace: F.num, fontSize: pt(32), bold: true,
        color: ci === 1 ? C.navy : C.text2 });
    });
  });
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 3단계 로드맵 ─────────────────────────────────────────────────────── */
function roadmapSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  const y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold }) + 52;
  const colH = H - y - PAD.bottom - 50;
  const gap = 34, cw = (CW - gap * 2) / 3;

  s.steps.forEach((st, i) => {
    const cx = PAD.side + i * (cw + gap);
    const last = i === s.steps.length - 1;
    card(sl, { x: cx, y, w: cw, h: colH,
      fill: last ? C.navy : C.card, line: last ? C.navy : C.cardLine,
      dark: last, topBar: st.bar });
    chip(sl, { x: cx + cw / 2 - 90, y: y + 40, w: 180, h: 56, text: st.label,
      solid: true, fillColor: st.chipBg, lineColor: st.chipBg, color: st.chipFg,
      fontSize: 24 });
    txt(sl, st.name, { x: X(cx), y: X(y + 118), w: X(cw), h: X(60),
      align: 'center', valign: 'middle', fontFace: F.kr, fontSize: pt(48), bold: true, color: st.nameColor });

    const tagW = cw / Math.max(st.tags.length, 1) - 16;
    st.tags.forEach((t, ti) => {
      chip(sl, { x: cx + 24 + ti * (tagW + 12), y: y + 190, w: tagW, h: 48, text: t,
        fillColor: last ? C.navy : C.card,
        lineColor: last ? 'FFFFFF' : C.chipLine,
        color: last ? C.white : '45505C', fontSize: 24 });
    });

    const items = st.items.map((it, k) => ([
      { text: it.k, options: { bold: true, color: last ? C.white : C.text,
                               paraSpaceAfter: 10 } },
      { text: ' — ' + it.v, options: { color: last ? 'E8F1FD' : '45505C',
                                       breakLine: k < st.items.length - 1 } },
    ])).flat();
    sl.addText(items, { isTextBox: true, margin: 0,
      x: X(cx + 34), y: X(y + 262), w: X(cw - 68), h: X(colH - 262 - 90),
      fontFace: F.kr, fontSize: pt(24), lineSpacingMultiple: 1.55, valign: 'top' });

    sl.addShape('line', { x: X(cx + 34), y: X(y + colH - 76), w: X(cw - 68), h: 0,
      line: { color: last ? 'FFFFFF' : C.cardLine, width: 0.75 } });
    txt(sl, st.footK, { x: X(cx + 34), y: X(y + colH - 62), w: X(cw / 2), h: X(40),
      fontFace: F.kr, fontSize: pt(24), color: last ? 'E8F1FD' : C.text2, valign: 'middle' });
    txt(sl, st.footV, { x: X(cx + cw / 2 - 34), y: X(y + colH - 62), w: X(cw / 2), h: X(40),
      align: 'right', fontFace: F.kr, fontSize: pt(24), color: last ? 'E8F1FD' : C.text2, valign: 'middle' });
  });
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 일정 타임라인 ────────────────────────────────────────────────────── */
function timelineSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  let y = header(sl, { eyebrow: s.eyebrow, title: s.title, titleBold: s.titleBold });
  y = lede(sl, s.lede, { y: y + 22 }) + 40;

  const nameW = 300, gap = 28;
  const trackX = PAD.side + nameW + gap;
  const trackW = CW - nameW - gap;
  const n = s.cols.length;
  const colW = trackW / n;

  s.cols.forEach((c, i) => {
    txt(sl, c, { x: X(trackX + i * colW), y: X(y), w: X(colW), h: X(34),
      align: 'center', valign: 'middle', fontFace: F.label, fontSize: pt(24),
      bold: true, charSpacing: 2, color: C.text3 });
  });

  const rowsTop = y + 56;
  const mileH = 92;
  const rowsH = H - rowsTop - PAD.bottom - 50 - mileH;
  const rowStep = rowsH / s.rows.length;

  s.rows.forEach((r, i) => {
    const ry = rowsTop + i * rowStep + (rowStep - 46) / 2;
    txt(sl, r.name, { x: X(PAD.side), y: X(ry), w: X(nameW), h: X(46),
      fontFace: F.kr, fontSize: pt(25), bold: true, color: C.text, valign: 'middle' });
    const bx = trackX + (r.from - 1) * colW;
    const bw = (r.to - r.from + 1) * colW - 6;
    sl.addShape('roundRect', { x: X(bx), y: X(ry), w: X(bw), h: X(46), rectRadius: 0.02,
      fill: { color: C.data[Math.min(i, C.data.length - 1)] }, line: { type: 'none' } });
    txt(sl, r.label, { x: X(bx + 16), y: X(ry), w: X(bw - 32), h: X(46),
      fontFace: F.kr, fontSize: pt(24), bold: true, color: C.white, valign: 'middle' });
  });

  // 마일스톤은 막대 트랙 밖 별도 줄. 겹치지 않는다.
  const my = H - PAD.bottom - 50 - mileH + 22;
  sl.addShape('line', { x: X(PAD.side), y: X(my - 22), w: X(CW), h: 0,
    line: { color: C.cardLine, width: 0.75 } });
  txt(sl, s.mileLabel || '마일스톤', { x: X(PAD.side), y: X(my), w: X(nameW), h: X(40),
    fontFace: F.kr, fontSize: pt(25), bold: true, color: C.text3, valign: 'middle' });
  const mw = trackW / s.milestones.length;
  s.milestones.forEach((m, i) => {
    sl.addShape('ellipse', { x: X(trackX + i * mw), y: X(my + 13), w: X(14), h: X(14),
      fill: { color: C.coral }, line: { type: 'none' } });
    txt(sl, m, { x: X(trackX + i * mw + 24), y: X(my), w: X(mw - 24), h: X(40),
      fontFace: F.kr, fontSize: pt(24), bold: true, color: C.navy, valign: 'middle' });
  });
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 단일 수치 강조 ───────────────────────────────────────────────────── */
function bigStatSlide(pres, s, brand, page) {
  const sl = pres.addSlide();
  sl.background = { color: C.page };
  L.watermark(sl, brand, false);   // 본문보다 먼저 그려야 뒤에 깔린다
  txt(sl, s.title, { x: X(PAD.side), y: X(96), w: X(CW), h: X(80),
    fontFace: F.kr, fontSize: pt(62), bold: true, color: C.text, valign: 'middle', charSpacing: -1 });

  let y = 214;
  s.paras.forEach((para) => {
    const runs = [];
    para.forEach((ln, li) => {
      (Array.isArray(ln) ? ln : [ln]).forEach((seg) => {
        if (typeof seg === 'string') runs.push({ text: seg, options: {} });
        else runs.push({ text: seg.k, options: { bold: true, color: C.navy } });
      });
      if (li < para.length - 1) runs[runs.length - 1].options.breakLine = true;
    });
    sl.addText(runs, { isTextBox: true, margin: 0,
      x: X(PAD.side), y: X(y), w: X(CW), h: X(para.length * 52),
      fontFace: F.kr, fontSize: pt(28), color: '333E4A', lineSpacingMultiple: 1.7, valign: 'top' });
    y += para.length * 52 + 40;
  });

  if (s.callout) {
    sl.addShape('roundRect', { x: X(PAD.side), y: X(y), w: X(1100), h: X(90), rectRadius: 0.125,
      fill: { color: C.warnBg }, line: { color: C.warnLine, width: 0.75 } });
    txt(sl, s.callout, { x: X(PAD.side + 30), y: X(y), w: X(1040), h: X(90),
      fontFace: F.kr, fontSize: pt(25), color: C.warnText, valign: 'middle', lineSpacingMultiple: 1.4 });
  }

  const chipW = 60 + s.chipText.length * 28;
  chip(sl, { x: W - PAD.side - chipW, y: 656, w: chipW, h: 66, text: s.chipText, fontSize: 27 });
  txt(sl, [{ text: s.value, options: {} }, { text: s.sup, options: { fontSize: pt(88), color: C.data[3] } }], {
    x: X(W - PAD.side - 900), y: X(730), w: X(900), h: X(210),
    align: 'right', valign: 'middle', fontFace: F.num, fontSize: pt(200),
    bold: true, color: C.coral, charSpacing: -4 });
  footer(sl, { docTitle: brand.docTitle, page });
  return sl;
}

/* ── 마무리 — 목록형 / 행동 요청형 ────────────────────────────────────── */
function closingSlide(pres, s, brand) {
  const sl = pres.addSlide();
  sl.background = { color: C.cover };
  L.watermark(sl, brand, true);
  sl.addText([
    { text: s.titleSoft, options: { color: C.soft[1], breakLine: true } },
    { text: s.titleMain, options: { color: C.onDark } },
  ], { isTextBox: true, margin: 0,
    x: X(COVER_PAD.side), y: X(220), w: X(1300), h: X(240),
    fontFace: F.kr, fontSize: pt(96), bold: true, valign: 'middle', charSpacing: -3,
    lineSpacingMultiple: 1.18 });

  let y = 520;
  if (s.lede) {
    txt(sl, s.lede.join('\n'), { x: X(COVER_PAD.side), y: X(y), w: X(1300), h: X(s.lede.length * 48),
      fontFace: F.kr, fontSize: pt(28), color: C.onCover2, valign: 'top', lineSpacingMultiple: 1.7 });
    y += s.lede.length * 48 + 36;
  }
  if (s.cta) {
    sl.addShape('rect', { x: X(COVER_PAD.side), y: X(y), w: X(60 + s.cta.length * 34), h: X(78),
      fill: { color: C.page }, line: { type: 'none' } });
    txt(sl, s.cta, { x: X(COVER_PAD.side), y: X(y), w: X(60 + s.cta.length * 34), h: X(78),
      align: 'center', valign: 'middle', fontFace: F.kr, fontSize: pt(30), bold: true, color: C.cover });
  }
  (s.rows || []).forEach((r, i) => {
    const ry = y + i * 82;
    txt(sl, r.text, { x: X(COVER_PAD.side), y: X(ry), w: X(1200), h: X(60),
      fontFace: F.kr, fontSize: pt(30), color: C.onDark, valign: 'middle' });
    txt(sl, r.when, { x: X(W - COVER_PAD.side - 400), y: X(ry), w: X(400), h: X(60),
      align: 'right', valign: 'middle', fontFace: F.num, fontSize: pt(24), color: C.onCover2 });
    sl.addShape('line', { x: X(COVER_PAD.side), y: X(ry + 62), w: X(W - COVER_PAD.side * 2), h: 0,
      line: { color: C.onCover3, width: 0.75 } });
  });

  txt(sl, `© ${brand.copyrightYear} ${brand.company} · All rights reserved`, {
    x: X(COVER_PAD.side), y: X(960), w: X(900), h: X(30),
    fontFace: F.num, fontSize: pt(24), color: C.onCover3, valign: 'middle' });
  return sl;
}

module.exports = {
  cover, agenda, darkSummary, tableSlide, barSlide, donutSlide,
  progressSlide, compareSlide, roadmapSlide, timelineSlide, bigStatSlide, closingSlide,
  statusColor, W, H,
};
