// 문서 뷰어 — 쪽번호·문서명·문서번호 자동 채움, 축척 맞춤, 인쇄.
// 문서 여러 종이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.
//
// 채우는 자리는 셋뿐이다. 나머지 머리말·꼬리말 내용은 HTML 에 그대로 둔다.
//   .bd-pageno    n / m
//   .bd-doctitle  .bd-doc 의 data-doc-title
//   .bd-docno     .bd-doc 의 data-doc-no

(function () {
  var doc   = document.querySelector('.bd-doc');
  var pages = Array.prototype.slice.call(document.querySelectorAll('.bd-page'));
  if (!doc || !pages.length) return;

  var title = doc.dataset.docTitle || '';
  var docno = doc.dataset.docNo || '';
  var total = pages.length;

  pages.forEach(function (pg, n) {
    pg.querySelectorAll('.bd-doctitle').forEach(function (el) { el.textContent = title; });
    pg.querySelectorAll('.bd-docno').forEach(function (el) { el.textContent = docno; });
    pg.querySelectorAll('.bd-pageno').forEach(function (el) {
      el.textContent = (n + 1) + ' / ' + total;
    });
  });

  // 창이 좁으면 지면을 줄여 가로 스크롤이 생기지 않게 한다. 인쇄에는 영향이 없다.
  function fit() {
    var w = parseFloat(getComputedStyle(document.documentElement)
                       .getPropertyValue('--bd-page-w')) || 794;
    var s = Math.min(1, (window.innerWidth - 48) / w);
    doc.style.transform = s < 1 ? 'scale(' + s + ')' : '';
    doc.style.transformOrigin = 'top center';
  }
  window.addEventListener('resize', fit);
  fit();

  var hud = document.getElementById('bd-hud');
  if (!hud) return;
  var pos = hud.querySelector('#bd-pos');
  if (pos) pos.textContent = total + '쪽';
  var pr = hud.querySelector('#bd-print');
  if (pr) pr.onclick = function () { window.print(); };
})();
