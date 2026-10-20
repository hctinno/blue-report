'use strict';
/**
 * 블루 리포트 PowerPoint 판 생성기.
 *
 *   node build.js --brand ../../../brand/hct/brand.json --out ./dist
 *
 * --brand 경로는 어디서 실행하느냐에 따라 다르다.
 *   저장소 스킬 폴더에서   ../../../brand/hct/brand.json
 *   저장소 루트에서        brand/hct/brand.json
 *   계정 스킬 설치본에서   brand/hct/brand.json
 *   node build.js --brand brand.json --deck internal
 *
 * 색·크기는 assets/blue-report.css 에서 읽는다(tokens.js). 여기 다시 적지 않는다.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// 의존성이 없으면 여기서 알아서 받는다. 사용자가 미리 npm install 할 필요가 없다.
if (!fs.existsSync(path.join(__dirname, 'node_modules', 'pptxgenjs'))) {
  if (process.env.BLUE_REPORT_NO_INSTALL) {
    console.error(`[준비 필요] PPTX 생성기 의존성이 없다.\n  실행: cd ${__dirname} && npm install`);
    process.exit(1);
  }
  console.error('[준비] PPTX 생성기 의존성 설치 — 처음 한 번만');
  try {
    execFileSync('npm', ['install', '--silent', '--prefix', __dirname], { stdio: 'inherit' });
  } catch (e) {
    console.error(`[준비 실패] npm install 이 실패했다.\n  직접 실행: cd ${__dirname} && npm install`);
    process.exit(1);
  }
}

const PptxGenJS = require('pptxgenjs');
const { C } = require('./tokens');
const S = require('./slides');
const L = require('./layouts');
const CONTENT = require('./content');

function loadBrand(p) {
  const b = JSON.parse(fs.readFileSync(p, 'utf8'));
  const dir = path.dirname(path.resolve(p));
  // 로고는 두 벌이다. 어두운 면에는 흰색 녹아웃, 밝은 면에는 원색을 쓴다.
  // 비율은 파일마다 다르다. 워터마크는 국문을 뗀 심볼이라 마크보다 납작하다.
  // 한 곳에 모아 두면 나중에 읽은 값이 앞의 것을 덮어써 로고가 찌그러진다.
  const resolveLogo = (rel, label) => {
    if (!rel) return null;
    const abs = path.isAbsolute(rel) ? rel : path.join(dir, rel);
    if (!fs.existsSync(abs)) {
      console.error(`주의: ${label} 로고 파일이 없어 워드마크 텍스트로 대체한다 — ${abs}`);
      return null;
    }
    const dim = pngSize(abs);
    return { path: abs, ratio: dim ? dim.w / dim.h : null };
  };
  const dark = resolveLogo(b.logo, '다크면용');
  const light = resolveLogo(b.logoOnLight, '밝은면용');
  const wm = resolveLogo(b.watermark, '워터마크용');

  b.logoPath = dark && dark.path;
  b.logoPathOnLight = light && light.path;
  // 우측 상단 마크의 비율. 다크면용을 기준으로 잡고 없으면 밝은면용을 쓴다.
  b.logoRatio = (dark && dark.ratio) || (light && light.ratio) || 3.07;
  // 배경 워터마크. 따로 주지 않으면 다크면용 로고를 그대로 키워 쓴다 (HTML 과 같은 규칙).
  b.watermarkPath = (wm && wm.path) || b.logoPath;
  b.watermarkRatio = (wm && wm.ratio) || b.logoRatio;
  const wmL = resolveLogo(b.watermarkOnLight, '밝은면 워터마크용');
  b.watermarkPathOnLight = (wmL && wmL.path) || b.logoPathOnLight;
  b.watermarkRatioOnLight = (wmL && wmL.ratio) || b.logoRatio;
  if (b.logoPath && !b.logoPathOnLight) {
    console.error('주의: logoOnLight 가 없다. 흰색 로고는 밝은 지면에서 보이지 않으므로 '
      + '밝은 슬라이드는 워드마크 텍스트로 둔다.');
  }
  b.wordmark = b.wordmark || b.company;
  b.logoHeight = b.logoHeight || 40;
  return b;
}

/** PNG 헤더에서 크기를 읽는다. 로고 비율 계산용. */
function pngSize(file) {
  const buf = fs.readFileSync(file);
  if (buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) return null;
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

const BUILDERS = {
  cover: S.cover, agenda: S.agenda, darkSummary: S.darkSummary, table: S.tableSlide,
  bar: S.barSlide, donut: S.donutSlide, compare: S.compareSlide, progress: S.progressSlide,
  roadmap: S.roadmapSlide, timeline: S.timelineSlide, bigStat: S.bigStatSlide,
  closing: S.closingSlide,
};

function buildDeck(deck, brand, outDir) {
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';          // 슬라이드를 추가하기 전에 설정해야 좌표가 맞는다
  pres.author = brand.company;
  pres.company = brand.company;
  pres.title = deck.docTitle;

  const b = Object.assign({}, brand, { docTitle: deck.docTitle });
  deck.slides.forEach((s, i) => {
    const fn = BUILDERS[s.type];
    if (!fn) throw new Error(`알 수 없는 슬라이드 종류: ${s.type}`);
    const sl = fn(pres, s, b, i + 1);
    L.mark(sl, b);                       // 우측 상단 브랜드 마크 — 빠짐없이 모든 장에
    if (s.notes) sl.addNotes(s.notes);   // 발표자 노트는 노트 창에만 들어간다
  });

  fs.mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, deck.file);
  return pres.writeFile({ fileName: out }).then(() => {
    const kb = fs.statSync(out).size / 1024;
    console.log(`  ${path.basename(out)}  ${deck.slides.length}장  ${kb.toFixed(0)}KB`);
    return out;
  });
}

async function main() {
  const args = process.argv.slice(2);
  const get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
  const brandPath = get('--brand');
  if (!brandPath) { console.error('사용법: node build.js --brand <brand.json> [--deck 이름] [--out 폴더]'); process.exit(1); }
  const brand = loadBrand(brandPath);
  const outDir = path.resolve(get('--out', path.join(__dirname, '..', 'dist', 'pptx')));
  const only = get('--deck');

  const decks = Object.entries(CONTENT).filter(([k, v]) => v && v.slides && (!only || k === only));
  if (!decks.length) { console.error(`덱을 찾지 못했다: ${only}`); process.exit(1); }

  console.log(`회사: ${brand.company} · 마크: 다크면 ${brand.logoPath ? '로고' : '워드마크'} · 밝은면 ${brand.logoPathOnLight ? '로고' : '워드마크'} (우측 상단)`);
  for (const [, deck] of decks) await buildDeck(deck, brand, outDir);
  console.log(`\n출력 폴더: ${outDir}`);
}

main().catch((e) => { console.error('실패:', e.message); process.exit(1); });
