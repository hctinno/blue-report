// 덱 뷰어 — 슬라이드 넘김, 축척, 쪽번호·문서명 자동 채움, 발표자 노트,
//           단계 전개(프래그먼트), 레이저, 대본 창.
// 용도별 덱이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.

(function () {
  var stage  = document.getElementById('stage');
  var frames = Array.prototype.slice.call(document.querySelectorAll('.br-frame'));
  var notes  = document.getElementById('notes');
  var notesText = document.getElementById('notes-text');
  var i = 0, showNotes = false;
  var allBtn = document.getElementById('all');
  var allMode = new URLSearchParams(location.search).get('all') === '1';
  var deckTitle = stage.dataset.deckTitle || '';

  // 동작을 줄여 달라는 설정을 한 곳에서 읽는다. 여기서 true 면 단계 전개도
  // 전이 없이 즉시 바뀐다 — CSS 만 꺼 두면 JS 가 켠 전이가 남아 어지럽다.
  var calm = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  // 푸터의 문서명과 쪽번호는 여기서 채운다. 슬라이드를 넣거나 빼도 번호가 어긋나지 않는다.
  //
  // data-apx 가 붙은 지면은 부록이다. 본문과 다른 체계로 센다 — 본문은 01·02,
  // 부록은 「부록 1 / 6」. 같은 자리에 다른 체계가 찍히는 것이 부록으로 넘어왔다는
  // 신호다. 부록이 없는 덱에서는 apxTotal 이 0 이라 예전과 똑같이 동작한다.
  var apxTotal = 0;
  frames.forEach(function (f) { if (f.hasAttribute('data-apx')) apxTotal++; });

  var bodyN = 0, apxN = 0;
  frames.forEach(function (f) {
    var isApx = f.hasAttribute('data-apx');
    if (isApx) apxN++; else bodyN++;
    var foot = f.querySelector('.br-footer');
    if (!foot) return;                       // 표지·간지·마무리는 푸터가 없다
    var page = isApx
      ? '부록 ' + apxN + ' / ' + apxTotal
      : String(bodyN).padStart(2, '0');
    foot.innerHTML = deckTitle
      ? deckTitle + ' <strong>' + page + '</strong>'
      : '<strong>' + page + '</strong>';
  });

  // ── 단계 전개(프래그먼트) ────────────────────────────────────────────────
  // 슬라이드 안의 요소에 data-f="1" 처럼 번호를 붙이면 그 순서로 하나씩 켜진다.
  //
  // 기본은 **검토 모드**다 — 전부 펼쳐 둔다. 만드는 사람은 한 장을 통째로 보면서
  // 고치지, 단계를 넘겨 가며 고치지 않는다. 발표 모드로 들어갈 때만 단계로 접는다.
  // 이 방향이 반대면(기본이 단계별) 덱을 열자마자 내용이 비어 보여 고장으로 읽힌다.
  //
  // 번호는 1부터다. 같은 번호를 여럿에 붙이면 함께 켜진다.
  var step = 0;

  function fragsOf(f) {
    return Array.prototype.slice.call(f.querySelectorAll('[data-f]'));
  }

  function maxStep(f) {
    return fragsOf(f).reduce(function (m, el) {
      return Math.max(m, parseInt(el.getAttribute('data-f'), 10) || 0);
    }, 0);
  }

  // open=true 면 단계를 무시하고 전부 켠다(검토·전체 보기·인쇄).
  function paintFrags(f, open) {
    fragsOf(f).forEach(function (el) {
      var n = parseInt(el.getAttribute('data-f'), 10) || 0;
      el.classList.toggle('is-shown', open || n <= step);
    });
  }

  function staged() {
    // 발표 모드에서만 접는다. 전체 보기 중에는 발표 모드라도 펼친다.
    return document.body.classList.contains('present')
        && !document.body.classList.contains('all-mode--live');
  }

  function repaint() {
    var open = !staged();
    // 숨기는 일은 CSS 가 하되, **이 클래스가 붙었을 때만** 한다. 기본값으로 숨겨 두면
    // JS 가 늦거나 막힌 환경에서 본문이 통째로 빈 화면이 된다 — 덱은 JS 없이도
    // 읽혀야 한다.
    document.body.classList.toggle('staged', !open);
    frames.forEach(function (f) { paintFrags(f, open || f !== frames[i]); });
    if (!open) paintFrags(frames[i], false);
    syncNotes();
  }

  // 다음 단계. 더 없으면 false 를 돌려 호출한 쪽이 장을 넘기게 한다.
  function stepFwd() {
    if (!staged()) return false;
    if (step >= maxStep(frames[i])) return false;
    step++; repaint(); return true;
  }

  function stepBack() {
    if (!staged()) return false;
    if (step <= 0) return false;
    step--; repaint(); return true;
  }

  // 지면 전체가 언제나 화면 안에 들어오게 맞춘다.
  //   - 가로·세로 중 더 빡빡한 쪽에 맞춘다(contain). 16:9 가 아닌 화면에서는 위아래나
  //     좌우에 여백이 남는다. 잘라 내지 않는다.
  //   - HUD 띠 높이를 빼 둔다. 안 빼면 16:9 정확히 맞는 화면에서 지면 아래 47px 가
  //     HUD 뒤로 들어가 꼬리말(문서명·쪽번호)이 가려진다.
  //   - translate(-50%,-50%) 로 되돌려 어느 창 크기에서든 가운데에 앉힌다.
  function scale() {
    var hud = document.getElementById('hud');
    // 발표 모드에서는 HUD 가 가장자리에서만 잠깐 뜨는 덧판이라 무대에서 빼지 않는다.
    // 빼면 띠가 뜰 때마다 지면이 움찔한다.
    var hudH = (hud && hud.offsetHeight && !document.body.classList.contains('present'))
             ? hud.offsetHeight : 0;
    var chrome = hudH + (showNotes ? window.innerHeight * .34 : 0);
    // 무대를 HUD·노트 띠 위까지로 줄인다. 배율만 줄이고 무대를 그대로 두면 지면이
    // 화면 한가운데에 앉아 아래쪽이 띠 뒤로 들어간다.
    stage.style.bottom = chrome + 'px';
    var s = Math.min(window.innerWidth / 1920,
                     Math.max(window.innerHeight - chrome, 100) / 1080);
    frames.forEach(function (f) {
      f.style.transform = 'translate(-50%,-50%) scale(' + s + ')';
    });
  }

  function show(n) {
    i = (n + frames.length) % frames.length;
    step = 0;                                // 장을 넘기면 단계는 처음부터
    frames.forEach(function (f, k) {
      f.classList.toggle('is-active', k === i);
      // 애니메이션은 활성 슬라이드에서만 재생한다
      if (k === i) { f.removeAttribute('data-deck-active'); void f.offsetWidth; f.setAttribute('data-deck-active', ''); }
      else { f.removeAttribute('data-deck-active'); }
    });
    // HUD 요소가 하나라도 없으면 여기서 예외가 나고, show() 를 부른 쪽의 나머지가
    // 통째로 멈춘다. 실제로 덱 2종에 #notes-text 가 빠져 있어 슬라이드를 넘길 때마다
    // 던지고 있었고, 그래서 '목록 → 발표' 전환이 조용히 실패했다. 없으면 건너뛴다.
    var pos = document.getElementById('pos');
    var nm = document.getElementById('name');
    if (pos) pos.textContent = (i + 1) + ' / ' + frames.length;
    if (nm) nm.textContent = frames[i].dataset.label;
    repaint();
  }

  // 마지막 단계까지 펼친 채로 이전 장으로 간다. 뒤로 가는데 첫 단계로 떨어지면
  // 방금 보고 온 화면이 안 나와 발표가 끊긴다.
  function showPrevFull() {
    show(i - 1);
    if (staged()) { step = maxStep(frames[i]); repaint(); }
  }

  // ── 발표자 노트 · 대본 창 ────────────────────────────────────────────────
  var scriptWin = null;

  function noteOf(k) {
    var f = frames[(k + frames.length) % frames.length];
    return f.dataset.notes || '';
  }

  function syncNotes() {
    if (notesText) {
      notesText.textContent = noteOf(i) || '(이 슬라이드에는 노트가 없다)';
    }
    pushScript();
  }

  // 대본 창 — 발표자만 보는 두 번째 화면.
  //
  // 새 창에 문서를 직접 써 넣는다. 파일을 따로 두면 단일 파일 덱에서 열 것이 없고,
  // 주소를 만들어 열면 file:// 에서 막힌다. document.write 는 같은 창을 계속
  // 갈아 끼우므로 본 창과 동기화가 단순해진다.
  function openScript() {
    if (scriptWin && !scriptWin.closed) { scriptWin.focus(); return; }
    scriptWin = window.open('', 'br-script', 'width=560,height=760');
    if (!scriptWin) {                        // 팝업 차단
      alert('대본 창이 브라우저에 막혔다. 이 사이트의 팝업을 허용한 뒤 다시 누른다.');
      return;
    }
    scriptWin.document.open();
    scriptWin.document.write(
      '<!doctype html><meta charset="utf-8"><title>대본 — ' + esc(deckTitle) + '</title>' +
      '<style>' +
      'body{margin:0;padding:22px 24px;background:#0c121e;color:#dbe3ec;' +
        "font:400 16px/1.7 system-ui,-apple-system,'Malgun Gothic',sans-serif}" +
      'h1{margin:0 0 4px;font:600 13px/1.3 system-ui,sans-serif;letter-spacing:.14em;' +
        'text-transform:uppercase;color:#8fa4bd}' +
      '#t{font:600 28px/1 ui-monospace,Menlo,monospace;color:#fff;margin:0 0 18px}' +
      '#cur{white-space:pre-wrap;border-left:3px solid #2f4a9c;padding-left:14px;margin-bottom:22px}' +
      '#nxt{white-space:pre-wrap;color:#8fa4bd;border-left:3px solid #2b3852;padding-left:14px}' +
      'h2{margin:0 0 6px;font:600 11px/1 system-ui,sans-serif;letter-spacing:.14em;' +
        'text-transform:uppercase;color:#8fa4bd}' +
      '</style>' +
      '<h1 id="pg"></h1><p id="t">00:00</p>' +
      '<h2>지금</h2><div id="cur"></div>' +
      '<h2>다음</h2><div id="nxt"></div>');
    scriptWin.document.close();

    // 시계는 대본 창 자신이 돌린다. 본 창이 멈춰도 시간은 흘러야 한다.
    var t0 = Date.now();
    scriptWin.setInterval(function () {
      var el = scriptWin.document.getElementById('t');
      if (!el) return;
      var s = Math.floor((Date.now() - t0) / 1000);
      el.textContent = String(Math.floor(s / 60)).padStart(2, '0') + ':' +
                       String(s % 60).padStart(2, '0');
    }, 1000);
    pushScript();
  }

  function pushScript() {
    if (!scriptWin || scriptWin.closed) return;
    var d = scriptWin.document;
    var pg = d.getElementById('pg'), cur = d.getElementById('cur'), nxt = d.getElementById('nxt');
    if (!pg) return;                         // 아직 다 써지지 않았다
    var ms = maxStep(frames[i]);
    pg.textContent = (i + 1) + ' / ' + frames.length +
                     (ms ? '   단계 ' + step + ' / ' + ms : '') +
                     (frames[i].dataset.label ? '   ' + frames[i].dataset.label : '');
    cur.textContent = noteOf(i) || '(노트 없음)';
    nxt.textContent = noteOf(i + 1) || '(노트 없음)';
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // 본 창이 닫히면 대본 창도 닫는다. 남겨 두면 갱신되지 않는 화면이 떠 있어
  // 발표자가 엉뚱한 장의 대본을 읽는다.
  window.addEventListener('beforeunload', function () {
    if (scriptWin && !scriptWin.closed) scriptWin.close();
  });

  // ── 레이저 포인터 ────────────────────────────────────────────────────────
  // 발표 중에만 뜬다. 편집 화면에 빨간 점이 따라다니면 방해만 된다.
  var laser = null, laserOn = false;

  function toggleLaser() {
    laserOn = !laserOn;
    document.body.classList.toggle('laser', laserOn);
    if (laserOn && !laser) {
      laser = document.createElement('div');
      laser.id = 'laser';
      laser.setAttribute('aria-hidden', 'true');
      document.body.appendChild(laser);
    }
    if (laser) laser.style.display = laserOn ? 'block' : 'none';
  }

  // 발표 모드 — 브라우저 전체화면으로 들어가고 HUD·노트를 감춘다.
  // 이게 없으면 F11 을 눌러도 화면만 커지고 버튼은 그대로 남는다. 발표를 못 한다.
  //
  // 전체화면은 사용자 제스처가 있어야 열리고, iframe(Artifact 미리보기 등)에서는
  // allow="fullscreen" 이 없으면 거부된다. 거부돼도 present 클래스는 붙인다 —
  // 창을 못 키워도 버튼이 사라지고 지면이 창을 가득 채우면 발표는 된다.
  var idleTimer = null;

  function inFull() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement);
  }

  function setPresent(on) {
    document.body.classList.toggle('present', on);
    if (!on) {
      document.body.classList.remove('idle');
      document.body.classList.remove('hud-peek');
      clearTimeout(idleTimer);
      if (laserOn) toggleLaser();
    }
    step = 0;
    repaint();
    scale();
  }

  function enterPresent() {
    // 전체 보기(세로 나열)에서 바로 들어오면 먼저 한 장씩으로 되돌린다.
    if (document.body.classList.contains('all-mode--live')) allBtn.onclick();
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen;
    setPresent(true);
    if (req) {
      var r = req.call(el);
      if (r && r.catch) r.catch(function () { /* 거부돼도 present 는 유지한다 */ });
    }
  }

  function exitPresent() {
    if (inFull()) {
      var ex = document.exitFullscreen || document.webkitExitFullscreen;
      if (ex) ex.call(document);
    }
    setPresent(false);
  }

  function togglePresent() {
    if (document.body.classList.contains('present')) exitPresent();
    else enterPresent();
  }

  // 브라우저가 Esc·F11 로 전체화면을 끄면 클래스도 따라 꺼야 한다.
  // 안 그러면 창은 돌아왔는데 버튼이 계속 숨어 있어 되돌아갈 길이 없다.
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
    document.addEventListener(ev, function () {
      if (!inFull() && document.body.classList.contains('present')) setPresent(false);
      else scale();
    });
  });

  // F11 은 브라우저 UI 전체화면이라 Fullscreen API 이벤트를 쏘지 않는다.
  // fullscreenchange 만 듣고 있으면 F11 을 눌러도 HUD 가 그대로 남는다 —
  // "전체화면인데 버튼이 보인다"가 정확히 이것이다.
  // display-mode 미디어 질의는 F11 에도 반응하므로 둘을 함께 듣는다.
  if (window.matchMedia) {
    var mq = window.matchMedia('(display-mode: fullscreen)');
    var onMq = function (e) { setPresent(e.matches || inFull()); };
    if (mq.addEventListener) mq.addEventListener('change', onMq);
    else if (mq.addListener) mq.addListener(onMq);
    if (mq.matches) setPresent(true);          // 전체화면인 채로 열린 경우
  }

  document.addEventListener('mousemove', function (e) {
    if (laserOn && laser) {
      laser.style.left = e.clientX + 'px';
      laser.style.top  = e.clientY + 'px';
    }
    if (!document.body.classList.contains('present')) return;
    // 발표 중에는 마우스를 움직였다고 조작판이 뜨지 않는다. 화면 맨 아래
    // 가장자리에 갖다 댈 때만 뜬다 — 발표 중 손이 스치는 것만으로 띠가 올라오면
    // 청중에게 그대로 보인다.
    document.body.classList.toggle('hud-peek',
      e.clientY > window.innerHeight - 56);
    document.body.classList.remove('idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () { document.body.classList.add('idle'); }, 2000);
  });

  function toggleNotes() {
    showNotes = !showNotes;
    notes.hidden = !showNotes;
    scale();
  }

  if (allMode) {
    document.body.classList.add('all-mode');
    frames.forEach(function (f) {
      f.setAttribute('data-deck-active', '');
      f.style.transform = 'none';            // 원본 크기 유지 (스크린샷·PDF용)
      paintFrags(f, true);                   // 내보내기에서는 단계를 전부 펼친다
    });
    return;
  }

  window.addEventListener('resize', scale);

  // ── 숫자 점프 ────────────────────────────────────────────────────────────
  // 숫자를 누르면 쌓이고 Enter 로 그 장으로 간다. 부록이 긴 덱에서 화살표로
  // 스무 번 넘기는 대신 「32 Enter」로 간다. Esc 로 버린다.
  var jump = '';
  function showJump() {
    var el = document.getElementById('jump');
    if (!el) return;
    el.textContent = jump;
    el.hidden = !jump;
  }

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    if (e.key >= '0' && e.key <= '9') { jump += e.key; showJump(); e.preventDefault(); return; }
    if (e.key === 'Enter' && jump) {
      var n = parseInt(jump, 10);
      jump = ''; showJump();
      if (n >= 1 && n <= frames.length) show(n - 1);
      e.preventDefault(); return;
    }
    if (e.key === 'Escape' && jump) { jump = ''; showJump(); e.preventDefault(); return; }

    // 단계가 남아 있으면 먼저 단계를 넘긴다. 다 넘겼을 때만 장이 넘어간다.
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      if (!stepFwd()) show(i + 1);
      e.preventDefault();
    }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (!stepBack()) showPrevFull();
      e.preventDefault();
    }
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(frames.length - 1);
    if (e.key === 'n' || e.key === 'N') toggleNotes();
    if (e.key === 's' || e.key === 'S') openScript();
    if (e.key === 'l' || e.key === 'L') {
      if (document.body.classList.contains('present')) toggleLaser();
    }
    if (e.key === 'f' || e.key === 'F') { togglePresent(); e.preventDefault(); }
    // 진짜 전체화면이면 브라우저가 Esc 를 먹고 위 리스너가 정리한다.
    // 거부돼 present 클래스만 붙은 경우에는 여기서 빠져나온다.
    if (e.key === 'Escape' && document.body.classList.contains('present')) exitPresent();
  });

  stage.addEventListener('click', function () {
    if (!document.body.classList.contains('present')) return;
    if (!stepFwd()) show(i + 1);
  });

  document.getElementById('prev').onclick = function () { if (!stepBack()) showPrevFull(); };
  document.getElementById('next').onclick = function () { if (!stepFwd()) show(i + 1); };
  document.getElementById('notes-btn').onclick = toggleNotes;
  var presentBtn = document.getElementById('present');
  if (presentBtn) presentBtn.onclick = togglePresent;
  var scriptBtn = document.getElementById('script-btn');
  if (scriptBtn) scriptBtn.onclick = openScript;
  // 전체 보기는 제자리에서 켜고 끈다. URL 을 바꾸면 새로고침이 되고, 되돌아갈 길도 없다.
  // Artifact 처럼 주소를 못 바꾸는 곳에서도 이 방식이면 동작한다.
  allBtn.onclick = function () {
    var on = !document.body.classList.contains('all-mode--live');
    document.body.classList.toggle('all-mode', on);
    document.body.classList.toggle('all-mode--live', on);
    frames.forEach(function (f) {
      if (on) { f.setAttribute('data-deck-active', ''); f.style.transform = 'none'; }
      else { f.removeAttribute('data-deck-active'); f.style.transform = ''; }
    });
    allBtn.textContent = on ? '한 장씩' : '전체 보기';
    repaint();                               // 전체 보기에서는 단계를 전부 펼친다
    if (on) { window.scrollTo(0, 0); } else { scale(); show(i); }
  };

  // 동작 감축 설정이면 단계 전이를 끈다. CSS 쪽에도 같은 분기가 있으나,
  // 여기서 클래스를 붙여 두면 인라인으로 만든 단일 파일에서도 함께 따라간다.
  if (calm) document.body.classList.add('calm');

  scale();
  show(0);
})();
