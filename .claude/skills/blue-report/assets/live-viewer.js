// 라이브 덱 뷰어 — 사내 발표 덱의 발표 기능을 한 파일에 담는다.
//
// 이 계통은 **JS 없이 열어도 전부 읽힌다.** 세로로 스크롤하면 그만이다. 배율과
// 넘김은 CSS 가 한다 — 루트 글자 크기가 clamp 로 따라가고 넘김은 scroll-snap 이 한다.
// 여기서는 JS 로만 되는 것을 한다. 단계 전개를 기본으로 접지 않는 이유도 같다.
//
//   넘김      ← → ↑ ↓ · PgUp PgDn · Space · Home End · 발표 중 화면 클릭 · 가로 보기 휠 · 밀기
//   단계      data-f="1" 부터. 같은 번호는 함께 열린다. 번호를 건너뛰어도 된다
//   쪽 이동   숫자 + Enter = 그 쪽번호. 0 = 표지. a(ㅁ) 를 먼저 누르면 부록 쪽번호
//   단축키    파워포인트 슬라이드 쇼를 따른다 — F5 처음부터 · Shift+F5 이 장부터 · Alt+F5 발표자
//             보기 · B 검은 화면 · W 흰 화면 · P(Ctrl+P) 펜 · Ctrl+I 형광펜 · Ctrl+E 지우개 ·
//             E 필기 지우기 · Ctrl+M 필기 숨김 · Ctrl+A 펜 끄기 · Ctrl+L 레이저 · F1 도움말.
//             우리 기능은 빈 글자에 — M 메모 · X 펼침 · V 가로. 표 KEYMAP 이 한 곳이고, 덱의
//             <script type="application/json" id="bl-keys"> 로 바꿀 수 있다
//   발표 중   레이저가 저절로 켜지고 커서 · 조작판 · 진행선이 숨는다. 화면 아래 끝에
//             마우스를 대면 조작판이 잠깐 보인다. 창을 화면 크기로 키우거나 F11 을 눌러도
//             발표 모드로 들어간다
//   대본 창   data-notes 를 마크다운으로 — **굵게** · [클릭] 배지 · → 전환: · ※ 메모.
//             장별 배정 시간(분당 300자) · 타이머 · 편집(이 브라우저에 저장) · 내보내기.
//             팝업이 막히면 같은 창 오른쪽에 연다
//   근거      .bl-ev[data-ev="E1,E2"] → 근거 패널. 근거가 여럿이면 탭, 캡처가 있으면
//             확대 · 끌기 · 하이라이트 상자로 바로 가는 뷰어
//   겹창      [data-peek="장 id"] 부록 겹쳐 보기 · [data-doc] 원문 · [data-video] 영상 ·
//             .bl-fig · .bl-shot 그림 크게 보기
//   부품      탭 · 세그먼트 · 시안 토글 · 노선도 · 장면 · 초점 행 · 카드 고르기 · 도넛 ·
//             조작형 누적 막대 · 와플 · 시뮬레이션 · 카운트업 · 다시 재생
//   이벤트    document 에 deck:sync{el,cur,list,step,steps,staged} · deck:present{on} ·
//             deck:presenter{open} · deck:laser{on}
//
// 장 전용 스크립트는 이 파일 **뒤에** 둔다. 그래야 그 스크립트가 장 안 요소에 단 클릭
// 처리기가 발표 중 「화면 클릭 = 다음」에서 저절로 빠진다(data-int 표시).

(function () {
  'use strict';
  var deck = document.getElementById('deck');
  if (!deck) return;
  var D = document, R = D.documentElement, B = D.body, W = window;
  var slides = Array.prototype.slice.call(deck.querySelectorAll('.bl-sl'));
  if (!slides.length) return;
  var deckTitle = deck.getAttribute('data-deck-title') || D.title || '';
  if (!deck.hasAttribute('tabindex')) deck.tabIndex = 0;   // 키를 받으려면 초점을 받을 수 있어야 한다
  var mqReduce = W.matchMedia ? W.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function reduced() { return !!mqReduce.matches; }
  // 숨김 상태(장에 들어오기 전 모습)는 이 표시가 있을 때만 건다. JS 가 없으면 전부 보인다
  R.classList.add('bl-anim');

  // ── 도구 ──────────────────────────────────────────────────────────────
  function $(sel, el) { return (el || D).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || D).querySelectorAll(sel)); }
  function mk(tag, cls, text) {
    var e = D.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function emit(name, detail) {
    try { D.dispatchEvent(new CustomEvent(name, { detail: detail })); } catch (e) { /* 옛 브라우저 */ }
  }
  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function mmss(sec) { sec = Math.max(0, Math.round(sec)); return Math.floor(sec / 60) + ':' + pad2(sec % 60); }
  function stamp() {
    var z = new Date();
    return z.getFullYear() + pad2(z.getMonth() + 1) + pad2(z.getDate()) + '_' + pad2(z.getHours()) + pad2(z.getMinutes());
  }
  function fileBase() { return (deckTitle || '덱').replace(/[\\/:*?"<>|]+/g, ' ').trim() || '덱'; }

  // 장 안 요소에 클릭 처리기를 다는 장 전용 스크립트가 있으면 그 요소에 data-int 를 단다.
  // 발표 중 화면 클릭이 「다음」인데, 단추를 누른 것까지 다음으로 넘어가면 안 된다.
  (function () {
    var proto = W.EventTarget && W.EventTarget.prototype;
    if (!proto || proto.__blWrapped) return;
    var add = proto.addEventListener;
    proto.addEventListener = function (type, fn, opt) {
      try {
        if ((type === 'click' || type === 'pointerdown' || type === 'mousedown') && this && this.nodeType === 1 &&
            this.closest && this.closest('.bl-sl') && !this.classList.contains('bl-sl') &&
            !this.classList.contains('bl-bd')) this.setAttribute('data-int', '1');
      } catch (e) { /* 무시 */ }
      return add.call(this, type, fn, opt);
    };
    proto.__blWrapped = true;
  })();

  // 클릭해도 「다음」으로 넘어가지 않는 것들
  var INTERACTIVE = 'a,button,input,select,textarea,label,summary,details,[data-int],[role="button"],' +
    '[role="tab"],[aria-pressed],.bl-ev,[data-pick],[data-peek],[data-doc],[data-video],[data-zoom],' +
    '.bl-route-st,.bl-donut-s,.bl-donut-leg li,.bl-fig > img,.bl-fig > svg,.bl-shot-img img,.bl-focusset [data-i]';

  // ── 쪽번호 ────────────────────────────────────────────────────────────
  // 표지는 번호가 없다. 본문은 「NN / 전체」, 부록 간지는 「부록」, 부록은 따로
  // 「부록 NN / 전체」로 센다. 같은 자리에 다른 체계가 찍히는 것이 부록으로
  // 넘어왔다는 신호다 — 사내 발표 덱과 같은 규약이다.
  function kind(s) {
    if (s.classList.contains('bl-sl--cover')) return 'cover';
    if (s.classList.contains('bl-sl--apxdiv')) return 'apxdiv';
    if (s.hasAttribute('data-apx')) return 'apx';
    return 'body';
  }
  var bodyList = slides.filter(function (s) { return kind(s) === 'body'; });
  var apxList = slides.filter(function (s) { return kind(s) === 'apx'; });
  var coverSlide = slides.filter(function (s) { return kind(s) === 'cover'; })[0] || slides[0];
  function pgOf(s) {
    var k = kind(s);
    if (k === 'cover') return '';
    if (k === 'apxdiv') return '부록';
    if (k === 'apx') return '부록 ' + pad2(apxList.indexOf(s) + 1) + ' / ' + pad2(apxList.length);
    return pad2(bodyList.indexOf(s) + 1) + ' / ' + pad2(bodyList.length);
  }
  slides.forEach(function (s) {
    var pg = s.querySelector('.bl-pg');
    if (pg) pg.textContent = pgOf(s);
    var nm = s.querySelector('.bl-rf-name');
    if (nm && !nm.textContent.trim()) nm.textContent = deckTitle;
  });
  function titleOf(s) {
    var t = s.getAttribute('data-t');
    if (t) return t;
    var h = s.querySelector('.bl-title, .bl-fin-l2, .bl-qa-q, h1, h2');
    var tt = h ? h.textContent.replace(/\s+/g, ' ').trim() : '';
    if (!tt) { var c = s.querySelector('.bl-code'); tt = c ? c.textContent.replace(/\s+/g, ' ').trim() : ''; }
    return tt;
  }
  function labelOf(s) { var p = pgOf(s); return (p ? p.split(' / ')[0] : '표지') + ' · ' + titleOf(s); }
  function keyOf(s) { return s.id || s.getAttribute('data-t') || ('p' + (slides.indexOf(s) + 1)); }

  // ── 단계 ──────────────────────────────────────────────────────────────
  // 장마다 단계 값 목록(고유 data-f 오름차순)과 「몇 단계까지 열었나」를 따로 쥔다.
  // 장을 옮겨도 그 장의 상태가 남아, 지나가는 장이 펼쳐진 채 번쩍이지 않는다.
  var i = 0;
  var stepAt = slides.map(function () { return 0; });
  function levels(s) {
    if (s.__blLv) return s.__blLv;
    var seen = {}, out = [];
    $$('[data-f]', s).forEach(function (el) {
      var n = parseFloat(el.getAttribute('data-f'));
      if (n > 0 && !seen[n]) { seen[n] = 1; out.push(n); }
    });
    out.sort(function (a, b) { return a - b; });
    s.__blLv = out;
    return out;
  }
  // 단계를 접어 두는가. 발표 모드에서는 언제나 접는다. 검토 중에도 펼침(E)을
  // 끄면 접는다 — 발표 전에 클릭 순서를 미리 밟아 보는 용도다.
  function staged() {
    return deck.classList.contains('bl-deck--present') || deck.classList.contains('bl-deck--collapse');
  }
  function threshold(k) {
    var lv = levels(slides[k]);
    return stepAt[k] ? lv[stepAt[k] - 1] : 0;
  }
  function paintSteps() {
    var st = staged();
    deck.classList.toggle('bl-deck--staged', st);
    slides.forEach(function (s, k) {
      var lv = levels(s);
      if (!lv.length) return;
      var th = st ? threshold(k) : Infinity;
      $$('[data-f]', s).forEach(function (el) {
        var n = parseFloat(el.getAttribute('data-f')) || 0;
        el.classList.toggle('is-shown', n <= th);
      });
      s.setAttribute('data-step', st ? stepAt[k] : lv.length);
    });
  }
  function stepFwd() {
    if (!staged()) return false;
    if (stepAt[i] >= levels(slides[i]).length) return false;
    stepAt[i]++; sync(); return true;
  }
  function stepBack() {
    if (!staged() || stepAt[i] <= 0) return false;
    stepAt[i]--; sync(); return true;
  }

  // ── 동기화 ────────────────────────────────────────────────────────────
  var WIDGETS = [];
  function sync() {
    paintSteps();
    var s = slides[i], lv = levels(s);
    var lbl = pgOf(s) || '표지';
    var st = staged() && lv.length ? ' · ' + stepAt[i] + '/' + lv.length : '';
    $$('.bl-hud [data-pg]').forEach(function (el) { el.textContent = lbl + st; });
    paintProg(); paintNotes(); paintToggles(); presenterPaint(false);
    var ctx = { staged: staged() };
    WIDGETS.forEach(function (w) {
      try { w.sync(w.slide === s, ctx); } catch (e) { if (W.console) console.warn(e); }
    });
    peekSeqReset();
    emit('deck:sync', { el: s, cur: i, list: slides, step: stepAt[i], steps: lv.length, staged: staged() });
  }

  // ── 장 이동 ───────────────────────────────────────────────────────────
  // 스크롤은 브라우저가 한다. 어디에 와 있는지는 관찰로 알아낸다 — scroll 이벤트로
  // 좌표를 재면 스냅 도중 값이 튄다. 옮기라고 시킨 직후에는 지나가는 장을 무시한다.
  var pending = null;
  function goTo(k, opt) {
    opt = opt || {};
    k = clamp(k, 0, slides.length - 1);
    stepAt[k] = opt.fromEnd ? levels(slides[k]).length : 0;
    pending = { k: k, t: Date.now() };
    var smooth = !!opt.smooth && !reduced();
    try { slides[k].scrollIntoView({ block: 'start', inline: 'start', behavior: smooth ? 'smooth' : 'auto' }); }
    catch (e) { slides[k].scrollIntoView(); }
    i = k;
    markIn(slides[k]);
    sync();
  }
  function next() { if (!stepFwd() && i < slides.length - 1) goTo(i + 1, { smooth: true }); }
  function prev() { if (!stepBack() && i > 0) goTo(i - 1, { smooth: true, fromEnd: staged() }); }
  function realign() {
    requestAnimationFrame(function () { slides[i].scrollIntoView({ block: 'start', inline: 'start' }); });
  }

  // 장이 처음 화면의 55% 를 넘으면 .in 을 단다. 떼지 않는다 — 돌아와도 다시 재생하지
  // 않는다. 숫자 카운트업도 이때 한 번 돈다.
  function markIn(s) {
    if (s.classList.contains('in')) return;
    s.classList.add('in');
    $$('[data-count]', s).forEach(countUp);
  }
  if (W.IntersectionObserver) {
    // 좁은 창에서는 장이 내용만큼 늘어나 화면보다 길 수 있다. 그런 장은 자기 높이의 55% 가
    // 한 번에 보이지 않으므로 「화면의 55% 를 덮었는가」도 함께 본다. 문턱을 촘촘히 둬야
    // 긴 장을 스크롤하는 동안에도 판정이 다시 돈다.
    var TH = [];
    for (var t = 0; t <= 20; t++) TH.push(t / 20);
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var rb = e.rootBounds, cover = rb && rb.height ? e.intersectionRect.height / rb.height : 0;
        if (e.intersectionRatio < .55 && cover < .55) return;
        var k = slides.indexOf(e.target);
        if (k < 0) return;
        markIn(e.target);
        if (k === i) return;
        if (pending && pending.k !== k && Date.now() - pending.t < 1200) return;
        pending = null;
        stepAt[k] = 0; i = k; sync();
      });
    }, { root: deck, threshold: TH });
    slides.forEach(function (s) { io.observe(s); });
  } else {
    slides.forEach(markIn);
  }

  // ── 진행선 ────────────────────────────────────────────────────────────
  function paintProg() {
    var el = D.getElementById('bl-prog');
    if (!el) return;
    el.style.width = (slides.length > 1 ? i / (slides.length - 1) * 100 : 100) + '%';
  }

  // ── 겹창 쌓기 ─────────────────────────────────────────────────────────
  // 겹창이 열려 있는 동안 키는 겹창 것이다. 아래 덱으로 새지 않는다 — 원문을 보다가
  // → 를 눌렀는데 뒤에서 장이 넘어가 있으면 발표가 무너진다.
  var modals = [];
  function topModal() { return modals[modals.length - 1]; }
  function pushModal(m) {
    if (modals.indexOf(m) < 0) modals.push(m);
    B.classList.add('bl-modal');
  }
  function popModal(m) {
    var k = modals.indexOf(m);
    if (k >= 0) modals.splice(k, 1);
    if (!modals.length) B.classList.remove('bl-modal');
  }
  function trapTab(e, root) {
    var f = $$('button:not([disabled]),a[href],[tabindex]:not([tabindex="-1"]),textarea,input,select', root)
      .filter(function (x) { return x.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && D.activeElement === first) { last.focus(); e.preventDefault(); }
    else if (!e.shiftKey && D.activeElement === last) { first.focus(); e.preventDefault(); }
    else if (!root.contains(D.activeElement)) { first.focus(); e.preventDefault(); }
  }

  // ── 알림 ──────────────────────────────────────────────────────────────
  var toastEl = null, toastT = 0;
  function toast(msg) {
    if (!toastEl) {
      toastEl = mk('div'); toastEl.id = 'bl-toast';
      toastEl.setAttribute('role', 'status'); toastEl.hidden = true;
      B.appendChild(toastEl);
    }
    toastEl.textContent = msg; toastEl.hidden = false;
    clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.hidden = true; }, 2600);
  }

  // ── 발표 모드 · 전체화면 ──────────────────────────────────────────────
  // F 는 전체화면을 요청한다. 대본 창은 P 로 따로 연다 — 브라우저는 사용자 동작 하나에
  // 팝업과 전체화면 중 하나만 허락한다. 사내 발표 덱은 둘을 한 번에 열다가 팝업이
  // 열리면 전체화면이 조용히 실패했다. 대본 창을 먼저 열어 두고 F 를 누르면 둘 다 된다.
  var fsMode = null, fsOptOut = false;
  function inFS() { return !!(D.fullscreenElement || D.webkitFullscreenElement); }
  function sizeFull() {
    var s = W.screen || {};
    return !!(s.width && W.innerWidth >= s.width - 2 && W.innerHeight >= s.height - 2);
  }
  var baseFull = sizeFull();      // 처음부터 화면 크기로 열린 창(키오스크 · 헤드리스)은 크기로 판정하지 않는다
  function looksFull() {
    if (inFS()) return true;
    try { if (W.matchMedia('(display-mode: fullscreen)').matches) return true; } catch (e) { /* 무시 */ }
    return !baseFull && sizeFull();
  }
  function isPresent() { return deck.classList.contains('bl-deck--present'); }
  function setPresent(on) {
    deck.classList.toggle('bl-deck--present', on);
    B.classList.toggle('present', on);
    B.classList.remove('peek');
    stepAt[i] = 0;
    if (!on) { setTool(null); setBlank(null); }
    setLaser(on);
    if (on) timerReset();
    sync();
    realign();
    emit('deck:present', { on: on });
    if (on) { try { deck.focus({ preventScroll: true }); } catch (e) { /* 무시 */ } }
  }
  function enterPresent(fromFs) {
    if (isPresent()) return;
    fsMode = fromFs || null;
    setPresent(true);
    if (fromFs) return;
    var req = R.requestFullscreen || R.webkitRequestFullscreen;
    if (!req) return;
    try {
      var r = req.call(R);
      fsMode = 'api';
      if (r && r.catch) r.catch(function () { fsMode = null; });
    } catch (e) { fsMode = null; }
  }
  function exitPresent() {
    if (!isPresent()) return;
    if (inFS()) {
      fsMode = null;
      var ex = D.exitFullscreen || D.webkitExitFullscreen;
      if (ex) { try { ex.call(D); } catch (e) { /* 무시 */ } }
    } else if (looksFull()) {
      fsOptOut = true;            // 전체화면은 그대로 두고 발표만 끈 경우 — 다시 들어가지 않는다
    }
    fsMode = null;
    setPresent(false);
  }
  function togglePresent() { if (isPresent()) exitPresent(); else enterPresent(null); }
  function fsCheck() {
    var full = looksFull();
    if (full) {
      if (!isPresent() && !fsOptOut) enterPresent(inFS() ? 'api' : 'auto');
    } else {
      fsOptOut = false;
      if (isPresent() && (fsMode === 'auto' || fsMode === 'api')) { fsMode = null; setPresent(false); }
    }
  }
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
    D.addEventListener(ev, function () {
      if (!inFS() && isPresent() && fsMode === 'api') { fsMode = null; setPresent(false); return; }
      fsCheck();
    });
  });
  var rsT = 0;
  W.addEventListener('resize', function () {
    clearTimeout(rsT);
    rsT = setTimeout(fsCheck, 450);
    fitPeek(); EVP.view && EVP.view.resize();
  });

  // 발표 중 조작판 엿보기 — 화면 아래 끝에 마우스를 대면 잠깐 보인다
  var peekT = 0;
  D.addEventListener('mousemove', function (e) {
    if (laserOn && !tool) placeLaser(e.clientX, e.clientY);
    if (!isPresent()) return;
    var near = e.clientY > W.innerHeight - 78;
    if (near) { clearTimeout(peekT); B.classList.add('peek'); }
    else if (B.classList.contains('peek')) {
      clearTimeout(peekT);
      peekT = setTimeout(function () { B.classList.remove('peek'); }, 200);
    }
  });
  R.addEventListener('mouseleave', function () { B.classList.remove('peek'); if (laserEl) laserEl.classList.remove('is-in'); });
  W.addEventListener('blur', function () { if (laserEl) laserEl.classList.remove('is-in'); });

  // ── 레이저 ────────────────────────────────────────────────────────────
  var laserEl = null, laserOn = false;
  function setLaser(on) {
    laserOn = !!on;
    B.classList.toggle('laser', laserOn);
    if (laserOn && !laserEl) {
      laserEl = mk('div'); laserEl.id = 'bl-laser'; laserEl.setAttribute('aria-hidden', 'true');
      B.appendChild(laserEl);
      placeLaser(W.innerWidth / 2, W.innerHeight / 2);
    }
    if (laserEl) laserEl.classList.toggle('is-in', laserOn);
    emit('deck:laser', { on: laserOn });
    paintToggles();
  }
  function placeLaser(x, y) {
    if (!laserEl) return;
    laserEl.style.transform = 'translate(' + x + 'px,' + y + 'px)';
    laserEl.classList.add('is-in');
  }

  // ── 펼침 · 가로 ───────────────────────────────────────────────────────
  function toggleExpand() {
    var on = !deck.classList.contains('bl-deck--collapse');
    deck.classList.toggle('bl-deck--collapse', on);
    stepAt[i] = 0;
    sync();
  }
  function horizontal() {
    return deck.classList.contains('bl-deck--present') || deck.classList.contains('bl-deck--horiz');
  }
  function toggleHoriz() {
    deck.classList.toggle('bl-deck--horiz');
    realign();
    paintToggles();
  }

  // 가로 보기에서 휠 한 번 = 한 장. 연속 휠은 650ms 묶는다 — 관성 스크롤이 여러 장을 넘긴다
  var wheelLock = 0;
  deck.addEventListener('wheel', function (e) {
    if (topModal() || !horizontal()) return;
    e.preventDefault();
    var dx = e.deltaX, dy = e.deltaY;
    if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
    var now = Date.now();
    if (now < wheelLock) return;
    wheelLock = now + 650;
    var d = Math.abs(dx) > Math.abs(dy) ? dx : dy;
    goTo(i + (d > 0 ? 1 : -1), { smooth: true });
  }, { passive: false });

  // 세로 보기에서 옆으로 밀기 = 넘김(단계 포함). 가로 보기는 브라우저가 스냅으로 넘긴다
  var tx = 0, ty = 0, tOn = false;
  deck.addEventListener('touchstart', function (e) {
    tOn = e.touches.length === 1;
    if (tOn) { tx = e.touches[0].clientX; ty = e.touches[0].clientY; }
  }, { passive: true });
  deck.addEventListener('touchend', function (e) {
    if (!tOn || horizontal()) return;
    tOn = false;
    var t = e.changedTouches[0], dx = t.clientX - tx, dy = t.clientY - ty;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) { if (dx < 0) next(); else prev(); }
  }, { passive: true });

  // ── 대본 (발표자 노트) ────────────────────────────────────────────────
  // 노트 문법 — 빈 줄로 문단을 나눈다.
  //   [클릭]  이 자리에서 다음 단계로 넘긴다는 표시. 대본 창에 「클릭 n」 배지로 뜨고
  //           지금 단계와 맞춰 지난 것 · 다음 것을 칠한다
  //   **굵게**  강조
  //   → 전환: …   다음 장으로 넘어가는 말. 따로 상자로 뜬다
  //   ※ …         읽지 않는 메모. 배정 시간 계산에서 뺀다
  var ORIG = {}, EDIT = {};
  var LSKEY = 'bl-script:' + (deckTitle || location.pathname);
  slides.forEach(function (s) { ORIG[keyOf(s)] = s.getAttribute('data-notes') || ''; });
  function noteOf(k) { var s = slides[k]; return s ? (s.getAttribute('data-notes') || '') : ''; }
  function applyEdits() {
    slides.forEach(function (s) {
      var k = keyOf(s);
      s.setAttribute('data-notes', Object.prototype.hasOwnProperty.call(EDIT, k) ? EDIT[k] : ORIG[k]);
    });
    retime();
  }
  function persist() {
    try {
      if (Object.keys(EDIT).length) W.localStorage.setItem(LSKEY, JSON.stringify(EDIT));
      else W.localStorage.removeItem(LSKEY);
    } catch (e) { /* 개인 창 · 막힌 저장소 — 이번 창에서만 유지 */ }
  }
  (function () {
    try {
      var o = JSON.parse(W.localStorage.getItem(LSKEY) || '{}');
      Object.keys(o).forEach(function (k) {
        if (Object.prototype.hasOwnProperty.call(ORIG, k) && typeof o[k] === 'string') EDIT[k] = o[k];
      });
    } catch (e) { /* 무시 */ }
  })();

  function md(text, step) {
    var n = 0;
    return String(text || '').replace(/\r/g, '').split(/\n\s*\n/).map(function (p) {
      p = p.trim();
      if (!p) return '';
      var h = esc(p)
        .replace(/\*\*\[클릭\]\*\*|\[클릭\]/g, function () {
          n++;
          var c = n <= step ? ' done' : (n === step + 1 ? ' now' : '');
          return '<span class="k' + c + '">클릭 ' + n + '</span>';
        })
        .replace(/\*\*\[(넘김|임의)\]\*\*|\[(넘김|임의)\]/g, function (m, a, b) { return '<span class="k x">' + (a || b) + '</span>'; })
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
      if (/^→\s*전환\s*:/.test(p)) return '<div class="tr">' + h + '</div>';
      if (/^※/.test(p)) return '<div class="memo">' + h + '</div>';
      return '<p>' + h + '</p>';
    }).join('');
  }

  // 장별 배정 시간 — 읽는 글자 수를 분당 300자로 나눠 5초 단위로 올린다. 최소 20초.
  // 간지는 5초, 부록은 본 발표 시간에 넣지 않는다(0).
  var ALLOT = [], CUM = [];
  function spokenLen(t) {
    return String(t || '').replace(/\r/g, '').split(/\n\s*\n/)
      .filter(function (p) { return !/^\s*※/.test(p); }).join(' ')
      .replace(/\*\*\[(클릭|넘김|임의)\]\*\*|\[(클릭|넘김|임의)\]/g, '')
      .replace(/\*\*/g, '').replace(/→\s*전환\s*:/g, '').replace(/\s+/g, '').length;
  }
  function estOf(s, k) {
    var kd = kind(s);
    if (kd === 'apx' || kd === 'apxdiv') return 0;
    if (s.classList.contains('bl-sl--div') || s.classList.contains('bl-sl--chapter')) return 5;
    var n = spokenLen(noteOf(k));
    return n ? Math.max(20, Math.ceil(n / 300 * 60 / 5) * 5) : 20;
  }
  function retime() {
    var c = 0;
    slides.forEach(function (s, k) { ALLOT[k] = estOf(s, k); c += ALLOT[k]; CUM[k] = c; });
  }
  applyEdits();

  // ── 메모 ──────────────────────────────────────────────────────────────
  // 지금 장의 발표자 노트를 지면 아래에 띄운다. 대본 창은 팝업이라 막히는 환경이
  // 있다 — 메모는 같은 창 안이라 언제나 열린다.
  var notesEl = null;
  function notesOn() { return !!(notesEl && !notesEl.hidden); }
  function toggleNotes() {
    if (!notesEl) {
      notesEl = mk('aside'); notesEl.id = 'bl-notes';
      notesEl.setAttribute('aria-live', 'polite'); notesEl.hidden = true;
      B.appendChild(notesEl);
    }
    notesEl.hidden = !notesEl.hidden;
    paintNotes(); paintToggles();
  }
  function paintNotes() {
    if (!notesOn()) return;
    notesEl.textContent = '';
    notesEl.appendChild(mk('b', null, '메모 · ' + (pgOf(slides[i]) || '표지')));
    var box = mk('div', 'bl-md');
    box.innerHTML = md(noteOf(i) || '(노트 없음)', stepAt[i]);
    notesEl.appendChild(box);
  }

  // ── 도움말 ────────────────────────────────────────────────────────────
  var helpEl = null;
  function helpOn() { return !!(helpEl && !helpEl.hidden); }
  function toggleHelp() {
    if (!helpEl) {
      helpEl = mk('div'); helpEl.id = 'bl-help';
      helpEl.setAttribute('role', 'dialog'); helpEl.setAttribute('aria-label', '단축키');
      var dl = mk('dl');
      helpRows().forEach(function (k) { dl.appendChild(mk('dt', null, k[0])); dl.appendChild(mk('dd', null, k[1])); });
      dl.appendChild(mk('p', 'bl-help-note', '파워포인트 슬라이드 쇼 단축키와 같다 · 덱의 #bl-keys 로 바꿀 수 있다'));
      helpEl.appendChild(dl);
      helpEl.hidden = true;
      helpEl.addEventListener('click', function () { helpEl.hidden = true; });
      B.appendChild(helpEl);
    }
    helpEl.hidden = !helpEl.hidden;
  }

  // ── 대본 창 ───────────────────────────────────────────────────────────
  var P = { win: null, panel: null, t0: 0, tick: 0, editing: false, editKey: null, resetArm: 0 };
  function presenterOpen() { return !!((P.win && !P.win.closed) || (P.panel && !P.panel.hidden)); }
  function timerReset() { P.t0 = Date.now(); presenterTick(); }
  function startTick() {
    if (P.tick) return;
    P.tick = setInterval(function () {
      if (!presenterOpen()) { clearInterval(P.tick); P.tick = 0; return; }
      presenterTick();
    }, 1000);
  }
  // 대본 창은 덱 CSS 가 없는 창이다. 덱의 토큰 값을 읽어 그 창의 :root 에 옮긴다 —
  // 색을 이 파일에 따로 적지 않는다.
  var PTOK = ['--br-dark', '--br-cover', '--br-on-dark', '--br-on-dark-2', '--br-on-dark-3', '--br-dark-line',
              '--br-amber', '--br-accent-on-dark', '--br-ok-on-dark', '--br-alert-on-dark', '--br-mark', '--br-card'];
  function tokenRoot() {
    var cs = getComputedStyle(R);
    return ':root{' + PTOK.map(function (t) { return t + ':' + (cs.getPropertyValue(t).trim() || 'initial'); }).join(';') + '}';
  }
  function fontFaces() {
    var out = [];
    Array.prototype.forEach.call(D.styleSheets, function (sh) {
      var rules;
      try { rules = sh.cssRules; } catch (e) { return; }   // 연결형 파일 덱은 읽기가 막힌다 — 시스템 글꼴로
      Array.prototype.forEach.call(rules || [], function (r) { if (r.type === 5) out.push(r.cssText); });
    });
    return out.join('\n');
  }
  var PCSS = [
    '.bl-p{box-sizing:border-box;min-height:100%;display:flex;flex-direction:column;gap:12px;padding:18px 20px 14px;',
    'background:var(--br-dark);color:var(--br-on-dark);font:400 16px/1.65 Pretendard,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;word-break:keep-all}',
    '.bl-p *{box-sizing:border-box}',
    '.bl-p button{font:700 12px/1.2 inherit;font-family:inherit;padding:6px 10px;border-radius:6px;border:1px solid var(--br-dark-line);',
    'background:transparent;color:var(--br-on-dark-2);cursor:pointer}',
    '.bl-p button:hover{color:var(--br-on-dark);border-color:var(--br-on-dark-3)}',
    '.bl-p .top{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center}',
    '.bl-p .n{font:700 22px/1 "IBM Plex Mono",ui-monospace,monospace;color:var(--br-amber)}',
    '.bl-p .t{font:800 17px/1.35 inherit;font-family:inherit}',
    '.bl-p .tm{display:grid;justify-items:end;gap:2px;padding:6px 10px;text-align:right}',
    '.bl-p .tm b{font:700 28px/1 "IBM Plex Mono",ui-monospace,monospace;color:var(--br-on-dark)}',
    '.bl-p .tm small{font:600 11px/1.2 inherit;font-family:inherit;color:var(--br-on-dark-3)}',
    '.bl-p .tm em{font:700 11px/1.2 inherit;font-family:inherit;font-style:normal}',
    '.bl-p .tm.late b,.bl-p .tm.late em{color:var(--br-alert-on-dark)}',
    '.bl-p .tm.early b,.bl-p .tm.early em{color:var(--br-ok-on-dark)}',
    '.bl-p .st{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--br-dark-line);',
    'font:600 13px/1.2 inherit;font-family:inherit;color:var(--br-on-dark-2)}',
    '.bl-p .st .ed{padding:2px 7px;border-radius:4px;background:var(--br-amber);color:var(--br-cover);font-weight:800}',
    '.bl-p .st button{margin-left:auto}',
    '.bl-p .bd{flex:1;min-height:120px;overflow:auto;padding-right:6px}',
    '.bl-md p{margin:0 0 .75em}.bl-md strong{color:var(--br-amber);font-weight:800}',
    '.bl-md .k{display:inline-block;margin:0 .2em;padding:.05em .45em;border-radius:4px;border:1px solid var(--br-dark-line);',
    'font-size:.82em;font-weight:800;color:var(--br-on-dark-3);vertical-align:.08em}',
    '.bl-md .k.done{color:var(--br-on-dark-3);text-decoration:line-through;opacity:.7}',
    '.bl-md .k.now{background:var(--br-amber);border-color:var(--br-amber);color:var(--br-cover)}',
    '.bl-md .k.x{border-style:dashed}',
    '.bl-md .tr{margin:.4em 0 .8em;padding:.5em .7em;border-left:3px solid var(--br-accent-on-dark);',
    'background:color-mix(in srgb,var(--br-accent-on-dark) 12%,transparent)}',
    '.bl-md .memo{margin:.4em 0 .8em;padding:.45em .7em;border-radius:6px;font-size:.9em;color:var(--br-on-dark-3);',
    'background:color-mix(in srgb,var(--br-on-dark) 6%,transparent)}',
    '.bl-p .nx{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:baseline;padding-top:8px;',
    'border-top:1px solid var(--br-dark-line);font:600 13px/1.35 inherit;font-family:inherit;color:var(--br-on-dark-2)}',
    '.bl-p .nx b{color:var(--br-on-dark-3);letter-spacing:.08em}',
    '.bl-p .ft{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font:500 11px/1.4 inherit;font-family:inherit;color:var(--br-on-dark-3)}',
    '.bl-p .ft .acts{margin-left:auto;display:flex;flex-wrap:wrap;gap:6px}',
    '.bl-p textarea{width:100%;min-height:260px;flex:1;resize:vertical;padding:12px;border-radius:6px;border:1px solid var(--br-dark-line);',
    'background:var(--br-cover);color:var(--br-on-dark);font:400 15px/1.6 inherit;font-family:inherit;outline:none}',
    '.bl-p .edc{font:600 12px/1.3 inherit;font-family:inherit;color:var(--br-on-dark-3)}',
    '.bl-p .row{display:flex;flex-wrap:wrap;gap:6px}',
    '.bl-p .row button.go{background:var(--br-amber);border-color:var(--br-amber);color:var(--br-cover)}'
  ].join('');

  function presenterRoot() {
    if (P.win && !P.win.closed) return P.win.document.getElementById('root');
    if (P.panel && !P.panel.hidden) return P.panel.querySelector('.bl-p');
    return null;
  }
  function mainCss() {
    if (D.getElementById('bl-p-css')) return;
    var st = D.createElement('style'); st.id = 'bl-p-css'; st.textContent = PCSS;
    D.head.appendChild(st);
  }
  function openPresenter() {
    if (P.win && !P.win.closed) { P.win.close(); P.win = null; emit('deck:presenter', { open: false }); paintToggles(); return; }
    if (P.panel && !P.panel.hidden) { closePanel(); return; }
    var w = null;
    try { w = W.open('', 'bl-presenter', 'width=760,height=920'); } catch (e) { w = null; }
    if (w && w.document) {
      P.win = w;
      var d = w.document;
      d.open();
      d.write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>대본 — ' + esc(deckTitle) + '</title><' +
              'style>html,body{margin:0;height:100%}' + tokenRoot() + fontFaces() + PCSS + '</' + 'style></head><body>' +
              '<div class="bl-p" id="root"></div></body></html>');
      d.close();
      d.addEventListener('keydown', popupKey);
      d.addEventListener('click', presenterClick);
      w.addEventListener('beforeunload', function () { P.win = null; emit('deck:presenter', { open: false }); paintToggles(); });
    } else {
      openPanel();
      toast('대본 창 팝업 차단 — 같은 창 오른쪽에 표시 · 팝업을 허용하면 별도 창');
    }
    if (!P.t0) timerReset();
    startTick();
    presenterPaint(true);
    paintToggles();
    emit('deck:presenter', { open: true });
  }
  function openPanel() {
    mainCss();
    if (!P.panel) {
      P.panel = mk('aside'); P.panel.id = 'bl-scr'; P.panel.setAttribute('aria-label', '대본');
      P.panel.appendChild(mk('div', 'bl-p'));
      P.panel.addEventListener('click', presenterClick);
      P.panel.addEventListener('keydown', fieldKey);
      B.appendChild(P.panel);
    }
    P.panel.hidden = false;
    R.classList.add('bl-scr');
    realign();
  }
  function closePanel() {
    if (P.editing) editSave(true);
    if (P.panel) P.panel.hidden = true;
    R.classList.remove('bl-scr');
    realign();
    paintToggles();
    emit('deck:presenter', { open: false });
  }
  function presenterTick() {
    var root = presenterRoot();
    if (!root) return;
    var tm = root.querySelector('.tm');
    if (!tm) return;
    var el = (Date.now() - P.t0) / 1000;
    var start = (CUM[i] || 0) - (ALLOT[i] || 0), end = CUM[i] || 0;
    var late = el > end + 45, early = el < start - 45;
    tm.className = 'tm' + (late ? ' late' : early ? ' early' : '');
    tm.querySelector('b').textContent = mmss(el);
    var diff = el - end;
    tm.querySelector('em').textContent = late ? '+' + mmss(diff) + ' 늦음' : early ? '-' + mmss(start - el) + ' 이름' : '예정 범위';
  }
  function presenterPaint(full) {
    var root = presenterRoot();
    if (!root) return;
    var s = slides[i], k = keyOf(s), lv = levels(s).length;
    if (P.editing && P.editKey !== k) editSave(true);
    var d = root.ownerDocument;
    function el(tag, cls, text) { var e = d.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
    root.textContent = '';
    var top = el('div', 'top');
    top.appendChild(el('span', 'n', (pgOf(s) || '표지').split(' / ')[0]));
    top.appendChild(el('span', 't', titleOf(s)));
    var tm = el('button', 'tm'); tm.type = 'button'; tm.setAttribute('data-a', 'timer'); tm.title = '누르면 0:00 부터';
    tm.appendChild(el('b', null, '0:00'));
    tm.appendChild(el('small', null, '배정 ' + mmss(ALLOT[i]) + ' · 누적 ' + mmss(CUM[i])));
    tm.appendChild(el('em'));
    top.appendChild(tm);
    root.appendChild(top);

    var st = el('div', 'st');
    st.appendChild(el('span', null, lv ? '단계 ' + stepAt[i] + ' / ' + lv : '단계 없음'));
    if (Object.prototype.hasOwnProperty.call(EDIT, k)) st.appendChild(el('span', 'ed', '수정됨'));
    if (!P.editing) { var eb = el('button', null, '편집'); eb.type = 'button'; eb.setAttribute('data-a', 'edit'); st.appendChild(eb); }
    root.appendChild(st);

    var bd = el('div', 'bd');
    if (P.editing) {
      var ta = el('textarea'); ta.id = 'bl-edta'; ta.value = noteOf(i);
      var cnt = el('div', 'edc');
      var upd = function () { cnt.textContent = spokenLen(ta.value) + '자 · 약 ' + mmss(Math.max(20, Math.ceil(spokenLen(ta.value) / 300 * 60 / 5) * 5)); };
      ta.addEventListener('input', upd); ta.addEventListener('keydown', fieldKey); upd();
      var row = el('div', 'row');
      [['save', '저장 (Ctrl+Enter)', 'go'], ['orig', '이 장 원본'], ['cancel', '취소 (Esc)']].forEach(function (b) {
        var x = el('button', b[2] || null, b[1]); x.type = 'button'; x.setAttribute('data-a', b[0]); row.appendChild(x);
      });
      bd.appendChild(ta); bd.appendChild(cnt); bd.appendChild(row);
    } else {
      var box = el('div', 'bl-md');
      box.innerHTML = md(noteOf(i) || '(노트 없음)', stepAt[i]);
      bd.appendChild(box);
    }
    root.appendChild(bd);

    var nx = el('div', 'nx');
    nx.appendChild(el('b', null, '다음'));
    nx.appendChild(el('span', null, i < slides.length - 1 ? labelOf(slides[i + 1]) : '마지막 장'));
    nx.appendChild(el('small', null, i < slides.length - 1 ? '배정 ' + mmss(ALLOT[i + 1]) : ''));
    root.appendChild(nx);

    var ft = el('div', 'ft');
    ft.appendChild(el('span', null, '→ Space 다음 · ← 이전 (단계 포함) · 타이머를 누르면 0:00'));
    var acts = el('span', 'acts');
    [['export', '수정분 내보내기'], ['copy', '수정분 복사'], ['all', '전체 대본'], ['reset', '전부 원복']].forEach(function (b) {
      var x = el('button', null, b[1]); x.type = 'button'; x.setAttribute('data-a', b[0]); acts.appendChild(x);
    });
    ft.appendChild(acts);
    root.appendChild(ft);
    presenterTick();
    if (P.editing) { var t = root.querySelector('textarea'); if (t) { t.focus(); } }
    else {
      var now = root.querySelector('.k.now');
      if (now && now.scrollIntoView) now.scrollIntoView({ block: 'center' });
    }
  }
  function presenterClick(e) {
    var b = e.target.closest && e.target.closest('[data-a]');
    if (!b) return;
    var a = b.getAttribute('data-a');
    if (a === 'timer') timerReset();
    else if (a === 'edit') { P.editing = true; P.editKey = keyOf(slides[i]); presenterPaint(true); }
    else if (a === 'save') editSave(false);
    else if (a === 'cancel') { P.editing = false; presenterPaint(true); }
    else if (a === 'orig') { var t = presenterRoot().querySelector('textarea'); if (t) { t.value = ORIG[keyOf(slides[i])]; t.dispatchEvent(new Event('input')); } }
    else if (a === 'export') exportEdits();
    else if (a === 'copy') copyEdits();
    else if (a === 'all') exportAll();
    else if (a === 'reset') resetAll();
  }
  function editSave(silent) {
    var root = presenterRoot(), t = root && root.querySelector('textarea');
    var k = P.editKey;
    P.editing = false;
    if (t && k != null) {
      if (t.value === ORIG[k]) delete EDIT[k]; else EDIT[k] = t.value;
      persist(); applyEdits();
      if (!silent) toast('대본 저장 — 이 브라우저에 보관');
    }
    if (!silent) presenterPaint(true);
  }
  function fieldKey(e) {
    if (!e.target || e.target.tagName !== 'TEXTAREA') return;
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); editSave(false); }
    else if (e.key === 'Escape') { e.preventDefault(); P.editing = false; presenterPaint(true); }
    e.stopPropagation();
  }
  function popupKey(e) {
    if (e.target && /^(TEXTAREA|INPUT)$/.test(e.target.tagName)) { fieldKey(e); return; }
    var k = e.key;
    var act = KEYIDX[comboOf(e)];
    if (act === 'next') { e.preventDefault(); next(); }
    else if (act === 'prev') { e.preventDefault(); prev(); }
    else if (k === 'Home') { e.preventDefault(); goTo(0); }
    else if (k === 'End') { e.preventDefault(); goTo(slides.length - 1); }
  }

  // 내보내기 — 저장 기능이 있는 호스트(Claude 아티팩트)면 그 길로, 아니면 파일 내려받기.
  // 둘 다 막히면 복사 창을 띄운다. 어느 길로도 내용은 이 창 밖으로 나가지 않는다.
  var DLCAP;
  function dlcap() {
    if (DLCAP !== undefined) return Promise.resolve(DLCAP);
    try {
      if (W.claude && typeof W.claude.use === 'function') {
        return W.claude.use('downloads').then(function (x) { DLCAP = x || null; return DLCAP; },
                                               function () { DLCAP = null; return null; });
      }
    } catch (e) { /* 무시 */ }
    DLCAP = null;
    return Promise.resolve(null);
  }
  function saveFile(name, text, mime) {
    dlcap().then(function (cap) {
      if (cap && cap.save) {
        cap.save({ filename: name, data: text }).then(function () { toast('내려받기 완료 · ' + name); }, function (err) {
          if (err && err.code === 'declined') return;
          copyOut(name, text);
        });
        return;
      }
      try {
        var u = URL.createObjectURL(new Blob(['﻿' + text], { type: (mime || 'text/plain') + ';charset=utf-8' }));
        var a = mk('a'); a.href = u; a.download = name; B.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(u); a.remove(); }, 800);
        toast('내려받기 · ' + name + ' — 막히면 「복사」 사용');
      } catch (e) { copyOut(name, text); }
    });
  }
  function copyOut(name, text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { toast('클립보드 복사 완료 · ' + name); },
                                                  function () { showRaw(name, text); });
        return;
      }
    } catch (e) { /* 무시 */ }
    showRaw(name, text);
  }
  var rawModal = null;
  function showRaw(name, text) {
    var ov = D.getElementById('bl-rawdl');
    if (ov) ov.remove();
    ov = mk('div'); ov.id = 'bl-rawdl'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true');
    var h = mk('div', 'bl-rawdl-h');
    h.appendChild(mk('b', null, name));
    var bc = mk('button', null, '전체 선택'); bc.type = 'button';
    var bx = mk('button', null, '닫기'); bx.type = 'button';
    h.appendChild(bc); h.appendChild(bx);
    var ta = mk('textarea'); ta.readOnly = true; ta.value = text;
    ov.appendChild(h); ov.appendChild(ta); B.appendChild(ov);
    function close() { ov.remove(); popModal(rawModal); }
    rawModal = { el: ov, key: function (e) { if (e.key === 'Escape') close(); else return false; }, close: close };
    pushModal(rawModal);
    bc.onclick = function () { ta.focus(); ta.select(); };
    bx.onclick = close;
    ta.focus(); ta.select();
  }
  function exportEdits() {
    var n = Object.keys(EDIT).length;
    if (!n) { toast('수정한 장 없음'); return; }
    saveFile(fileBase() + '_대본수정_' + stamp() + '.json', JSON.stringify(EDIT, null, 2), 'application/json');
  }
  function copyEdits() {
    if (!Object.keys(EDIT).length) { toast('수정한 장 없음'); return; }
    copyOut(fileBase() + '_대본수정.json', JSON.stringify(EDIT, null, 2));
  }
  function exportAll() {
    var total = slides.reduce(function (a, s, k) { return a + (ALLOT[k] || 0); }, 0);
    var out = ['# ' + (deckTitle || '대본'), '', '총 ' + mmss(total) + ' · ' + new Date().toLocaleString('ko-KR'), ''];
    slides.forEach(function (s, k) {
      var key = keyOf(s);
      out.push('## ' + labelOf(s) + '  [' + mmss(ALLOT[k]) + ' · 누적 ' + mmss(CUM[k]) + ']' +
               (Object.prototype.hasOwnProperty.call(EDIT, key) ? ' (수정됨)' : ''));
      out.push('', noteOf(k) || '(노트 없음)', '');
    });
    saveFile(fileBase() + '_대본_' + stamp() + '.md', out.join('\n'), 'text/markdown');
  }
  function resetAll() {
    if (!Object.keys(EDIT).length) { toast('수정한 장 없음'); return; }
    if (!P.resetArm || Date.now() - P.resetArm > 4000) { P.resetArm = Date.now(); toast('한 번 더 누르면 전부 원복'); return; }
    P.resetArm = 0; EDIT = {}; persist(); applyEdits(); presenterPaint(true); toast('대본 원복 완료');
  }
  W.addEventListener('beforeunload', function () { if (P.win && !P.win.closed) P.win.close(); });

  // ── 출처 칩 · 근거 패널 ───────────────────────────────────────────────
  // 근거는 덱 안의 JSON 한 벌에 모은다. 칩은 키만 들고 있다 — 같은 근거를 여러
  // 장에서 가리켜도 내용은 한 곳에서 고친다.
  //   {"ev":  {"E1": {title, grade, facts, src, date, url, note, key, gnote, use, doc,
  //                    imgs: [["캡처id", "설명"]], hl: ["facts 에서 칠할 문구"]}},
  //    "img": {"캡처id": "data:image/…"},        캡처 원본
  //    "hl":  {"캡처id": [[x, y, w, h]]},         캡처 위 하이라이트 상자 — 0~1 비율
  //    "grades": {"A": "…"}}                      등급 설명을 바꾸거나 늘릴 때
  // facts 는 줄 배열이 기본이다. 한 문자열로 주면 ' / ' 로 큰 단위, 긴 줄은 ' · ' 로 나눈다.
  var GRADES = { A: '1차 공식 자료', B: '학술·전문기관', C: '언론·2차 자료', R: '직접 조회·집계' };
  var EV = {}, EVIMG = {}, EVHL = {};
  (function () {
    var el = D.getElementById('bl-evidence');
    if (!el) return;
    try {
      var d = JSON.parse(el.textContent);
      EV = d.ev || {}; EVIMG = d.img || {}; EVHL = d.hl || {};
      var g = d.grades || d.gr;
      if (g) Object.keys(g).forEach(function (k) { GRADES[k] = g[k]; });
    } catch (err) { if (W.console) console.warn('bl-evidence JSON 을 읽지 못함', err); }
  })();
  function splitTop(s, sep) {
    var out = [], depth = 0, cur = '', open = '(「[『【〈《', close = ')」]』】〉》';
    for (var k = 0; k < s.length; k++) {
      var ch = s.charAt(k);
      if (open.indexOf(ch) >= 0) depth++;
      else if (close.indexOf(ch) >= 0) depth = Math.max(0, depth - 1);
      if (!depth && s.substr(k, sep.length) === sep) { out.push(cur); cur = ''; k += sep.length - 1; continue; }
      cur += ch;
    }
    out.push(cur);
    return out.map(function (x) { return x.trim(); }).filter(Boolean);
  }
  function factsOf(e) {
    if (!e || !e.facts) return [];
    if (Array.isArray(e.facts)) return e.facts.slice();
    var out = [];
    splitTop(String(e.facts), ' / ').forEach(function (chunk) {
      if (chunk.length <= 95) { out.push(chunk); return; }
      var acc = '';
      splitTop(chunk, ' · ').forEach(function (p) {
        if (!acc) { acc = p; return; }
        if (acc.length < 28 || p.length < 22) acc += ' · ' + p; else { out.push(acc); acc = p; }
      });
      if (acc) out.push(acc);
    });
    return out;
  }
  function markHl(text, hl) {
    var h = esc(text), hit = false;
    (hl || []).forEach(function (p) {
      if (!p) return;
      var q = esc(p);
      if (h.indexOf(q) >= 0) { hit = true; h = h.split(q).join('<mark>' + q + '</mark>'); }
    });
    return { html: h, hit: hit };
  }

  var EVP = { el: null, keys: [], cur: 0, chip: null, kbd: false, view: null, wide: false, modal: null };
  function openEvidence(chip, kbd) {
    var keys = (chip.getAttribute('data-ev') || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean);
    if (!keys.length) return;
    EVP.keys = keys; EVP.cur = 0; EVP.chip = chip; EVP.kbd = kbd;
    if (!EVP.el) {
      EVP.el = mk('div'); EVP.el.id = 'bl-ev-panel';
      EVP.el.setAttribute('role', 'dialog'); EVP.el.setAttribute('aria-modal', 'true');
      EVP.el.setAttribute('aria-labelledby', 'bl-ev-title');
      EVP.el.hidden = true;
      EVP.el.addEventListener('click', function (ev) { if (ev.target === EVP.el) closeEvidence(); });
      EVP.el.addEventListener('wheel', function (ev) {
        if (!ev.target.closest('.bl-ev-text, .bl-ev-box:not(.has-view)') && !ev.target.closest('.bl-ev-stagebox')) ev.preventDefault();
      }, { passive: false });
      B.appendChild(EVP.el);
      EVP.modal = { el: EVP.el, key: evKey, close: closeEvidence };
    }
    EVP.el.hidden = false;
    R.classList.add('bl-evidence-open');
    pushModal(EVP.modal);
    renderEvidence();
  }
  function renderEvidence() {
    var key = EVP.keys[EVP.cur], e = EV[key];
    var anyImg = EVP.keys.some(function (k) { return EV[k] && EV[k].imgs && EV[k].imgs.length; });
    var el = EVP.el;
    el.textContent = '';
    el.classList.toggle('has-img', anyImg);
    var box = mk('div', 'bl-ev-box' + (anyImg ? ' has-view' : ''));
    var head = mk('div', 'bl-ev-head');
    if (EVP.keys.length > 1) {
      var tabs = mk('div', 'bl-ev-tabs'); tabs.setAttribute('role', 'tablist');
      EVP.keys.forEach(function (k, n) {
        var b = mk('button', null, k); b.type = 'button'; b.setAttribute('role', 'tab');
        b.setAttribute('aria-selected', String(n === EVP.cur));
        b.title = (EV[k] && EV[k].title) || k;
        b.onclick = function () { EVP.cur = n; renderEvidence(); };
        tabs.appendChild(b);
      });
      head.appendChild(tabs);
    } else {
      head.appendChild(mk('span', 'bl-ev-id', key));
    }
    if (e && e.grade) {
      var g = mk('span', 'bl-ev-grade'); g.setAttribute('data-g', e.grade);
      g.appendChild(mk('b', null, e.grade));
      g.appendChild(D.createTextNode(GRADES[e.grade] || ''));
      head.appendChild(g);
    }
    if (e && e.key) head.appendChild(mk('span', 'bl-ev-id', e.key));
    if (anyImg) {
      var wb = mk('button', 'bl-ev-wide', '넓게 보기'); wb.type = 'button';
      wb.setAttribute('aria-pressed', String(EVP.wide));
      wb.onclick = function () { EVP.wide = !EVP.wide; wb.setAttribute('aria-pressed', String(EVP.wide));
        var bd = el.querySelector('.bl-ev-body'); if (bd) bd.classList.toggle('is-wide', EVP.wide);
        setTimeout(function () { if (EVP.view) EVP.view.resize(true); }, 30); };
      head.appendChild(wb);
    }
    var x = mk('button', 'bl-ev-x', '×'); x.type = 'button'; x.setAttribute('aria-label', '근거 닫기');
    x.onclick = closeEvidence;
    head.appendChild(x);
    box.appendChild(head);

    var text = mk('div', anyImg ? 'bl-ev-text' : null);
    var t = mk('h3', 'bl-ev-title', e ? e.title : '근거 없음 — ' + key); t.id = 'bl-ev-title';
    var claim = EVP.chip && EVP.chip.getAttribute('data-claim');
    if (claim) text.appendChild(mk('p', 'bl-ev-claim', claim));
    text.appendChild(t);
    var facts = factsOf(e);
    if (facts.length) {
      var ul = mk('ul', 'bl-ev-facts');
      facts.forEach(function (f) {
        var li = mk('li'), r = markHl(f, e && e.hl);
        li.innerHTML = r.html;
        if (r.hit) li.className = 'is-hl';
        ul.appendChild(li);
      });
      text.appendChild(ul);
    }
    if (e && e.doc) {
      var db = mk('button', 'bl-pgref', '원문 보기'); db.type = 'button';
      db.setAttribute('data-doc', e.doc);
      if (e.dochl != null) db.setAttribute('data-hl', e.dochl);
      text.appendChild(db);
    }
    if (e && (e.src || e.date)) {
      var src = mk('p', 'bl-ev-src', [e.src, e.date].filter(Boolean).join(' · '));
      if (e.url && /^https?:\/\//.test(e.url)) {
        src.appendChild(D.createTextNode(' · '));
        var a = mk('a', null, '원문 링크'); a.href = e.url; a.target = '_blank'; a.rel = 'noopener noreferrer';
        src.appendChild(a);
      }
      text.appendChild(src);
    }
    if (e && e.note) text.appendChild(mk('p', 'bl-ev-note', e.note));
    [['gnote', '등급 근거'], ['use', '이 근거를 쓴 곳']].forEach(function (p) {
      if (!e || !e[p[0]]) return;
      var dt = mk('details', 'bl-ev-more'); dt.appendChild(mk('summary', null, p[1]));
      dt.appendChild(mk('p', null, e[p[0]])); text.appendChild(dt);
    });

    if (!anyImg) {
      box.appendChild(text);
      el.appendChild(box);
      EVP.view = null;
    } else {
      var body = mk('div', 'bl-ev-body' + (EVP.wide ? ' is-wide' : ''));
      body.appendChild(text);
      var vw = mk('div', 'bl-ev-view');
      body.appendChild(vw);
      box.appendChild(body);
      el.appendChild(box);
      var imgs = (e && e.imgs) || [];
      EVP.view = imgs.length ? viewer(vw, imgs, EVP.cur === 0 && EVP.chip ? EVP.chip.getAttribute('data-img') : null) : null;
      if (!imgs.length) vw.appendChild(mk('p', 'bl-ev-note', '이 근거에는 캡처 없음'));
    }
    x.focus();
  }
  function closeEvidence() {
    if (!EVP.el) return;
    EVP.el.hidden = true;
    R.classList.remove('bl-evidence-open');
    popModal(EVP.modal);
    EVP.view = null;
    if (EVP.chip) { if (EVP.kbd) EVP.chip.focus(); else if (EVP.chip.blur) EVP.chip.blur(); }
    EVP.chip = null;
  }
  function evKey(e) {
    var k = e.key;
    if (k === 'Escape') { closeEvidence(); return; }
    if (k === 'Tab') { trapTab(e, EVP.el); return false; }
    if ((k === 'ArrowLeft' || k === 'ArrowRight') && EVP.keys.length > 1) {
      EVP.cur = (EVP.cur + (k === 'ArrowRight' ? 1 : EVP.keys.length - 1)) % EVP.keys.length;
      renderEvidence(); return;
    }
    if (EVP.view) EVP.view.key(e);
  }

  // 캡처 뷰어 — 휠 확대(커서 기준) · 끌기 · 두 번 눌러 2배 · 폭 맞춤 · 전체 보기 ·
  // 하이라이트 상자로 이동(h). 처음에는 첫 하이라이트로, 없으면 폭 맞춤으로 연다.
  function viewer(host, imgs, startId) {
    var st = { idx: 0, s: 1, x: 0, y: 0, iw: 0, ih: 0, hl: -1 };
    var thumbs = mk('div', 'bl-ev-thumbs');
    var tool = mk('div', 'bl-ev-tool');
    var cap = mk('span', 'bl-ev-cap');
    var hp = mk('button', null, '‹'), hn = mk('span'), hx = mk('button', null, '›');
    var zo = mk('button', null, '−'), zv = mk('span'), zi = mk('button', null, '+');
    var fw = mk('button', null, '폭 맞춤'), fa = mk('button', null, '전체 보기');
    [hp, hx, zo, zi, fw, fa].forEach(function (b) { b.type = 'button'; });
    hp.setAttribute('aria-label', '이전 하이라이트'); hx.setAttribute('aria-label', '다음 하이라이트');
    zo.setAttribute('aria-label', '축소'); zi.setAttribute('aria-label', '확대');
    [cap, hp, hn, hx, zo, zv, zi, fw, fa].forEach(function (n) { tool.appendChild(n); });
    var sbox = mk('div', 'bl-ev-stagebox'), stage = mk('div', 'bl-ev-stage'), img = mk('img');
    img.alt = ''; img.draggable = false;
    stage.appendChild(img); sbox.appendChild(stage);
    host.appendChild(thumbs); host.appendChild(tool); host.appendChild(sbox);
    imgs.forEach(function (it, n) {
      var b = mk('button'); b.type = 'button';
      b.setAttribute('aria-label', it[1] || it[0]);
      if (EVIMG[it[0]]) b.style.backgroundImage = 'url("' + EVIMG[it[0]] + '")';
      b.onclick = function () { load(n); };
      thumbs.appendChild(b);
    });
    if (imgs.length < 2) thumbs.hidden = true;
    function rects() { return EVHL[imgs[st.idx][0]] || []; }
    function minS() { return fitAllS() * .9; }
    function maxS() { return Math.max(fitWS() * 5, 3); }
    function fitWS() { return st.iw ? Math.max(.01, (sbox.clientWidth - 80) / st.iw) : 1; }
    function fitAllS() { return st.iw ? Math.max(.01, Math.min((sbox.clientWidth - 80) / st.iw, (sbox.clientHeight - 80) / st.ih)) : 1; }
    function apply(anim) {
      stage.classList.toggle('is-anim', !!anim);
      stage.style.transform = 'translate(' + st.x + 'px,' + st.y + 'px) scale(' + st.s + ')';
      zv.textContent = Math.round(st.s * 100) + '%';
    }
    function fitW(anim) { st.s = fitWS(); st.x = (sbox.clientWidth - st.iw * st.s) / 2; st.y = 16; apply(anim); }
    function fitAll(anim) {
      st.s = fitAllS();
      st.x = (sbox.clientWidth - st.iw * st.s) / 2; st.y = (sbox.clientHeight - st.ih * st.s) / 2; apply(anim);
    }
    function zoomAt(f, cx, cy, anim) {
      var s2 = clamp(st.s * f, minS(), maxS()), k = s2 / st.s;
      if (cx == null) { cx = sbox.clientWidth / 2; cy = sbox.clientHeight / 2; }
      st.x = cx - (cx - st.x) * k; st.y = cy - (cy - st.y) * k; st.s = s2; apply(anim);
    }
    function goRect(n) {
      var rs = rects();
      if (!rs.length) return;
      st.hl = (n + rs.length) % rs.length;
      var r = rs[st.hl], bw = sbox.clientWidth, bh = sbox.clientHeight;
      var aw = Math.max(r[2] * 3, .55) * st.iw, ah = Math.max(r[3] * 6, .28) * st.ih;
      var s = clamp(Math.min(bw / aw, bh / ah), fitAllS(), fitWS() * 4);
      var cx = (r[0] + r[2] / 2) * st.iw, cy = (r[1] + r[3] / 2) * st.ih;
      st.s = s; st.x = bw / 2 - cx * s; st.y = bh / 2 - cy * s; apply(true);
      $$('.bl-ev-hb', stage).forEach(function (h, k) {
        h.classList.remove('is-cur');
        if (k === st.hl) { void h.offsetWidth; h.classList.add('is-cur'); }
      });
      hn.textContent = (st.hl + 1) + ' / ' + rs.length;
    }
    function load(n) {
      st.idx = n; st.hl = -1;
      $$('button', thumbs).forEach(function (b, k) { b.setAttribute('aria-pressed', String(k === n)); });
      cap.textContent = imgs[n][1] || imgs[n][0];
      $$('.bl-ev-hb', stage).forEach(function (h) { h.remove(); });
      var src = EVIMG[imgs[n][0]];
      if (!src) { cap.textContent = '캡처 없음 — ' + imgs[n][0]; img.removeAttribute('src'); return; }
      img.onload = function () {
        st.iw = img.naturalWidth || 1000; st.ih = img.naturalHeight || 700;
        img.style.width = st.iw + 'px'; img.style.height = st.ih + 'px';
        rects().forEach(function (r) {
          var h = mk('i', 'bl-ev-hb');
          h.style.left = r[0] * st.iw + 'px'; h.style.top = r[1] * st.ih + 'px';
          h.style.width = r[2] * st.iw + 'px'; h.style.height = r[3] * st.ih + 'px';
          stage.appendChild(h);
        });
        var rs = rects();
        hp.hidden = hx.hidden = hn.hidden = !rs.length;
        hn.textContent = rs.length ? '0 / ' + rs.length : '';
        if (rs.length) goRect(0); else fitW(false);
      };
      img.src = src;
    }
    hp.onclick = function () { goRect(st.hl - 1); };
    hx.onclick = function () { goRect(st.hl + 1); };
    zo.onclick = function () { zoomAt(1 / 1.3, null, null, true); };
    zi.onclick = function () { zoomAt(1.3, null, null, true); };
    fw.onclick = function () { fitW(true); };
    fa.onclick = function () { fitAll(true); };
    sbox.addEventListener('wheel', function (e) {
      e.preventDefault();
      var dy = e.deltaMode === 1 ? e.deltaY * 30 : e.deltaY, rc = sbox.getBoundingClientRect();
      zoomAt(Math.exp(-dy * .0018), e.clientX - rc.left, e.clientY - rc.top, false);
    }, { passive: false });
    var drag = null;
    sbox.addEventListener('pointerdown', function (e) {
      drag = { x: e.clientX, y: e.clientY, sx: st.x, sy: st.y };
      try { sbox.setPointerCapture(e.pointerId); } catch (er) { /* 무시 */ }
      sbox.classList.add('is-drag');
    });
    sbox.addEventListener('pointermove', function (e) {
      if (!drag) return;
      st.x = drag.sx + e.clientX - drag.x; st.y = drag.sy + e.clientY - drag.y; apply(false);
    });
    function endDrag() { drag = null; sbox.classList.remove('is-drag'); }
    sbox.addEventListener('pointerup', endDrag); sbox.addEventListener('pointercancel', endDrag);
    sbox.addEventListener('dblclick', function (e) {
      var rc = sbox.getBoundingClientRect(); zoomAt(2, e.clientX - rc.left, e.clientY - rc.top, true);
    });
    var start = 0;
    if (startId) imgs.forEach(function (it, n) { if (it[0] === startId) start = n; });
    load(start);
    return {
      key: function (e) {
        var k = e.key;
        if (k === '+' || k === '=') zoomAt(1.3, null, null, true);
        else if (k === '-' || k === '_') zoomAt(1 / 1.3, null, null, true);
        else if (k === '0') fitW(true);
        else if (k === 'h' || k === 'H' || e.code === 'KeyH') goRect(st.hl + 1);
      },
      resize: function (anim) { if (!st.iw) return; if (st.hl >= 0) goRect(st.hl); else fitW(anim); }
    };
  }

  // ── 부록 겹쳐 보기 ────────────────────────────────────────────────────
  // 본문 장의 [data-peek="장 id"] 단추가 그 장을 지금 자리에 띄운다. 쪽을 옮기지
  // 않으므로 질문에 답한 뒤 닫으면 보던 자리 그대로다. 장을 복제해 단계를 모두 펼치고
  // 화면에 맞게 줄인다.
  //   발표 중 차례로 열기 — 장에 data-peek-seq 를 주면 화면 클릭마다 그 장의 단추를
  //   차례로 연다(열린 동안 클릭 = 닫기). 다 열면 클릭이 다시 「다음」이 된다.
  var PK = { el: null, stage: null, clone: null, from: null, modal: null, seq: 0, seqSlide: null };
  function openPeek(btn, seqInfo) {
    var id = btn.getAttribute('data-peek'), t = D.getElementById(id);
    if (!t || !t.classList.contains('bl-sl')) { toast('겹쳐 볼 장 없음 — ' + id); return; }
    if (!PK.el) {
      PK.el = mk('div'); PK.el.id = 'bl-peek'; PK.el.setAttribute('role', 'dialog'); PK.el.setAttribute('aria-modal', 'true');
      var head = mk('div', 'bl-peek-head');
      PK.badge = mk('b'); PK.title = mk('h3'); PK.help = mk('span');
      var x = mk('button', null, '×'); x.type = 'button'; x.setAttribute('aria-label', '닫기');
      x.onclick = closePeek;
      head.appendChild(PK.badge); head.appendChild(PK.title); head.appendChild(PK.help); head.appendChild(x);
      PK.stage = mk('div', 'bl-peek-stage');
      PK.el.appendChild(head); PK.el.appendChild(PK.stage);
      PK.el.addEventListener('click', function (e) {
        if (PK.el.classList.contains('is-seq') || e.target === PK.stage || e.target === PK.el) closePeek();
      });
      PK.el.addEventListener('wheel', function (e) { e.preventDefault(); }, { passive: false });
      B.appendChild(PK.el);
      PK.modal = { el: PK.el, key: function (e) {
        if (e.key === 'Escape') closePeek();
        else if (e.key === 'Tab') { trapTab(e, PK.el); return false; }
      }, close: closePeek };
    }
    var c = t.cloneNode(true);
    c.removeAttribute('id');
    $$('[id]', c).forEach(function (n) { n.removeAttribute('id'); });
    $$('[data-f]', c).forEach(function (n) { n.classList.add('is-shown'); });
    c.classList.add('in', 'bl-rs');
    c.setAttribute('aria-hidden', 'true');
    PK.stage.textContent = '';
    PK.stage.appendChild(c);
    PK.clone = c; PK.from = btn;
    var kd = kind(t);
    var badge = kd === 'apx' ? '부록 ' + (apxList.indexOf(t) + 1) + '쪽' : kd === 'body' ? '본문 ' + (bodyList.indexOf(t) + 1) + '쪽' : '표지';
    if (seqInfo) badge += ' · ' + seqInfo;
    PK.badge.textContent = badge;
    PK.title.textContent = titleOf(t);
    PK.help.textContent = btn.getAttribute('data-help') || (seqInfo ? '아무 곳이나 누르면 닫힘' : 'Esc · 바깥 클릭 — 닫기');
    PK.el.classList.toggle('is-seq', !!seqInfo);
    PK.el.hidden = false;
    pushModal(PK.modal);
    fitPeek();
    if (!seqInfo && isPresent()) {
      // 발표 중 직접 누른 단추는 차례 열기의 다음 자리를 정한다
      var list = peekList(slides[i]);
      var k = list.indexOf(btn);
      if (k >= 0) { PK.seq = k + 1; PK.seqSlide = slides[i]; }
    }
  }
  function fitPeek() {
    if (!PK.clone || !PK.el || PK.el.hidden) return;
    var r = PK.stage.getBoundingClientRect();
    var s = Math.min(r.width / W.innerWidth, r.height / W.innerHeight) * .96;
    PK.clone.style.transform = 'translate(-50%,-50%) scale(' + s + ')';
  }
  function closePeek() {
    if (!PK.el || PK.el.hidden) return;
    PK.el.hidden = true;
    PK.stage.textContent = '';
    PK.clone = null;
    popModal(PK.modal);
    if (PK.from && PK.from.focus && !isPresent()) PK.from.focus();
  }
  function peekList(s) {
    var order = s.getAttribute('data-peek-seq');
    var btns = $$('[data-peek]', s);
    if (order && order !== '' && order !== 'auto') {
      var ids = order.split(',').map(function (x) { return x.trim(); });
      return ids.map(function (id) { return btns.filter(function (b) { return b.getAttribute('data-peek') === id; })[0]; })
        .filter(Boolean);
    }
    return btns;
  }
  function peekSeqReset() { if (PK.seqSlide && PK.seqSlide !== slides[i]) { PK.seq = 0; PK.seqSlide = null; } }
  function peekSeqClick() {
    var s = slides[i];
    if (!s.hasAttribute('data-peek-seq')) return false;
    var list = peekList(s);
    if (PK.seqSlide !== s) { PK.seq = 0; PK.seqSlide = s; }
    if (PK.seq >= list.length) return false;
    var b = list[PK.seq];
    PK.seq++;
    openPeek(b, PK.seq + '/' + list.length);
    return true;
  }

  // ── 원문 보기 ─────────────────────────────────────────────────────────
  // [data-doc="id"] → id 가 같은 <script type="application/json"> 의 {"title","html","file"}.
  // 여기 주석에도 script 닫는 태그를 쓰지 않는다 — 한 파일로 묶으면 그 자리에서 스크립트가 끊긴다.
  // html 안의 .bl-hl 단락이 강조다. 단추마다 그 강조로 바로 간다. file({name,type,b64})을
  // 주면 「원본 내려받기」가 생긴다. 근거 패널에서 열면 닫을 때 근거 패널로 돌아간다.
  var DOC = { el: null, back: null, frame: null, modal: null, fromEv: false, data: null, from: null };
  function openDoc(btn) {
    var id = btn.getAttribute('data-doc'), src = D.getElementById(id), data;
    if (!src) { toast('원문 없음 — ' + id); return; }
    try { data = JSON.parse(src.textContent); } catch (e) { toast('원문을 읽지 못함 — ' + id); return; }
    DOC.data = data; DOC.from = btn;
    DOC.fromEv = !!(EVP.el && !EVP.el.hidden && EVP.el.contains(btn));
    if (DOC.fromEv) EVP.el.hidden = true;
    if (!DOC.el) {
      DOC.back = mk('div'); DOC.back.id = 'bl-doc-back';
      DOC.back.addEventListener('click', closeDoc);
      DOC.el = mk('div'); DOC.el.id = 'bl-doc'; DOC.el.setAttribute('role', 'dialog'); DOC.el.setAttribute('aria-modal', 'true');
      B.appendChild(DOC.back); B.appendChild(DOC.el);
      DOC.modal = { el: DOC.el, key: function (e) {
        if (e.key === 'Escape') closeDoc();
        else if (e.key === 'Tab') { trapTab(e, DOC.el); return false; }
      }, close: closeDoc };
    }
    DOC.el.textContent = '';
    var head = mk('div', 'bl-doc-head');
    head.appendChild(mk('h3', null, data.title || '원문'));
    var x = mk('button', null, '×'); x.type = 'button'; x.setAttribute('aria-label', '원문 닫기'); x.onclick = closeDoc;
    head.appendChild(x);
    var tools = mk('div', 'bl-doc-tools');
    var top = mk('button', null, '문서 처음'); top.type = 'button';
    tools.appendChild(top);
    tools.appendChild(mk('span', 'bl-lbl', '강조'));
    var chips = mk('span', 'bl-row');
    tools.appendChild(chips);
    if (data.file && data.file.b64) {
      var dl = mk('button', null, '원본 내려받기'); dl.type = 'button';
      dl.onclick = function () {
        try {
          var bin = atob(data.file.b64), u8 = new Uint8Array(bin.length);
          for (var k = 0; k < bin.length; k++) u8[k] = bin.charCodeAt(k);
          var u = URL.createObjectURL(new Blob([u8], { type: data.file.type || 'application/octet-stream' }));
          var a = mk('a'); a.href = u; a.download = data.file.name || 'original'; B.appendChild(a); a.click();
          setTimeout(function () { URL.revokeObjectURL(u); a.remove(); }, 30000);
        } catch (e) { toast('원본 내려받기 실패'); }
      };
      tools.appendChild(dl);
    }
    var fr = mk('iframe'); fr.setAttribute('sandbox', 'allow-same-origin'); fr.title = data.title || '원문';
    DOC.frame = fr;
    DOC.el.appendChild(head); DOC.el.appendChild(tools); DOC.el.appendChild(fr);
    var want = parseInt(btn.getAttribute('data-hl'), 10);
    fr.addEventListener('load', function () {
      var d;
      try { d = fr.contentDocument; } catch (e) { return; }
      if (!d) return;
      var stl = d.createElement('style');
      stl.textContent = '.bl-hl{background:' + getComputedStyle(R).getPropertyValue('--br-warn-bg') + ';scroll-margin:30vh}' +
        '.bl-hl.is-cur{outline:3px solid ' + getComputedStyle(R).getPropertyValue('--br-warn-text') + ';outline-offset:2px}';
      (d.head || d.documentElement).appendChild(stl);
      d.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); closeDoc(); } });
      var hs = Array.prototype.slice.call(d.querySelectorAll('.bl-hl'));
      chips.textContent = '';
      hs.forEach(function (h, k) {
        var c = mk('button', null, h.getAttribute('data-label') || String(k + 1)); c.type = 'button';
        c.onclick = function () { jump(k); };
        chips.appendChild(c);
      });
      function jump(k) {
        hs.forEach(function (h, n) { h.classList.toggle('is-cur', n === k); });
        $$('button', chips).forEach(function (b, n) { b.classList.toggle('is-on', n === k); });
        if (hs[k]) hs[k].scrollIntoView({ block: 'center' });
      }
      top.onclick = function () { hs.forEach(function (h) { h.classList.remove('is-cur'); }); d.documentElement.scrollTop = 0; d.body.scrollTop = 0; };
      setTimeout(function () { if (!isNaN(want) && hs[want]) jump(want); }, 120);
    });
    fr.srcdoc = data.html || '';
    DOC.back.hidden = false; DOC.el.hidden = false;
    pushModal(DOC.modal);
    x.focus();
  }
  function closeDoc() {
    if (!DOC.el || DOC.el.hidden) return;
    DOC.el.hidden = true; DOC.back.hidden = true;
    DOC.frame && DOC.frame.removeAttribute('srcdoc');
    popModal(DOC.modal);
    if (DOC.fromEv && EVP.el) { EVP.el.hidden = false; }
    else if (DOC.from && DOC.from.focus) DOC.from.focus();
  }

  // ── 영상 ──────────────────────────────────────────────────────────────
  // [data-video="id"] → id 가 같은 <script type="text/plain" data-type="video/mp4"> 의 base64.
  // 또는 data-video 에 파일 경로. 처음 열 때 한 번만 풀어 둔다.
  var VID = { el: null, video: null, modal: null, from: null, urls: {} };
  function openVideo(btn) {
    var ref = btn.getAttribute('data-video'), url = VID.urls[ref];
    if (!url) {
      var src = D.getElementById(ref);
      if (src && src.tagName === 'SCRIPT') {
        try {
          var bin = atob(src.textContent.replace(/\s+/g, '')), u8 = new Uint8Array(bin.length);
          for (var k = 0; k < bin.length; k++) u8[k] = bin.charCodeAt(k);
          url = URL.createObjectURL(new Blob([u8], { type: src.getAttribute('data-type') || 'video/mp4' }));
        } catch (e) { toast('영상을 풀지 못함 — ' + ref); return; }
      } else url = ref;
      VID.urls[ref] = url;
    }
    if (!VID.el) {
      VID.el = mk('div'); VID.el.id = 'bl-vid'; VID.el.setAttribute('role', 'dialog'); VID.el.setAttribute('aria-modal', 'true');
      var box = mk('div', 'bl-vid-box');
      VID.video = mk('video'); VID.video.controls = true; VID.video.setAttribute('playsinline', ''); VID.video.preload = 'none';
      var x = mk('button', null, '×'); x.type = 'button'; x.setAttribute('aria-label', '영상 닫기'); x.onclick = closeVideo;
      box.appendChild(VID.video); box.appendChild(x); VID.el.appendChild(box);
      VID.el.addEventListener('click', function (e) { if (e.target === VID.el) closeVideo(); });
      B.appendChild(VID.el);
      VID.modal = { el: VID.el, key: function (e) {
        if (e.key === 'Escape') closeVideo();
        else if (e.key === 'Tab') { trapTab(e, VID.el); return false; }
        else if (e.key === ' ' || e.key === 'k') { if (VID.video.paused) VID.video.play(); else VID.video.pause(); }
      }, close: closeVideo };
    }
    VID.from = btn;
    VID.video.src = url;
    VID.el.hidden = false;
    pushModal(VID.modal);
    var p = VID.video.play();
    if (p && p.catch) p.catch(function () { /* 자동 재생이 막히면 ▶ 를 누른다 */ });
    VID.el.querySelector('button').focus();
  }
  function closeVideo() {
    if (!VID.el || VID.el.hidden) return;
    try { VID.video.pause(); VID.video.currentTime = 0; } catch (e) { /* 무시 */ }
    VID.el.hidden = true;
    popModal(VID.modal);
    if (VID.from && VID.from.focus) VID.from.focus();
  }

  // ── 그림 크게 보기 ────────────────────────────────────────────────────
  // .bl-fig 안의 그림 · .bl-shot 의 캡처 · [data-zoom] 을 누르면 화면 가득 띄운다.
  // 시안이 여럿인 그림은 ← → 로 넘긴다.
  var LB = { el: null, items: [], idx: 0, modal: null, from: null, fig: null };
  function openLightbox(target) {
    var fig = target.closest('.bl-fig');
    LB.fig = fig;
    LB.items = fig ? $$(':scope > [data-v]', fig) : [target];
    if (!LB.items.length) LB.items = [target];
    LB.idx = Math.max(0, LB.items.indexOf(target));
    LB.from = target;
    if (!LB.el) {
      LB.el = mk('div'); LB.el.id = 'bl-lb'; LB.el.setAttribute('role', 'dialog'); LB.el.setAttribute('aria-modal', 'true');
      LB.el.addEventListener('click', function (e) { if (!e.target.closest('button')) closeLightbox(); });
      B.appendChild(LB.el);
      LB.modal = { el: LB.el, key: function (e) {
        if (e.key === 'Escape') closeLightbox();
        else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') lbStep(e.key === 'ArrowRight' ? 1 : -1);
        else if (e.key === 'Tab') { trapTab(e, LB.el); return false; }
      }, close: closeLightbox };
    }
    lbPaint();
    LB.el.hidden = false;
    pushModal(LB.modal);
  }
  function lbPaint() {
    var it = LB.items[LB.idx];
    LB.el.textContent = '';
    var f = mk('figure'), c = it.cloneNode(true);
    c.removeAttribute('id'); c.style.display = 'block';
    f.appendChild(c);
    var capText = it.getAttribute('data-cap') || it.getAttribute('alt') || it.getAttribute('aria-label') || '';
    if (LB.items.length > 1) {
      var ab = mk('div', 'bl-fig-ab');
      LB.items.forEach(function (x, n) {
        var b = mk('button', null, x.getAttribute('data-v') || String(n + 1)); b.type = 'button';
        b.setAttribute('aria-pressed', String(n === LB.idx));
        b.onclick = function (e) { e.stopPropagation(); LB.idx = n; lbSync(); lbPaint(); };
        ab.appendChild(b);
      });
      f.appendChild(ab);
    }
    if (capText) f.appendChild(mk('figcaption', null, capText));
    var x = mk('button', 'bl-lb-x', '×'); x.type = 'button'; x.setAttribute('aria-label', '닫기');
    x.onclick = closeLightbox;
    LB.el.appendChild(f); LB.el.appendChild(x);
    x.focus();
  }
  function lbStep(d) {
    if (LB.items.length < 2) return;
    LB.idx = (LB.idx + d + LB.items.length) % LB.items.length;
    lbSync(); lbPaint();
  }
  function lbSync() { if (LB.fig && LB.fig.__blSel) LB.fig.__blSel(LB.items[LB.idx].getAttribute('data-v')); }
  function closeLightbox() {
    if (!LB.el || LB.el.hidden) return;
    LB.el.hidden = true;
    popModal(LB.modal);
  }

  // ── 부품 ──────────────────────────────────────────────────────────────
  function slideOf(el) { return el.closest('.bl-sl'); }
  function addWidget(el, sync) { WIDGETS.push({ el: el, slide: slideOf(el), sync: sync }); }
  function shownIn(el) { return $$('[data-f]', el).filter(function (m) { return m.classList.contains('is-shown'); }).length; }

  // 순번 — 자식마다 --i 를 단다. 차례 등장 · 칸 채우기에 쓴다. 값을 주면 그 선택자로 센다
  $$('[data-stagger]').forEach(function (el) {
    var sel = el.getAttribute('data-stagger');
    var list = sel ? $$(sel, el) : Array.prototype.slice.call(el.children);
    list.forEach(function (c, k) { c.style.setProperty('--i', k); });
  });

  // 와플 — data-total · data-on(· data-alt · data-cols · data-icon) 으로 칸을 깐다
  $$('.bl-waffle[data-total]').forEach(function (w) {
    if (w.children.length) return;
    var total = +w.getAttribute('data-total') || 0, on = +w.getAttribute('data-on') || 0, alt = +w.getAttribute('data-alt') || 0;
    var icon = w.getAttribute('data-icon');
    if (w.getAttribute('data-cols')) w.style.setProperty('--cols', w.getAttribute('data-cols'));
    for (var k = 0; k < total; k++) {
      var c = D.createElement('i');
      if (icon) c.className = 'bl-i bl-i--' + icon;
      if (k < on) c.classList.add('is-on'); else if (k < on + alt) c.classList.add('is-alt');
      c.style.setProperty('--i', k);
      w.appendChild(c);
    }
    if (!w.getAttribute('aria-label')) w.setAttribute('aria-label', on + ' / ' + total);
    w.setAttribute('role', 'img');
  });

  // 탭 — 단추를 누르면 그 판. 단추에 data-at="단계 값" 을 주면 발표 중 그 단계에서 넘어간다.
  // 첫 탭에는 data-at 을 주지 않는다 — 0단계(장에 들어온 직후)의 기본 판이다. 첫 탭에도
  // data-at="1" 을 주면 첫 클릭에 화면이 그대로인 헛클릭이 생긴다.
  // 검토(펼침)에서는 단계와 무관하게 첫 판을 보인다 — 보통 탭처럼 읽는다.
  // 손으로 고른 판은 단계가 바뀔 때까지 그대로 둔다.
  $$('.bl-tabset').forEach(function (set) {
    var btns = $$(':scope > .bl-tabs > button[data-v]', set), panes = $$(':scope > .bl-pane[data-v]', set);
    if (!btns.length) return;
    set.setAttribute('data-ready', '');
    var bar = set.querySelector(':scope > .bl-tabs');
    if (bar) bar.setAttribute('role', 'tablist');
    btns.forEach(function (b) { b.type = 'button'; b.setAttribute('role', 'tab'); });
    panes.forEach(function (p) { p.setAttribute('role', 'tabpanel'); });
    var manual = null, lastLv = null;
    function sel(v) {
      btns.forEach(function (b) { b.setAttribute('aria-selected', String(b.getAttribute('data-v') === v)); });
      panes.forEach(function (p) { p.classList.toggle('is-on', p.getAttribute('data-v') === v); });
      set.setAttribute('data-tab', v);
    }
    btns.forEach(function (b) {
      b.addEventListener('click', function () { manual = b.getAttribute('data-v'); sel(manual); });
    });
    var pre = btns.filter(function (b) { return b.getAttribute('aria-selected') === 'true'; })[0] || btns[0];
    sel(pre.getAttribute('data-v'));
    var linked = btns.some(function (b) { return b.hasAttribute('data-at'); });
    if (!linked) return;
    addWidget(set, function (active, ctx) {
      var k = slides.indexOf(slideOf(set)), th = ctx.staged ? threshold(k) : 0;
      if (lastLv !== th) { manual = null; lastLv = th; }
      if (manual) return;
      var best = null;
      btns.forEach(function (b) {
        var at = parseFloat(b.getAttribute('data-at'));
        if (!isNaN(at) && at <= th && (!best || at >= parseFloat(best.getAttribute('data-at')))) best = b;
      });
      sel((best || btns[0]).getAttribute('data-v'));
    });
  });

  // 세그먼트 — 같은 그림의 보기만 바꾼다. <div class="bl-seg" data-key="view"> 단추마다 data-v.
  // 고른 값이 범위(가장 가까운 [data-scope], 없으면 장)에 data-view="…" 로 붙고,
  // 그 안의 [data-when="view=plan"] 요소가 맞을 때만 보인다
  function applyWhen(scope) {
    $$('[data-when]', scope).forEach(function (el) {
      var ok = el.getAttribute('data-when').split('&').every(function (c) {
        var m = c.split('='), want = (m[1] || '').split('|').map(function (x) { return x.trim(); });
        return want.indexOf(scope.getAttribute('data-' + m[0].trim()) || '') >= 0;
      });
      el.hidden = !ok;
    });
  }
  $$('.bl-seg').forEach(function (seg) {
    var key = seg.getAttribute('data-key') || 'view';
    var scope = seg.closest('[data-scope]') || slideOf(seg) || B;
    var btns = $$('button[data-v]', seg);
    if (!btns.length) return;
    function set(v) {
      scope.setAttribute('data-' + key, v);
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === v)); });
      applyWhen(scope);
    }
    btns.forEach(function (b) { b.type = 'button'; b.addEventListener('click', function () { set(b.getAttribute('data-v')); }); });
    var pre = btns.filter(function (b) { return b.getAttribute('aria-pressed') === 'true'; })[0] || btns[0];
    set(pre.getAttribute('data-v'));
  });

  // 시안 토글 그림 — .bl-fig-ab 단추(data-v) ↔ 그림(data-v)
  $$('.bl-fig').forEach(function (fig) {
    var items = $$(':scope > [data-v]', fig), btns = $$('.bl-fig-ab > button[data-v]', fig);
    if (!items.length) return;
    fig.setAttribute('data-ready', '');
    function sel(v) {
      items.forEach(function (x) { x.classList.toggle('is-on', x.getAttribute('data-v') === v); });
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === v)); });
    }
    fig.__blSel = sel;
    btns.forEach(function (b) { b.type = 'button'; b.addEventListener('click', function () { sel(b.getAttribute('data-v')); }); });
    sel(items[0].getAttribute('data-v'));
  });

  // 노선도 — 역이 2.6초마다 돌며 상세 카드가 바뀐다. 역을 누르면 고정, 다시 누르면 풀림.
  // 단계로 접힌 노선(data-f)의 역은 건너뛴다. 장이 화면에 있을 때만 돈다.
  $$('.bl-route').forEach(function (rt) {
    var sts = $$('.bl-route-st[data-i]', rt), cards = $$('.bl-route-card[data-i]', rt);
    if (!sts.length) return;
    rt.setAttribute('data-ready', '');
    var side = rt.querySelector('.bl-route-side') || rt;
    var empty = side.querySelector('.bl-route-empty');
    if (!empty) { empty = mk('div', 'bl-route-empty', '역을 고르면 상세'); empty.hidden = true; side.appendChild(empty); }
    var cur = null, pin = null, timer = 0;
    sts.forEach(function (b) { if (b.tagName === 'BUTTON') b.type = 'button'; });
    function show(btn) {
      cur = btn;
      sts.forEach(function (b) { b.classList.toggle('is-on', b === btn); });
      var v = btn ? btn.getAttribute('data-i') : null, hit = false;
      cards.forEach(function (c) { var on = c.getAttribute('data-i') === v; c.classList.toggle('is-on', on); hit = hit || on; });
      empty.hidden = hit;
    }
    function avail() {
      return sts.filter(function (b) { var f = b.closest('[data-f]'); return !f || f.classList.contains('is-shown'); });
    }
    function tick() {
      var list = avail();
      if (!list.length) { show(null); return; }
      var k = list.indexOf(cur);
      show(list[(k + 1) % list.length]);
    }
    function stop() { clearInterval(timer); timer = 0; }
    sts.forEach(function (b) {
      b.addEventListener('click', function () {
        if (pin === b) { pin = null; b.removeAttribute('aria-pressed'); return; }
        pin = b; sts.forEach(function (x) { x.removeAttribute('aria-pressed'); }); b.setAttribute('aria-pressed', 'true');
        stop(); show(b);
      });
    });
    show(sts[0]);
    addWidget(rt, function (active) {
      if (cur && avail().indexOf(cur) < 0) show(avail()[0] || null);
      if (active && !pin && !reduced()) { if (!timer) timer = setInterval(tick, 2600); }
      else stop();
    });
  });

  // 장면 — 같은 자리에 장면을 갈아 끼운다. 단계 표식(data-f)이 열린 수만큼 장면이
  // 넘어가고, 목록 단추를 누르면 그 장면부터 5.6초마다 끝까지 저절로 넘어간다.
  $$('.bl-scenebox').forEach(function (box) {
    var holder = box.querySelector('.bl-scenes');
    var sc = $$('.bl-scene[data-sc]', box), nav = $$('.bl-scene-nav button[data-k]', box);
    if (!holder || !sc.length) return;
    holder.setAttribute('data-ready', '');
    var cur = 0, auto = 0;
    function show(n) {
      n = clamp(n, 1, sc.length);
      if (n === cur) return;
      cur = n;
      sc.forEach(function (s) {
        var on = +s.getAttribute('data-sc') === n;
        if (on) { s.classList.remove('is-cur'); void s.offsetWidth; }
        s.classList.toggle('is-cur', on);
      });
      nav.forEach(function (b) {
        var k = +b.getAttribute('data-k');
        b.classList.toggle('is-ok', k < n); b.classList.toggle('is-now', k === n);
      });
      box.setAttribute('data-st', n);
    }
    function stopAuto() { clearInterval(auto); auto = 0; }
    nav.forEach(function (b) {
      b.type = 'button';
      b.addEventListener('click', function () {
        stopAuto(); cur = 0; show(+b.getAttribute('data-k'));
        if (reduced()) return;
        auto = setInterval(function () { if (cur >= sc.length) stopAuto(); else show(cur + 1); }, 5600);
      });
    });
    show(1);
    addWidget(box, function (active, ctx) {
      if (!active) stopAuto();
      if (auto) return;
      show(ctx.staged ? Math.max(1, shownIn(box)) : sc.length);
    });
  });

  // 초점 행 — 표식이 열린 수만큼 그 번호의 행을 밝히고 짝 카드를 연다. 행을 누르면 고정.
  // 펼침(검토)에서는 밝히지 않는다 — 표를 통째로 읽는 자리다. 카드 data-i="0" 이 기본
  $$('.bl-focusset').forEach(function (set) {
    set.setAttribute('data-ready', '');
    var rows = $$('[data-i]', set).filter(function (r) { return !r.closest('.bl-focus-cards'); });
    var cards = $$('.bl-focus-cards > [data-i]', set);
    var pin = null;
    function apply(n) {
      set.classList.toggle('is-active', n != null);
      rows.forEach(function (r) {
        var on = n != null && r.getAttribute('data-i') === n;
        r.classList.toggle('is-focus', on); r.classList.toggle('is-dim', n != null && !on);
        if (pin === r.getAttribute('data-i')) r.setAttribute('data-pinned', ''); else r.removeAttribute('data-pinned');
      });
      var want = n != null ? n : '0', hit = false;
      cards.forEach(function (c) { var on = c.getAttribute('data-i') === want; c.classList.toggle('is-on', on); hit = hit || on; });
      if (!hit && cards[0]) cards[0].classList.add('is-on');
    }
    function auto(ctx) { var k = ctx && ctx.staged ? shownIn(set) : 0; apply(pin != null ? pin : (k ? String(k) : null)); }
    rows.forEach(function (r) {
      r.addEventListener('click', function () {
        var v = r.getAttribute('data-i');
        pin = pin === v ? null : v;
        auto({ staged: staged() && slideOf(set) === slides[i] });
      });
    });
    apply(null);
    addWidget(set, function (active, ctx) { auto(ctx); });
  });

  // 카드 고르기 — 누른 카드만 남기고 나머지를 흐리게. [data-when-pick="값"] 이 따라 열린다
  $$('.bl-pickset').forEach(function (set) {
    var items = $$('[data-pick]', set), cur = null;
    function pick(v) {
      cur = v;
      set.classList.toggle('has-pick', !!v);
      set.setAttribute('data-sel', v || '');
      items.forEach(function (it) { it.setAttribute('aria-pressed', String(it.getAttribute('data-pick') === v)); });
      $$('[data-when-pick]', set).forEach(function (el) { el.classList.toggle('is-on', el.getAttribute('data-when-pick') === v); });
    }
    items.forEach(function (it) {
      it.setAttribute('role', 'button'); it.tabIndex = 0; it.setAttribute('aria-pressed', 'false');
      it.addEventListener('click', function () { var v = it.getAttribute('data-pick'); pick(cur === v ? null : v); });
      it.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); it.click(); }
      });
    });
  });

  // 도넛 — 조각이나 범례에 손을 대면 그 항목이 가운데로 올라온다. 떼면 합계로 돌아간다
  // 글자 폭(em) 어림 — donut.py 와 같은 셈. 숫자 .58 · 쉼표 .28 · 한글 1 · 그 밖 .6
  function emOf(t) {
    var w = 0;
    for (var q = 0; q < t.length; q++) {
      var ch = t.charAt(q);
      w += /\d/.test(ch) ? .58 : /[,.]/.test(ch) ? .28 : t.charCodeAt(q) >= 0x1100 ? 1 : .6;
    }
    return w;
  }
  $$('.bl-donut-box').forEach(function (box) {
    var dn = box.querySelector('.bl-donut');
    if (!dn) return;
    var c = dn.querySelector('.bl-donut-c'), orig = c ? c.innerHTML : '';
    var segs = $$('.bl-donut-s[data-k]', box), lis = $$('.bl-donut-leg > li[data-k]', box);
    function on(k) {
      dn.classList.add('is-hov');
      segs.forEach(function (s) { s.classList.toggle('is-on', s.getAttribute('data-k') === k); });
      lis.forEach(function (l) { l.classList.toggle('is-on', l.getAttribute('data-k') === k); });
      var li = lis.filter(function (l) { return l.getAttribute('data-k') === k; })[0];
      if (c && li) {
        c.textContent = '';
        var v = li.querySelector('b'), n = li.querySelector('span');
        // 숫자와 단위를 갈라 합계와 같은 모양으로 — 폭(--w)을 줘야 「1,150시간」이 구멍 안에 든다
        var t = (li.getAttribute('data-v') || (v ? v.textContent : '')).trim();
        var m = t.match(/^([-+−]?[\d.,]*\d)(.*)$/), b = mk('b', null, m ? m[1] : t);
        if (m && m[2]) b.appendChild(mk('small', null, m[2]));
        b.style.setProperty('--w', (emOf(m ? m[1] : t) + .5 * emOf(m ? m[2] : '') + .1).toFixed(2));
        c.appendChild(b);
        c.appendChild(mk('span', 'bl-cap', (n ? n.textContent : '') + (li.getAttribute('data-p') ? ' · ' + li.getAttribute('data-p') : '')));
      }
    }
    function off() {
      dn.classList.remove('is-hov');
      segs.concat(lis).forEach(function (x) { x.classList.remove('is-on'); });
      if (c) c.innerHTML = orig;
    }
    lis.forEach(function (l) { l.tabIndex = 0; });
    segs.concat(lis).forEach(function (x) {
      var k = x.getAttribute('data-k');
      x.addEventListener('mouseenter', function () { on(k); });
      x.addEventListener('focus', function () { on(k); });
      x.addEventListener('mouseleave', off);
      x.addEventListener('blur', off);
    });
  });

  // 조작형 누적 막대 — 장 안의 <script type="application/json" class="bl-sc-data"> 를 그린다.
  //   {"unit": "억원", "cats": [{"k": "lab", "name": "인건비", "c": "1"}],
  //    "groups": {"a": "본부"}, "views": {"nat": "성격별", "fn": "기능별"},
  //    "rows": [{"id": "r1", "name": "가 본부", "sub": "시험 · 교정", "grp": "a", "total": 1200,
  //              "parts": [["lab", 420], ["mat", 180, true]], "fn": [["sell", 300]],
  //              "rate": 12.4, "key": true, "pick": true, "note": "…", "src": "…"}]}
  //   parts 의 셋째 값 true 는 추정치(빗금). views 를 주면 rows 마다 그 이름의 배열을 쓴다.
  var scTip = null;
  function scTipEl() {
    if (!scTip) { scTip = mk('div', 'bl-sc-tip'); scTip.hidden = true; B.appendChild(scTip); }
    return scTip;
  }
  function niceStep(max) {
    var raw = max / 4, p = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), n = raw / p;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p;
  }
  function fmtNum(v) {
    var a = Math.abs(v), s = a >= 100 ? Math.round(v).toString() : a >= 10 ? v.toFixed(1) : v.toFixed(1);
    return s.replace(/\.0$/, '').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  $$('.bl-sc').forEach(function (box) {
    var src = box.querySelector('script.bl-sc-data'), data;
    if (!src) return;
    try { data = JSON.parse(src.textContent); } catch (e) { return; }
    var cats = data.cats || [], rows = data.rows || [], unit = data.unit || '', catBy = {};
    cats.forEach(function (c) { catBy[c.k] = c; });
    var views = data.views || null, viewKeys = views ? Object.keys(views) : [];
    var S = { mode: 'rel', view: viewKeys[0] || 'parts',
              sel: rows.filter(function (r) { return r.pick !== false; }).map(function (r) { return r.id; }) };
    var DEF = S.sel.slice();
    var ctl = box.querySelector('.bl-sc-ctl') || box.appendChild(mk('div', 'bl-sc-ctl'));
    var pick = box.querySelector('.bl-sc-pick') || box.appendChild(mk('div', 'bl-sc-pick'));
    var leg = box.querySelector('.bl-sc-leg') || box.appendChild(mk('ul', 'bl-leg bl-sc-leg'));
    var chart = box.querySelector('.bl-sc-chart') || box.appendChild(mk('div', 'bl-sc-chart'));
    function seg(key, opts) {
      var g = mk('div', 'bl-seg');
      opts.forEach(function (o) {
        var b = mk('button', null, o[1]); b.type = 'button'; b.setAttribute('data-v', o[0]);
        b.onclick = function () { S[key] = o[0]; paint(); };
        g.appendChild(b);
      });
      g.__key = key;
      return g;
    }
    ctl.textContent = '';
    var segs = [seg('mode', [['rel', '비율 %'], ['abs', '금액 ' + unit]])];
    if (viewKeys.length > 1) segs.push(seg('view', viewKeys.map(function (k) { return [k, views[k]]; })));
    segs.forEach(function (g) { ctl.appendChild(g); });
    var groups = data.groups || {};
    function partsOf(r) { var p = r[S.view] || r.parts || []; return p.filter(function (x) { return catBy[x[0]]; }); }
    function buildPick() {
      pick.textContent = '';
      var keys = Object.keys(groups);
      if (!keys.length) keys = [''];
      keys.forEach(function (g) {
        if (g) {
          var gb = mk('button', null, groups[g]); gb.type = 'button'; gb.className = 'is-grp';
          gb.onclick = function () {
            var ids = rows.filter(function (r) { return r.grp === g; }).map(function (r) { return r.id; });
            var all = ids.every(function (id) { return S.sel.indexOf(id) >= 0; });
            S.sel = all ? S.sel.filter(function (id) { return ids.indexOf(id) < 0; }) : S.sel.concat(ids.filter(function (id) { return S.sel.indexOf(id) < 0; }));
            if (!S.sel.length) S.sel = ids.slice(0, 1);
            paint();
          };
          pick.appendChild(gb);
        }
        rows.filter(function (r) { return !g || r.grp === g; }).forEach(function (r) {
          var b = mk('button', r.sub && r.seg ? 'is-sub' : null, r.name); b.type = 'button'; b.setAttribute('data-id', r.id);
          b.onclick = function () {
            var k = S.sel.indexOf(r.id);
            if (k >= 0) { if (S.sel.length > 1) S.sel.splice(k, 1); } else S.sel.push(r.id);
            paint();
          };
          pick.appendChild(b);
        });
      });
      var rs = mk('button', null, '기본'); rs.type = 'button'; rs.onclick = function () { S.sel = DEF.slice(); paint(); };
      var al = mk('button', null, '전체'); al.type = 'button'; al.onclick = function () { S.sel = rows.map(function (r) { return r.id; }); paint(); };
      pick.appendChild(rs); pick.appendChild(al);
    }
    function paint() {
      segs.forEach(function (g) {
        $$('button', g).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === S[g.__key])); });
      });
      $$('button[data-id]', pick).forEach(function (b) { b.setAttribute('aria-pressed', String(S.sel.indexOf(b.getAttribute('data-id')) >= 0)); });
      var list = rows.filter(function (r) { return S.sel.indexOf(r.id) >= 0 && partsOf(r).length; });
      var used = {};
      chart.textContent = '';
      if (!list.length) { chart.appendChild(mk('div', 'bl-sc-empty', '고른 대상 없음 — 이 보기에 값이 없는 대상')); leg.textContent = ''; return; }
      var maxT = Math.max.apply(null, list.map(function (r) { return r.total || partsOf(r).reduce(function (a, p) { return a + p[1]; }, 0); }));
      var step = S.mode === 'rel' ? 20 : niceStep(maxT), top = S.mode === 'rel' ? 100 : Math.ceil(maxT / step) * step;
      var ax = mk('div', 'bl-stack-ax'), axd = mk('div');
      ax.appendChild(mk('span')); ax.appendChild(axd); ax.appendChild(mk('span', 'bl-axis', S.mode === 'rel' ? '' : unit));
      for (var t = 0; t <= top + 1e-9; t += step) axd.appendChild(mk('span', 'bl-axis', S.mode === 'rel' ? t + '%' : fmtNum(t)));
      chart.appendChild(ax);
      list.forEach(function (r) {
        var ps = partsOf(r), tot = r.total || ps.reduce(function (a, p) { return a + p[1]; }, 0);
        var row = mk('div', 'bl-stack-r' + (r.key ? ' is-key' : ''));
        var nm = mk('div', 'bl-stack-n', r.name);
        if (r.sub) nm.appendChild(mk('small', null, r.sub));
        var bar = mk('div', 'bl-stack-b');
        ps.forEach(function (p) {
          var cat = catBy[p[0]], v = p[1], share = tot ? v / tot * 100 : 0;
          used[p[0]] = used[p[0]] || !!p[2] || false;
          var seg2 = mk('i', p[2] ? 'is-est' : null);
          seg2.setAttribute('data-c', cat.c || '1');
          seg2.style.setProperty('--v', S.mode === 'rel' ? share : v / top * 100);
          seg2.appendChild(mk('b', 'bl-dl', S.mode === 'rel' ? Math.round(share) : fmtNum(v)));
          seg2.addEventListener('mouseenter', function (e) {
            var tip = scTipEl();
            tip.innerHTML = '';
            tip.appendChild(mk('b', null, r.name + ' · ' + cat.name + (p[2] ? ' (추정)' : '')));
            tip.appendChild(mk('div', null, fmtNum(v) + ' ' + unit + ' · ' + share.toFixed(1) + '%'));
            if (r.note) tip.appendChild(mk('div', null, r.note));
            if (r.src) tip.appendChild(mk('div', null, '출처 ' + r.src));
            tip.hidden = false;
            var rc = seg2.getBoundingClientRect();
            tip.style.left = Math.min(W.innerWidth - tip.offsetWidth - 8, rc.left) + 'px';
            tip.style.top = Math.max(8, rc.top - tip.offsetHeight - 8) + 'px';
          });
          seg2.addEventListener('mouseleave', function () { scTipEl().hidden = true; });
          bar.appendChild(seg2);
        });
        if (S.mode === 'abs' && tot < top) {
          var gap = mk('i', 'is-gap'); gap.style.setProperty('--v', (top - tot) / top * 100); bar.appendChild(gap);
        }
        var v = mk('div', 'bl-stack-val' + (r.rate < 0 ? ' is-neg' : ''), r.rate == null ? '' : r.rate.toFixed(1) + '%');
        if (r.rateLabel) v.appendChild(mk('small', null, r.rateLabel));
        row.appendChild(nm); row.appendChild(bar); row.appendChild(v);
        chart.appendChild(row);
      });
      leg.textContent = '';
      cats.forEach(function (c) {
        if (!(c.k in used)) return;
        var li = mk('li'), sw = mk('i');
        li.setAttribute('data-c', c.c || '1'); li.appendChild(sw); li.appendChild(D.createTextNode(c.name));
        leg.appendChild(li);
      });
      if (Object.keys(used).some(function (k) { return used[k]; })) {
        var e = mk('li'), sw2 = mk('i', 'is-est'); e.setAttribute('data-c', 'mute'); e.appendChild(sw2); e.appendChild(D.createTextNode('추정치'));
        leg.appendChild(e);
      }
    }
    buildPick();
    paint();
  });

  // 시뮬레이션 — 장이 화면에 있을 때만 돈다. 같은 장면이 나오도록 난수를 고정한다
  // (렌더 검사의 화면이 매번 같아야 비교할 수 있다). 감속 모드면 멈춘 한 장면.
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  $$('.bl-simq').forEach(function (sim, n) {
    var rnd = rng(7 + n);
    var srcs = $$('.bl-simq-src > [data-c]', sim), q = sim.querySelector('.bl-simq-q');
    var hubN = sim.querySelector('[data-sim-n]'), bins = $$('.bl-simq-bin', sim);
    if (!q || !bins.length) return;
    var done = 0, t1 = 0, t2 = 0, rr = 0;
    function tok(c) { var t = D.createElement('i'); t.setAttribute('data-c', c); return t; }
    function spawn() {
      if (q.children.length < 10) q.appendChild(tok(srcs.length ? srcs[Math.floor(rnd() * srcs.length)].getAttribute('data-c') : '1'));
      t1 = setTimeout(spawn, 850 + rnd() * 400);
    }
    function work() {
      var t = q.firstElementChild;
      if (t) {
        var c = t.getAttribute('data-c'); t.remove();
        done++; if (hubN) hubN.textContent = done;
        var bin = bins[rr++ % bins.length], pile = bin.querySelector(':scope > div') || bin;
        pile.appendChild(tok(c));
        while (pile.children.length > 36) pile.firstElementChild.remove();
        var cnt = bin.querySelector('[data-sim-c]');
        if (cnt) cnt.textContent = (parseInt(cnt.getAttribute('data-n') || '0', 10) + 1) + '건';
        if (cnt) cnt.setAttribute('data-n', parseInt(cnt.getAttribute('data-n') || '0', 10) + 1);
        bin.classList.add('is-hit'); setTimeout(function () { bin.classList.remove('is-hit'); }, 650);
      }
      t2 = setTimeout(work, 2400);
    }
    function still() {
      for (var k = 0; k < 4; k++) q.appendChild(tok(srcs.length ? srcs[k % srcs.length].getAttribute('data-c') : '1'));
      bins.forEach(function (b, k) {
        var pile = b.querySelector(':scope > div') || b;
        for (var m = 0; m < 3 + k * 2; m++) pile.appendChild(tok(srcs.length ? srcs[(m + k) % srcs.length].getAttribute('data-c') : '1'));
        var cnt = b.querySelector('[data-sim-c]');
        if (cnt) { cnt.textContent = (3 + k * 2) + '건'; cnt.setAttribute('data-n', 3 + k * 2); }
      });
      done = bins.reduce(function (a, b, k) { return a + 3 + k * 2; }, 0);
      if (hubN) hubN.textContent = done;
    }
    still();
    addWidget(sim, function (active) {
      if (active && !reduced()) { if (!t1) { spawn(); t2 = setTimeout(work, 1200); } }
      else { clearTimeout(t1); clearTimeout(t2); t1 = t2 = 0; }
    });
  });
  $$('.bl-simg').forEach(function (sim, n) {
    var rnd = rng(31 + n);
    var rows = $$('.bl-simg-r', sim), kpi = sim.querySelector('[data-sim-n]'), bar = sim.querySelector('.bl-simg-bar');
    var cols = parseInt(sim.getAttribute('data-cols') || '24', 10), timer = 0;
    sim.style.setProperty('--cols', cols);
    var W8 = [['a', .72], ['m', .1], ['w', .12], ['i', .06]];
    function pickS() { var r = rnd(), a = 0; for (var k = 0; k < W8.length; k++) { a += W8[k][1]; if (r < a) return W8[k][0]; } return 'a'; }
    rows.forEach(function (r) {
      $$('i', r).forEach(function (x) { x.remove(); });
      for (var k = 0; k < cols; k++) { var c = D.createElement('i'); c.setAttribute('data-s', pickS()); r.appendChild(c); }
    });
    function stat() {
      var cnt = { a: 0, m: 0, w: 0, i: 0 };
      rows.forEach(function (r) { var last = r.lastElementChild; if (last) cnt[last.getAttribute('data-s')]++; });
      var all = { a: 0, m: 0, w: 0, i: 0 };
      rows.forEach(function (r) { $$('i', r).forEach(function (x) { all[x.getAttribute('data-s')]++; }); });
      if (kpi) kpi.textContent = cnt.a + ' / ' + rows.length;
      if (bar) $$('i[data-s]', bar).forEach(function (x) { x.style.setProperty('--v', all[x.getAttribute('data-s')] || .001); });
    }
    function tick() {
      rows.forEach(function (r) {
        var f = r.querySelector('i'); if (f) f.remove();
        var c = D.createElement('i'); c.setAttribute('data-s', pickS()); r.appendChild(c);
      });
      stat();
    }
    stat();
    addWidget(sim, function (active) {
      if (active && !reduced()) { if (!timer) timer = setInterval(tick, 420); }
      else { clearInterval(timer); timer = 0; }
    });
  });

  // 숫자 카운트업 — data-count 를 단 숫자가 장에 들어올 때 0 에서 제 값까지 오른다(1.1초).
  // 값은 마크업에 적힌 그대로다 — JS 가 없으면 처음부터 제 값이다.
  // data-count="roll" 이면 자리마다 숫자가 굴러 멈춘다. 소수 자리는 data-dec 로 정한다.
  function firstNum(el) {
    var w = D.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) { if (/\d/.test(n.nodeValue)) return n; }
    return null;
  }
  function countUp(el) {
    if (reduced() || el.__blCounting) return;
    var tn = firstNum(el);
    if (!tn) return;
    var txt = el.__blText != null ? el.__blText : tn.nodeValue;
    el.__blText = txt;
    var m = txt.match(/[-+]?\d[\d,]*(\.\d+)?/);
    if (!m) return;
    if (el.getAttribute('data-count') === 'roll') { roll(el, tn, txt, m); return; }
    var target = parseFloat(m[0].replace(/,/g, ''));
    var dec = el.hasAttribute('data-dec') ? +el.getAttribute('data-dec') : (m[1] ? m[1].length - 1 : 0);
    var comma = m[0].indexOf(',') >= 0, sign = m[0].charAt(0) === '+' ? '+' : '';
    var pre = txt.slice(0, m.index), post = txt.slice(m.index + m[0].length), t0 = 0;
    function fmt(v) {
      var s = Math.abs(v).toFixed(dec), parts = s.split('.');
      if (comma) parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      return pre + (v < 0 ? '-' : sign) + parts.join('.') + post;
    }
    el.__blCounting = true;
    function step(now) {
      if (!t0) t0 = now;
      var p = Math.min(1, (now - t0) / 1100), e = 1 - Math.pow(1 - p, 3);
      tn.nodeValue = p < 1 ? fmt(target * e) : txt;
      if (p < 1) requestAnimationFrame(step); else el.__blCounting = false;
    }
    requestAnimationFrame(step);
  }
  function roll(el, tn, txt, m) {
    if (el.__blRolled) { $$('.bl-roll', el).forEach(function (r) { r.classList.remove('go'); void r.offsetWidth; r.classList.add('go'); }); return; }
    el.__blRolled = true;
    var frag = D.createDocumentFragment(), pre = txt.slice(0, m.index), num = m[0], post = txt.slice(m.index + num.length);
    if (pre) frag.appendChild(D.createTextNode(pre));
    var k = 0;
    num.split('').forEach(function (ch) {
      if (!/\d/.test(ch)) { frag.appendChild(D.createTextNode(ch)); return; }
      var r = mk('span', 'bl-roll'), col = mk('span');
      r.setAttribute('aria-hidden', 'true');
      col.style.setProperty('--n', ch); col.style.setProperty('--k', k++);
      for (var d = 0; d <= 9; d++) col.appendChild(mk('b', null, String(d)));
      r.appendChild(col); frag.appendChild(r);
    });
    if (post) frag.appendChild(D.createTextNode(post));
    el.setAttribute('aria-label', txt.trim());
    tn.parentNode.replaceChild(frag, tn);
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      $$('.bl-roll', el).forEach(function (r) { r.classList.add('go'); });
    }); });
  }

  // ── 클릭 ──────────────────────────────────────────────────────────────
  // 겹창을 여는 단추는 문서 전체에서 한 처리기로 받는다(장마다 다는 대신). 캡처 단계에서
  // 먼저 잡아, 장 안의 다른 처리기가 같은 클릭으로 엉뚱한 일을 하지 않게 한다.
  D.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var chip = t.closest('.bl-ev[data-ev]');
    if (chip && !t.closest('#bl-peek')) { e.preventDefault(); e.stopPropagation(); openEvidence(chip, e.detail === 0); return; }
    var pk = t.closest('[data-peek]');
    if (pk && !t.closest('#bl-peek')) { e.preventDefault(); e.stopPropagation(); openPeek(pk); return; }
    var dc = t.closest('[data-doc]');
    if (dc) { e.preventDefault(); e.stopPropagation(); openDoc(dc); return; }
    var vd = t.closest('[data-video]');
    if (vd) { e.preventDefault(); e.stopPropagation(); openVideo(vd); return; }
    var rp = t.closest('.bl-replay');
    if (rp) {
      var s = slideOf(rp);
      if (s) {
        e.preventDefault();
        s.classList.add('bl-rs'); void s.offsetWidth;
        requestAnimationFrame(function () { s.classList.remove('bl-rs'); $$('[data-count]', s).forEach(countUp); });
      }
      return;
    }
    var zoom = t.closest('.bl-fig > img, .bl-fig > svg, .bl-shot-img img, [data-zoom]');
    var open = t.closest('.bl-shot-open');
    if (open) { var im = open.closest('.bl-shot-img'); zoom = im && im.querySelector('img, svg'); }
    if (zoom && deck.contains(zoom)) { e.preventDefault(); e.stopPropagation(); openLightbox(zoom); }
  }, true);

  // 발표 중 화면 클릭 = 다음. 단추 · 칩 · 고르기 카드 같은 것은 빼고
  deck.addEventListener('click', function (e) {
    if (!isPresent() || topModal() || tool) return;
    if (blankMode) { setBlank(null); return; }
    if (e.target.closest && e.target.closest(INTERACTIVE)) {
      // 단추를 누른 뒤에도 Space 가 「다음」이 되게 초점을 덱으로 돌린다
      setTimeout(function () { try { deck.focus({ preventScroll: true }); } catch (er) { /* 무시 */ } }, 0);
      return;
    }
    if (W.getSelection && String(W.getSelection())) return;
    if (peekSeqClick()) return;
    next();
  });

  // ── 단축키 표 ─────────────────────────────────────────────────────────
  // 파워포인트 슬라이드 쇼 단축키를 그대로 쓴다. 처음 보는 사람도 손에 익은 키로 발표하게.
  // 파워포인트에 없는 우리 기능(메모 · 펼침 · 가로)은 파워포인트가 쓰지 않는 글자에 둔다.
  // 표가 한 곳이다 — 도움말 · 조작판 글자 · 키 처리가 전부 여기서 읽는다. 덱마다 바꾸려면
  //   <script type="application/json" id="bl-keys">{"pen": ["p", "ctrl+p"], "notes": ["m"]}</script>
  // 키 이름: 글자 · f1~f12 · arrowright 등 · space · enter · backspace · pageup · home · . , ?
  // 조합은 ctrl+ · alt+ · shift+ (맥의 ⌘ 는 ctrl 로 본다)
  var KEYMAP = {
    next:        { keys: ['arrowright', 'arrowdown', 'pagedown', 'space', 'enter', 'n'], hud: 'arrowright', label: '다음 (단계 먼저)' },
    prev:        { keys: ['arrowleft', 'arrowup', 'pageup', 'backspace'], hud: 'arrowleft', label: '이전' },
    first:       { keys: ['home'], label: '첫 장' },
    last:        { keys: ['end'], label: '마지막 장' },
    fromStart:   { keys: ['f5'], label: '처음부터 발표' },
    fromHere:    { keys: ['shift+f5', 'f'], hud: 'shift+f5', label: '이 장부터 발표 · 다시 누르면 끝' },
    presenter:   { keys: ['alt+f5', 's'], hud: 'alt+f5', label: '발표자 보기 — 대본 · 타이머 · 다음 장' },
    black:       { keys: ['b', '.'], label: '검은 화면 · 아무 키나 누르면 돌아옴' },
    white:       { keys: ['w', ','], label: '흰 화면 · 아무 키나 누르면 돌아옴' },
    pen:         { keys: ['p', 'ctrl+p'], hud: 'p', label: '펜 — 화면에 쓰기 · 다시 누르면 끔' },
    highlighter: { keys: ['ctrl+i'], label: '형광펜' },
    eraser:      { keys: ['ctrl+e'], label: '지우개 — 닿은 획 지우기' },
    erase:       { keys: ['e'], label: '이 장 필기 모두 지우기' },
    ink:         { keys: ['ctrl+m'], label: '필기 보이기 · 숨기기' },
    arrow:       { keys: ['ctrl+a'], label: '펜 끄기 (레이저로 돌아감)' },
    laser:       { keys: ['ctrl+l', 'l'], hud: 'l', label: '레이저 켜기 · 끄기' },
    notes:       { keys: ['m'], label: '메모 — 이 장의 발표자 노트' },
    expand:      { keys: ['x'], label: '펼침 — 단계 전부 보기 · 끄면 한 단계씩' },
    horiz:       { keys: ['v'], label: '가로 보기' },
    help:        { keys: ['f1', '?'], hud: '?', label: '이 도움말' }
  };
  (function () {
    var o = null;
    try {
      var el = D.getElementById('bl-keys');
      if (el) o = JSON.parse(el.textContent);
      else if (W.BL_KEYS) o = W.BL_KEYS;
    } catch (er) { if (W.console) console.warn('bl-keys JSON 을 읽지 못했다', er); }
    if (!o) return;
    Object.keys(o).forEach(function (a) {
      if (!KEYMAP[a]) { if (W.console) console.warn('bl-keys — 모르는 동작:', a); return; }
      var ks = [].concat(o[a]).map(function (x) { return String(x).toLowerCase().replace(/\s+/g, ''); });
      KEYMAP[a].keys = ks;
      if (ks.indexOf(KEYMAP[a].hud) < 0) KEYMAP[a].hud = ks[0];
    });
  })();
  var KEYIDX = {};
  Object.keys(KEYMAP).forEach(function (a) { KEYMAP[a].keys.forEach(function (c) { KEYIDX[c] = a; }); });

  // 눌린 키를 표의 이름으로. 글자는 물리 위치(code)로 본다 — 한글 입력 중에도 P · B · W 가 듣는다.
  // 기호(? . ,)는 Shift 를 따지지 않는다 — ? 는 이미 Shift 를 누른 글자다.
  function comboOf(e) {
    var k = e.key || '', c = e.code || '', main;
    if (/^Key[A-Z]$/.test(c)) main = c.slice(3).toLowerCase();
    else if (k === ' ') main = 'space';
    else main = k.toLowerCase();
    var named = main.length > 1 || /^[a-z]$/.test(main);
    return (e.ctrlKey || e.metaKey ? 'ctrl+' : '') + (e.altKey ? 'alt+' : '') +
           (e.shiftKey && named ? 'shift+' : '') + main;
  }
  var PRETTY = { arrowright: '→', arrowleft: '←', arrowup: '↑', arrowdown: '↓', pagedown: 'PgDn', pageup: 'PgUp',
                 space: 'Space', enter: 'Enter', backspace: 'Backspace', home: 'Home', end: 'End', escape: 'Esc' };
  function pretty(c) {
    return c.split('+').map(function (p) {
      if (p === 'ctrl') return 'Ctrl'; if (p === 'alt') return 'Alt'; if (p === 'shift') return 'Shift';
      return PRETTY[p] || p.toUpperCase();
    }).join('+');
  }
  function helpRows() {
    var rows = Object.keys(KEYMAP).map(function (a) {
      return [KEYMAP[a].keys.map(pretty).join(' · '), KEYMAP[a].label];
    });
    rows.splice(4, 0, ['숫자 Enter', '그 쪽으로 이동 · 0 은 표지'], ['a 숫자 Enter', '부록 쪽으로 이동']);
    rows.push(['Esc', '닫기 · 펜 끄기 · 발표 끝']);
    return rows;
  }

  // ── 검은 화면 · 흰 화면 ───────────────────────────────────────────────
  var blankEl = null, blankMode = null;
  function setBlank(m) {
    blankMode = m && blankMode !== m ? m : null;
    if (!blankEl && !blankMode) return;
    if (!blankEl) {
      blankEl = mk('div'); blankEl.id = 'bl-blank'; blankEl.setAttribute('aria-hidden', 'true');
      blankEl.addEventListener('click', function () { setBlank(null); });
      B.appendChild(blankEl);
    }
    blankEl.className = blankMode ? 'is-' + blankMode : '';
    blankEl.hidden = !blankMode;
    emit('deck:blank', { mode: blankMode });
  }

  // ── 필기 — 펜 · 형광펜 · 지우개 ─────────────────────────────────────
  // 장마다 투명 캔버스를 한 장 깐다. 획은 장 크기에 대한 비율로 적어 두어 창 크기가 바뀌거나
  // 가로 보기로 바꿔도 같은 자리에 다시 그린다. 필기는 이 창에만 있다 — 파일에는 남지 않는다.
  var tool = null, inkHidden = false, penColor = '--br-alert-text', INK = {};
  var PEN_COLORS = [['--br-alert-text', '빨강'], ['--br-cobalt', '파랑'], ['--br-text', '검정']];
  function tok(name) { return getComputedStyle(R).getPropertyValue(name).trim() || 'crimson'; }
  function inkOf(s) {
    var c = s.querySelector(':scope > canvas.bl-ink');
    if (c) return c;
    c = mk('canvas', 'bl-ink'); c.setAttribute('aria-hidden', 'true');
    s.appendChild(c);
    bindInk(c, s);
    sizeInk(c, s);
    return c;
  }
  function sizeInk(c, s) {
    var r = s.getBoundingClientRect(), d = W.devicePixelRatio || 1;
    var w = Math.max(1, Math.round(r.width * d)), h = Math.max(1, Math.round(r.height * d));
    if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
    drawInk(slides.indexOf(s));
  }
  function drawInk(k) {
    var s = slides[k], c = s && s.querySelector(':scope > canvas.bl-ink');
    if (!c) return;
    var g = c.getContext('2d');
    g.clearRect(0, 0, c.width, c.height);
    (INK[k] || []).forEach(function (st) {
      g.save();
      g.globalAlpha = st.hl ? 0.4 : 1;
      if (st.hl) g.globalCompositeOperation = 'multiply';
      g.strokeStyle = st.color; g.lineWidth = st.w * c.width;
      g.lineCap = 'round'; g.lineJoin = 'round';
      g.beginPath();
      st.pts.forEach(function (p, j) {
        var x = p[0] * c.width, y = p[1] * c.height;
        if (j) g.lineTo(x, y); else { g.moveTo(x, y); if (st.pts.length === 1) g.lineTo(x + 0.01, y); }
      });
      g.stroke();
      g.restore();
    });
  }
  function bindInk(c, s) {
    var cur = null;
    function pt(e) { var r = c.getBoundingClientRect(); return [(e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height]; }
    function eraseAt(k, p) {
      var r = c.getBoundingClientRect(), tx = 12 / r.width, ty = 12 / r.height, list = INK[k] || [];
      var left = list.filter(function (st) {
        return !st.pts.some(function (q) { return Math.abs(q[0] - p[0]) < tx && Math.abs(q[1] - p[1]) < ty; });
      });
      if (left.length !== list.length) { INK[k] = left; drawInk(k); }
    }
    c.addEventListener('pointerdown', function (e) {
      if (!tool) return;
      e.preventDefault(); e.stopPropagation();
      try { c.setPointerCapture(e.pointerId); } catch (er) { /* 무시 */ }
      var k = slides.indexOf(s);
      if (tool === 'eraser') { cur = { k: k, erase: true }; eraseAt(k, pt(e)); return; }
      var hl = tool === 'hl';
      cur = { k: k, st: { hl: hl, color: tok(hl ? '--br-warn-line' : penColor), w: hl ? 0.016 : 0.0028, pts: [pt(e)] } };
      (INK[k] = INK[k] || []).push(cur.st);
      drawInk(k);
    });
    c.addEventListener('pointermove', function (e) {
      if (!cur) return;
      if (cur.erase) { eraseAt(cur.k, pt(e)); return; }
      cur.st.pts.push(pt(e)); drawInk(cur.k);
    });
    function end() { cur = null; }
    c.addEventListener('pointerup', end);
    c.addEventListener('pointercancel', end);
    c.addEventListener('click', function (e) { if (tool) e.stopPropagation(); });
  }
  function setTool(t) {
    t = t || null;
    if (t === tool) t = null;                       // 같은 키를 다시 누르면 끈다
    tool = t;
    B.classList.toggle('inking', !!tool);
    B.setAttribute('data-ink', tool || '');
    if (tool) {
      slides.forEach(inkOf);
      if (inkHidden) setInkHidden(false);
      if (laserOn) setLaser(false);
    } else if (isPresent() && !laserOn) {
      setLaser(true);                                // 발표 중이면 레이저로 돌아간다
    }
    inkBar();
    paintToggles();
    emit('deck:ink', { tool: tool });
  }
  function setInkHidden(on) {
    inkHidden = !!on;
    B.classList.toggle('ink-hidden', inkHidden);
    if (inkHidden && tool) setTool(null);
    toast(inkHidden ? '필기 숨김 · ' + pretty(KEYMAP.ink.keys[0]) + ' 로 다시 보기' : '필기 보임');
  }
  function eraseSlide() {
    if (!(INK[i] && INK[i].length)) return;
    INK[i] = []; drawInk(i);
    toast('이 장 필기를 지웠다');
  }
  W.addEventListener('resize', function () {
    slides.forEach(function (s) { var c = s.querySelector(':scope > canvas.bl-ink'); if (c) sizeInk(c, s); });
  });
  D.addEventListener('deck:sync', function () {
    if (!tool) return;
    var s = slides[i], c = s && s.querySelector(':scope > canvas.bl-ink');
    if (c) sizeInk(c, s);
  });

  // 필기 도구판 — 펜을 켜면 화면 위에 뜬다. 도구 · 색 · 지우기 · 끄기
  var inkBarEl = null;
  function inkBar() {
    if (!tool) { if (inkBarEl) inkBarEl.hidden = true; return; }
    if (!inkBarEl) {
      inkBarEl = mk('div'); inkBarEl.id = 'bl-inkbar'; inkBarEl.setAttribute('role', 'toolbar');
      inkBarEl.setAttribute('aria-label', '필기 도구');
      function btn(label, title, fn, data) {
        var b = mk('button', null, label); b.type = 'button'; b.title = title;
        if (data) Object.keys(data).forEach(function (k2) { b.setAttribute(k2, data[k2]); });
        b.addEventListener('click', function (e) { e.stopPropagation(); fn(); });
        inkBarEl.appendChild(b);
        return b;
      }
      btn('펜', '펜 · ' + KEYMAP.pen.keys.map(pretty).join(' / '), function () { if (tool !== 'pen') setTool('pen'); }, { 'data-tool': 'pen' });
      btn('형광펜', '형광펜 · ' + KEYMAP.highlighter.keys.map(pretty).join(' / '), function () { if (tool !== 'hl') setTool('hl'); }, { 'data-tool': 'hl' });
      btn('지우개', '지우개 · ' + KEYMAP.eraser.keys.map(pretty).join(' / '), function () { if (tool !== 'eraser') setTool('eraser'); }, { 'data-tool': 'eraser' });
      PEN_COLORS.forEach(function (pc) {
        var b = btn('', pc[1], function () { penColor = pc[0]; if (tool !== 'pen') setTool('pen'); else inkBar(); },
                    { 'data-color': pc[0], 'aria-label': pc[1] + ' 펜' });
        b.className = 'bl-ink-sw'; b.style.setProperty('--sw', 'var(' + pc[0] + ')');
      });
      btn('모두 지우기', '이 장 필기 모두 지우기 · ' + pretty(KEYMAP.erase.keys[0]), eraseSlide);
      btn('끄기', '펜 끄기 · Esc', function () { setTool(null); });
      B.appendChild(inkBarEl);
    }
    inkBarEl.hidden = false;
    $$('[data-tool]', inkBarEl).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-tool') === tool ? 'true' : 'false'); });
    $$('[data-color]', inkBarEl).forEach(function (b) { b.setAttribute('aria-pressed', tool === 'pen' && b.getAttribute('data-color') === penColor ? 'true' : 'false'); });
  }

  // 표의 동작 이름 → 할 일
  var DO = {
    next: next, prev: prev,
    first: function () { goTo(0); },
    last: function () { goTo(slides.length - 1); },
    fromStart: function () { goTo(0); if (!isPresent()) enterPresent(null); },
    fromHere: togglePresent,
    presenter: openPresenter,
    black: function () { setBlank('black'); },
    white: function () { setBlank('white'); },
    pen: function () { setTool('pen'); },
    highlighter: function () { setTool('hl'); },
    eraser: function () { setTool('eraser'); },
    erase: eraseSlide,
    ink: function () { setInkHidden(!inkHidden); },
    arrow: function () { if (tool) setTool(null); },
    laser: function () { if (tool) setTool(null); setLaser(!laserOn); },
    notes: toggleNotes,
    expand: toggleExpand,
    horiz: toggleHoriz,
    help: toggleHelp
  };

  // ── 키 ────────────────────────────────────────────────────────────────
  var jbuf = '', japx = false, jtimer = 0, jel = null;
  function jumpEl() {
    jel = jel || D.getElementById('bl-jump');
    if (!jel) { jel = mk('div'); jel.id = 'bl-jump'; jel.hidden = true; B.appendChild(jel); }
    return jel;
  }
  function jumpShow(bad) {
    var el = jumpEl();
    clearTimeout(jtimer);
    if (!jbuf && !japx && !bad) { el.hidden = true; el.classList.remove('is-bad'); return; }
    el.hidden = false;
    el.classList.toggle('is-bad', !!bad);
    el.textContent = '';
    if (japx) el.appendChild(mk('small', null, '부록'));
    el.appendChild(D.createTextNode(bad ? '없음' : (jbuf || '_')));
    jtimer = setTimeout(function () { jbuf = ''; japx = false; jumpShow(); }, 3000);
  }
  function jumpGo() {
    var n = parseInt(jbuf, 10), t = null;
    if (!isNaN(n)) {
      if (japx) t = apxList[n - 1];
      else if (n === 0) t = coverSlide;
      else t = bodyList[n - 1];
    }
    jbuf = ''; japx = false;
    if (!t) { jumpShow(true); return; }
    jumpShow();
    goTo(slides.indexOf(t));
  }
  function isField(t) { return !!(t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))); }
  function isActivator(t) {
    return !!(t && t.closest && t !== deck && t.closest('button, a[href], summary, [role="button"], [role="tab"], [data-pick]'));
  }

  W.addEventListener('keydown', function (e) {
    if (e.key === 'F11') { setTimeout(fsCheck, 450); setTimeout(fsCheck, 1100); return; }
    var m = topModal();
    if (m) {
      if (isField(e.target) && e.key !== 'Escape') return;
      var r = m.key(e);
      if (r !== false && e.key !== 'Tab') { e.preventDefault(); e.stopPropagation(); }
      return;
    }
    if (isField(e.target)) return;
    if (/^(Control|Shift|Alt|Meta|Process|Unidentified)$/.test(e.key)) return;
    var k = e.key, code = e.code, plain = !(e.ctrlKey || e.metaKey || e.altKey);

    // 검은·흰 화면은 아무 키나 누르면 돌아온다 — 파워포인트와 같다
    if (blankMode) { setBlank(null); e.preventDefault(); return; }

    if (plain && /^[0-9]$/.test(k)) { if (jbuf.length < 3) jbuf += k; jumpShow(); e.preventDefault(); return; }
    if (jbuf || japx) {
      if (k === 'Enter') { if (jbuf) jumpGo(); e.preventDefault(); return; }
      if (k === 'Backspace') { jbuf = jbuf.slice(0, -1); jumpShow(); e.preventDefault(); return; }
      if (k === 'Escape') { jbuf = ''; japx = false; jumpShow(); e.preventDefault(); return; }
    }
    if (plain && !jbuf && (code === 'KeyA' || k === 'a' || k === 'A' || k === 'ㅁ')) {
      japx = !japx; jumpShow(); e.preventDefault(); return;
    }
    // Esc 는 하나씩 닫는다 — 도움말 → 펜 → 발표
    if (k === 'Escape') {
      if (helpOn()) toggleHelp();
      else if (tool) setTool(null);
      else if (isPresent()) exitPresent();
      else return;
      e.preventDefault(); return;
    }
    if ((k === ' ' || k === 'Enter') && plain && isActivator(e.target)) return;   // 초점 받은 단추는 제 일을 한다
    var act = KEYIDX[comboOf(e)];
    if (!act) return;
    if (helpOn() && act !== 'help') toggleHelp();
    e.preventDefault();
    DO[act]();
  }, true);

  // ── 조작판 ────────────────────────────────────────────────────────────
  // data-act 로 묶는다. id 로 묶으면 덱마다 이름을 새로 지어야 하고, 한 글자만 달라도
  // 단추가 조용히 죽는다 — 눌러 보기 전에는 아무도 모른다.
  function paintToggles() {
    function set(act, on) {
      $$('[data-act="' + act + '"]').forEach(function (b) { b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    }
    set('expand', !deck.classList.contains('bl-deck--collapse'));
    set('horiz', deck.classList.contains('bl-deck--horiz'));
    set('notes', notesOn());
    set('laser', laserOn);
    set('present', isPresent());
    set('script', presenterOpen());
    set('pen', tool === 'pen' || tool === 'hl');
  }
  var ACTS = {
    prev: prev, next: next, present: togglePresent, script: openPresenter, presenter: openPresenter,
    expand: toggleExpand, horiz: toggleHoriz, notes: toggleNotes, help: toggleHelp,
    laser: function () { setLaser(!laserOn); },
    pen: function () { setTool(tool === 'pen' ? null : 'pen'); }
  };
  // 단추에 적힌 단축키도 표에서 가져온다 — 표를 바꾸면 단추 글자도 따라 바뀐다
  var ACT_KEY = { prev: 'prev', next: 'next', present: 'fromHere', script: 'presenter', presenter: 'presenter',
                  expand: 'expand', horiz: 'horiz', notes: 'notes', help: 'help', laser: 'laser', pen: 'pen' };
  $$('[data-act]').forEach(function (b) {
    var a = b.getAttribute('data-act'), fn = ACTS[a];
    if (fn) b.onclick = fn;
    var kb = b.querySelector('kbd'), km = KEYMAP[ACT_KEY[a]];
    if (kb && km) kb.textContent = pretty(km.hud || km.keys[0]);
  });
  // 예전 덱의 id 방식도 받아 준다
  var pb = D.getElementById('bl-present');
  if (pb) pb.onclick = togglePresent;
  var sb = D.getElementById('bl-script');
  if (sb) sb.onclick = openPresenter;

  // ── 시작 ──────────────────────────────────────────────────────────────
  // 주소 끝 #장id 로 열면 그 장에서 시작한다. 장을 옮겨도 주소는 바꾸지 않는다 —
  // 아티팩트 · 메일 미리보기처럼 주소를 못 바꾸는 곳에서도 같게 움직이게.
  var startAt = 0;
  try {
    var h = decodeURIComponent((location.hash || '').slice(1));
    if (h) { var t = D.getElementById(h); var k = slides.indexOf(t); if (k >= 0) startAt = k; }
  } catch (e) { /* 무시 */ }
  if (startAt) goTo(startAt); else { markIn(slides[0]); sync(); }
  try { if (!D.activeElement || D.activeElement === B) deck.focus({ preventScroll: true }); } catch (e) { /* 무시 */ }

  // 다른 스크립트가 덱을 움직일 수 있게 최소한만 내놓는다
  W.blDeck = { go: function (n) { goTo(n); }, next: next, prev: prev, present: togglePresent,
               laser: function (on) { setLaser(on == null ? !laserOn : on); }, presenter: openPresenter,
               tool: function (t) { setTool(t || null); }, keys: KEYMAP, ink: INK,
               get index() { return i; }, get step() { return stepAt[i]; }, slides: slides };
})();
