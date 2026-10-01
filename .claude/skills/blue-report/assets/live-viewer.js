// 라이브 덱 뷰어 — 축 전환(검토↔발표), 단계 전개, 쪽번호, 노트·대본,
// 펼침·가로·메모·도움말, 출처 칩의 근거 패널.
//
// 슬라이드 계통의 deck-viewer.js 와 역할은 같지만 하는 일이 훨씬 적다.
// 배율과 넘김을 CSS 가 이미 한다 — 루트 글자 크기가 clamp 로 따라가고, 넘김은
// 브라우저의 scroll-snap 이 한다. 그래서 여기서는 JS 로만 되는 것만 한다.
//
// 이 계통은 **JS 없이 열어도 전부 읽힌다.** 세로로 스크롤하면 그만이다.
// 단계 전개를 기본으로 접지 않는 이유도 같다.

(function () {
  var deck = document.getElementById('deck');
  if (!deck) return;
  var slides = Array.prototype.slice.call(deck.querySelectorAll('.bl-sl'));
  var deckTitle = deck.dataset.deckTitle || '';
  var i = 0, step = 0;

  // ── 쪽번호 ────────────────────────────────────────────────────────────
  // 부록은 본문과 다른 체계로 센다. 같은 자리에 다른 체계가 찍히는 것이
  // 부록으로 넘어왔다는 신호다 — 덱 계통과 같은 규약이다.
  var apxTotal = slides.filter(function (s) { return s.hasAttribute('data-apx'); }).length;
  var bodyN = 0, apxN = 0;
  slides.forEach(function (s) {
    var isApx = s.hasAttribute('data-apx');
    if (isApx) apxN++; else bodyN++;
    var pg = s.querySelector('.bl-pg');
    if (!pg) return;
    pg.textContent = isApx ? '부록 ' + apxN + ' / ' + apxTotal
                           : String(bodyN).padStart(2, '0') + ' / '
                             + String(slides.length - apxTotal).padStart(2, '0');
    var nm = s.querySelector('.bl-rf-name');
    if (nm && !nm.textContent) nm.textContent = deckTitle;
  });

  // ── 단계 전개 ─────────────────────────────────────────────────────────
  function frags(s) { return Array.prototype.slice.call(s.querySelectorAll('[data-f]')); }
  function maxStep(s) {
    return frags(s).reduce(function (m, el) {
      return Math.max(m, parseInt(el.getAttribute('data-f'), 10) || 0);
    }, 0);
  }
  // 단계를 접어 두는가. 발표 모드에서는 언제나 접는다. 검토 중에도 펼침(E)을
  // 끄면 접는다 — 발표 전에 클릭 순서를 미리 밟아 보는 용도다.
  function staged() {
    return deck.classList.contains('bl-deck--present') ||
           deck.classList.contains('bl-deck--collapse');
  }

  function paint() {
    paintProg();
    deck.classList.toggle('bl-deck--staged', staged());
    slides.forEach(function (s, k) {
      var open = !staged() || k !== i;
      frags(s).forEach(function (el) {
        var n = parseInt(el.getAttribute('data-f'), 10) || 0;
        el.classList.toggle('is-shown', open || n <= step);
      });
    });
    pushScript();
    paintNotes();
    paintToggles();
  }

  function stepFwd() {
    if (!staged() || step >= maxStep(slides[i])) return false;
    step++; paint(); return true;
  }
  function stepBack() {
    if (!staged() || step <= 0) return false;
    step--; paint(); return true;
  }

  // ── 현재 장 추적 ──────────────────────────────────────────────────────
  // 스크롤은 브라우저가 한다. 어디에 와 있는지만 관찰로 알아낸다 —
  // scroll 이벤트로 좌표를 재면 스냅 도중 값이 튄다.
  if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var k = slides.indexOf(e.target);
        if (k < 0 || k === i) return;
        i = k; step = 0; paint();
      });
    }, { root: deck, threshold: .6 });
    slides.forEach(function (s) { io.observe(s); });
  }

  function goTo(k) {
    i = Math.max(0, Math.min(slides.length - 1, k));
    step = 0;
    slides[i].scrollIntoView({ block: 'start', inline: 'start' });
    paint();
  }

  // ── 발표 모드 ─────────────────────────────────────────────────────────
  // 축을 세로에서 가로로 바꾸고 전체화면으로 들어간다. 클래스 하나가
  // scroll-snap-type 과 flex-direction 을 함께 바꾼다.
  function inFull() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement);
  }
  function setPresent(on) {
    deck.classList.toggle('bl-deck--present', on);
    document.body.classList.toggle('present', on);
    step = 0;
    paint();
    // 축이 바뀌면 스크롤 좌표가 무의미해진다. 보던 장으로 다시 앉힌다.
    requestAnimationFrame(function () {
      slides[i].scrollIntoView({ block: 'start', inline: 'start' });
    });
  }
  function enterPresent() {
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen;
    setPresent(true);
    if (req) { var r = req.call(el); if (r && r.catch) r.catch(function () {}); }
  }
  function exitPresent() {
    if (inFull()) {
      var ex = document.exitFullscreen || document.webkitExitFullscreen;
      if (ex) ex.call(document);
    }
    setPresent(false);
  }
  function togglePresent() {
    if (deck.classList.contains('bl-deck--present')) exitPresent(); else enterPresent();
  }
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
    document.addEventListener(ev, function () {
      if (!inFull() && deck.classList.contains('bl-deck--present')) setPresent(false);
    });
  });

  // ── 대본 창 ───────────────────────────────────────────────────────────
  var scriptWin = null;
  function noteOf(k) {
    var s = slides[(k + slides.length) % slides.length];
    return s.dataset.notes || '';
  }
  function openScript() {
    if (scriptWin && !scriptWin.closed) { scriptWin.focus(); return; }
    scriptWin = window.open('', 'bl-script', 'width=560,height=760');
    if (!scriptWin) { alert('대본 창이 브라우저에 막혔다. 팝업을 허용한 뒤 다시 누른다.'); return; }
    scriptWin.document.open();
    scriptWin.document.write(
      '<!doctype html><meta charset="utf-8"><title>대본</title><style>' +
      "body{margin:0;padding:22px 24px;background:#0c121e;color:#dbe3ec;font:400 16px/1.7 system-ui,'Malgun Gothic',sans-serif}" +
      'h1{margin:0 0 4px;font:600 13px/1.3 system-ui;letter-spacing:.14em;text-transform:uppercase;color:#8fa4bd}' +
      '#t{font:600 28px/1 ui-monospace,Menlo,monospace;color:#fff;margin:0 0 18px}' +
      '#cur{white-space:pre-wrap;border-left:3px solid #2f4a9c;padding-left:14px;margin-bottom:22px}' +
      '#nxt{white-space:pre-wrap;color:#8fa4bd;border-left:3px solid #2b3852;padding-left:14px}' +
      'h2{margin:0 0 6px;font:600 11px/1 system-ui;letter-spacing:.14em;text-transform:uppercase;color:#8fa4bd}' +
      '</style><h1 id="pg"></h1><p id="t">00:00</p>' +
      '<h2>지금</h2><div id="cur"></div><h2>다음</h2><div id="nxt"></div>');
    scriptWin.document.close();
    var t0 = Date.now();
    scriptWin.setInterval(function () {
      var el = scriptWin.document.getElementById('t');
      if (!el) return;
      var s = Math.floor((Date.now() - t0) / 1000);
      el.textContent = String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
    }, 1000);
    pushScript();
  }
  function pushScript() {
    if (!scriptWin || scriptWin.closed) return;
    var d = scriptWin.document, pg = d.getElementById('pg');
    if (!pg) return;
    var ms = maxStep(slides[i]);
    pg.textContent = (i + 1) + ' / ' + slides.length + (ms ? '   단계 ' + step + ' / ' + ms : '');
    d.getElementById('cur').textContent = noteOf(i) || '(노트 없음)';
    d.getElementById('nxt').textContent = noteOf(i + 1) || '(노트 없음)';
  }
  window.addEventListener('beforeunload', function () {
    if (scriptWin && !scriptWin.closed) scriptWin.close();
  });

  // ── 펼침 · 가로 ───────────────────────────────────────────────────────
  // 사내 발표 덱의 조작을 그대로 따른다. 펼침(E)은 단계를 모두 보인
  // 채로 검토하는 기본 상태이고, 끄면 발표처럼 한 단계씩 나온다. 가로(H)는
  // 전체화면 없이 축만 옆으로 돌린다.
  function setCollapse(on) {
    deck.classList.toggle('bl-deck--collapse', on);
    step = on ? 0 : step;
    paint();
  }
  function toggleExpand() { setCollapse(!deck.classList.contains('bl-deck--collapse')); }
  function toggleHoriz() {
    deck.classList.toggle('bl-deck--horiz');
    requestAnimationFrame(function () {
      slides[i].scrollIntoView({ block: 'start', inline: 'start' });
    });
    paintToggles();
  }

  // ── 메모 ──────────────────────────────────────────────────────────────
  // 지금 장의 발표자 노트를 지면 아래에 띄운다. 대본 창(S)은 팝업이라 막히는
  // 환경이 있다 — 메모는 같은 창 안이라 언제나 열린다.
  var notesEl = null;
  function notesOn() { return !!(notesEl && !notesEl.hidden); }
  function toggleNotes() {
    if (!notesEl) {
      notesEl = document.createElement('aside');
      notesEl.id = 'bl-notes';
      notesEl.setAttribute('aria-live', 'polite');
      notesEl.hidden = true;
      document.body.appendChild(notesEl);
    }
    notesEl.hidden = !notesEl.hidden;
    paintNotes(); paintToggles();
  }
  function paintNotes() {
    if (!notesOn()) return;
    notesEl.textContent = '';
    var h = document.createElement('b');
    h.textContent = '메모 · ' + (i + 1) + ' / ' + slides.length;
    notesEl.appendChild(h);
    notesEl.appendChild(document.createTextNode(noteOf(i) || '(노트 없음)'));
  }

  // ── 도움말 ────────────────────────────────────────────────────────────
  var KEYS = [
    ['← →', '이전 · 다음 (단계 포함)'], ['숫자 Enter', '그 장으로 이동'],
    ['Home End', '처음 · 끝'], ['E', '펼침 — 단계를 모두 보이기 · 끄면 한 단계씩'],
    ['H', '가로 보기'], ['N', '메모 — 이 장의 발표자 노트'], ['F', '발표 — 전체화면'],
    ['S', '대본 창'], ['?', '이 도움말'], ['Esc', '닫기 · 발표 끝내기']
  ];
  var helpEl = null;
  function helpOn() { return !!(helpEl && !helpEl.hidden); }
  function toggleHelp() {
    if (!helpEl) {
      helpEl = document.createElement('div');
      helpEl.id = 'bl-help';
      helpEl.setAttribute('role', 'dialog');
      helpEl.setAttribute('aria-label', '단축키');
      var dl = document.createElement('dl');
      KEYS.forEach(function (k) {
        var dt = document.createElement('dt'), dd = document.createElement('dd');
        dt.textContent = k[0]; dd.textContent = k[1];
        dl.appendChild(dt); dl.appendChild(dd);
      });
      helpEl.appendChild(dl);
      helpEl.hidden = true;
      helpEl.addEventListener('click', function () { helpEl.hidden = true; });
      document.body.appendChild(helpEl);
    }
    helpEl.hidden = !helpEl.hidden;
  }

  // ── 출처 칩 · 근거 패널 ───────────────────────────────────────────────
  // 근거는 덱 안의 JSON 한 벌에 모은다. 칩은 키만 들고 있다 — 같은 근거를
  // 여러 장에서 가리켜도 내용은 한 곳에서 고친다.
  var GRADES = { A: '1차 공식 자료', B: '학술·전문기관', C: '언론·2차 자료', R: '직접 조회·집계' };
  var EV = {};
  (function () {
    var el = document.getElementById('bl-evidence');
    if (!el) return;
    try {
      var d = JSON.parse(el.textContent);
      EV = d.ev || {};
      if (d.grades) Object.keys(d.grades).forEach(function (g) { GRADES[g] = d.grades[g]; });
    } catch (err) { if (window.console) console.warn('bl-evidence JSON 을 읽지 못했다', err); }
  })();

  var evEl = null, evFrom = null;
  function evOn() { return !!(evEl && !evEl.hidden); }
  function mk(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function openEvidence(chip) {
    var key = chip.getAttribute('data-ev'), e = EV[key];
    if (!evEl) {
      evEl = mk('div'); evEl.id = 'bl-ev-panel';
      evEl.setAttribute('role', 'dialog'); evEl.setAttribute('aria-modal', 'true');
      evEl.setAttribute('aria-labelledby', 'bl-ev-title');
      evEl.hidden = true;
      evEl.addEventListener('click', function (ev) { if (ev.target === evEl) closeEvidence(); });
      document.body.appendChild(evEl);
    }
    evEl.textContent = '';
    var box = mk('div', 'bl-ev-box'), head = mk('div', 'bl-ev-head');
    head.appendChild(mk('span', 'bl-ev-id', key));
    if (e && e.grade) {
      var g = mk('span', 'bl-ev-grade');
      g.setAttribute('data-g', e.grade);
      g.appendChild(mk('b', null, e.grade));
      g.appendChild(document.createTextNode(GRADES[e.grade] || ''));
      head.appendChild(g);
    }
    var x = mk('button', 'bl-ev-x', '×');
    x.type = 'button'; x.setAttribute('aria-label', '근거 닫기');
    x.onclick = closeEvidence;
    head.appendChild(x);
    box.appendChild(head);
    var t = mk('h3', 'bl-ev-title', e ? e.title : '근거 없음 — ' + key);
    t.id = 'bl-ev-title';
    box.appendChild(t);
    var claim = chip.getAttribute('data-claim');
    if (claim) box.appendChild(mk('p', 'bl-ev-claim', claim));
    if (e && e.facts && e.facts.length) {
      var ul = mk('ul', 'bl-ev-facts');
      e.facts.forEach(function (f) { ul.appendChild(mk('li', null, f)); });
      box.appendChild(ul);
    }
    if (e && (e.src || e.date)) {
      var src = mk('p', 'bl-ev-src', [e.src, e.date].filter(Boolean).join(' · '));
      if (e.url && /^https?:\/\//.test(e.url)) {
        src.appendChild(document.createTextNode(' · '));
        var a = mk('a', null, '원문');
        a.href = e.url; a.target = '_blank'; a.rel = 'noopener noreferrer';
        src.appendChild(a);
      }
      box.appendChild(src);
    }
    if (e && e.note) box.appendChild(mk('p', 'bl-ev-note', e.note));
    evEl.appendChild(box);
    evFrom = chip;
    evEl.hidden = false;
    x.focus();
  }
  function closeEvidence() {
    if (!evEl) return;
    evEl.hidden = true;
    if (evFrom) { evFrom.focus(); evFrom = null; }
  }
  document.addEventListener('click', function (ev) {
    var chip = ev.target.closest && ev.target.closest('.bl-ev[data-ev]');
    if (!chip) return;
    ev.preventDefault(); ev.stopPropagation();
    openEvidence(chip);
  }, true);

  // 상태가 있는 단추에 눌림을 표시한다
  function paintToggles() {
    function set(act, on) {
      Array.prototype.forEach.call(document.querySelectorAll('[data-act="' + act + '"]'), function (b) {
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }
    set('expand', !staged());
    set('horiz', deck.classList.contains('bl-deck--horiz'));
    set('notes', notesOn());
  }

  // ── 진행선 ────────────────────────────────────────────────────────────
  // 어디쯤인지만 알려 준다. 없으면 아무 일도 하지 않는다 — 덱이 이 줄을 안 넣어도
  // 뷰어가 죽지 않아야 한다.
  function paintProg() {
    var el = document.getElementById('bl-prog');
    if (!el) return;
    el.style.width = ((i + 1) / slides.length * 100) + '%';
  }

  // ── 조작 ──────────────────────────────────────────────────────────────
  var jump = '';
  function showJump() {
    var el = document.getElementById('bl-jump');
    if (!el) return;
    el.textContent = jump; el.hidden = !jump;
  }

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (evOn()) { if (e.key === 'Escape') { closeEvidence(); e.preventDefault(); } return; }
    if (helpOn() && (e.key === 'Escape' || e.key === '?')) { toggleHelp(); e.preventDefault(); return; }
    if (e.key >= '0' && e.key <= '9') { jump += e.key; showJump(); e.preventDefault(); return; }
    if (e.key === 'Enter' && jump) {
      var n = parseInt(jump, 10); jump = ''; showJump();
      if (n >= 1 && n <= slides.length) goTo(n - 1);
      e.preventDefault(); return;
    }
    if (e.key === 'Escape' && jump) { jump = ''; showJump(); e.preventDefault(); return; }

    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      if (!stepFwd()) goTo(i + 1);
      e.preventDefault();
    }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (!stepBack()) { goTo(i - 1); if (staged()) { step = maxStep(slides[i]); paint(); } }
      e.preventDefault();
    }
    if (e.key === 'Home') goTo(0);
    if (e.key === 'End') goTo(slides.length - 1);
    if (e.key === 's' || e.key === 'S') openScript();
    if (e.key === 'e' || e.key === 'E') { toggleExpand(); e.preventDefault(); }
    if (e.key === 'h' || e.key === 'H') { toggleHoriz(); e.preventDefault(); }
    if (e.key === 'n' || e.key === 'N') { toggleNotes(); e.preventDefault(); }
    if (e.key === '?') { toggleHelp(); e.preventDefault(); }
    if (e.key === 'f' || e.key === 'F') { togglePresent(); e.preventDefault(); }
    if (e.key === 'Escape' && deck.classList.contains('bl-deck--present')) exitPresent();
  });

  deck.addEventListener('click', function (e) {
    if (!deck.classList.contains('bl-deck--present')) return;
    if (e.target.closest && e.target.closest('button, a, .bl-ev, [data-int]')) return;
    if (!stepFwd()) goTo(i + 1);
  });

  // 조작판은 data-act 로 묶는다. id 로 묶으면 덱마다 이름을 새로 지어야 하고,
  // 한 글자만 달라도 버튼이 조용히 죽는다 — 눌러 보기 전에는 아무도 모른다.
  var ACTS = {
    prev:    function () { if (!stepBack()) goTo(i - 1); },
    next:    function () { if (!stepFwd()) goTo(i + 1); },
    present: togglePresent,
    script:  openScript,
    expand:  toggleExpand,
    horiz:   toggleHoriz,
    notes:   toggleNotes,
    help:    toggleHelp
  };
  Array.prototype.forEach.call(document.querySelectorAll('[data-act]'), function (b) {
    var fn = ACTS[b.getAttribute('data-act')];
    if (fn) b.onclick = fn;
  });
  // 예전 덱의 id 방식도 받아 준다
  var pb = document.getElementById('bl-present');
  if (pb) pb.onclick = togglePresent;
  var sb = document.getElementById('bl-script');
  if (sb) sb.onclick = openScript;

  paint();
})();
