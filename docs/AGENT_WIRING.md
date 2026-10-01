# 모든 에이전트를 이 저장소에 붙이는 법

이 문서는 덱을 만드는 법이 아니라, **에이전트가 이 저장소를 스스로 가지러 오게 만드는 법**이다.
덱 작업 자체는 `docs/CODEX_DECK_PROMPT.md` 가 다룬다.

---

## 먼저 알아야 할 것

**GitHub 계정을 연결했다는 사실만으로 에이전트가 이 템플릿을 쓰지는 않는다.** 어느 플랫폼도
사용자의 GitHub 계정을 훑어 스킬을 자동으로 찾아 오지 않는다. 에이전트는 자기가 열려 있는
저장소만 본다. 다른 저장소에서 일하다 "보고서 만들어줘" 라고 하면 이 템플릿은 시야에 없다.

그래서 필요한 것은 권한이 아니라 **지시**다. "회사 양식 요청을 받으면 이 저장소를 가져와라"
한 문단을 계정 지침에 심어 두면, 그때부터 GitHub 권한이 실제로 쓰인다. 등록은 계정당 한 번이고,
내용은 언제나 저장소 최신판이다 — 지침에는 경로만 들어가고 규격은 들어가지 않기 때문이다.

## 저장소 사정

| 항목 | 값 | 영향 |
|---|---|---|
| 공개 범위 | **public** | 인증 없이 clone 한다 |
| 기본 브랜치 | **`main`** | 표준이다. 별도 지정 없이 clone 하면 된다 |

`assets/` 의 견본 내용은 전부 가상 시나리오다. 실제 조직·인물·수치가 아니다.

## 에이전트별 경로

| 에이전트 | 저장소를 여는 세션 | 다른 곳에서 시작한 세션 |
|---|---|---|
| Claude Code 로컬 | `.claude/skills/` 자동 로드 | ①계정 지침 · ③플러그인 · ④사용자 스킬 폴더 |
| Claude Code 웹·원격 | 자동 로드 | ①계정 지침 (세션에 저장소를 붙이게 한다) |
| claude.ai 대화·모바일 | 해당 없음 | ①계정 지침 |
| Codex | `AGENTS.md` 자동 로드 | ②전역 `AGENTS.md` |
| 그 밖의 에이전트 | `AGENTS.md` 를 읽으면 자동 | ②와 같은 문단을 그 도구의 전역 지침에 |

---

## ① Claude 계정 지침 — 계정 전체에 한 번

claude.ai → 좌측 하단 이니셜 → Settings → **Instructions for Claude** 에 아래를 더한다.
이 지침은 그 계정의 모든 대화에 적용되므로, claude.ai 대화·모바일·각 PC 의 Claude Code·
원격 세션이 전부 덮인다.

```text
사내 보고서·발표자료·덱·슬라이드·회의록·공지·매뉴얼·보드·대시보드·현황판을 회사 양식이나
템플릿으로 만들라는 요청을 받으면, 새 스타일을 만들지 말고 먼저 아래 저장소를 현재 세션에
붙인다. 세션에 저장소를 붙이는 수단이 있으면 그것을 쓰고, 없으면 git clone 한다.

    github.com/hctinno/blue-report

붙인 뒤 docs/CODEX_DECK_PROMPT.md 를 전부 읽고 그대로 수행한다. 그 문서에 슬라이드 덱 12종,
A4 문서 4종, 웹 보드 5종의 목록과 각각의 --deck 이름, 금지 사항, 검사 절차가 들어 있다.
덱과 A4 문서와 웹 보드는 규격이 서로 달라 바꿔 쓸 수 없다. 용도가 분명하지 않으면 먼저 묻는다.

완료라고 말하기 전에 그 저장소의 검사 스크립트를 돌리고 결과를 함께 제시한다.
실패가 0 이 아니면 완료가 아니다.
```

## ② Codex 등 — 전역 지침

Codex 는 `.claude/skills/` 를 인식하지 못한다. 전역 지침 파일에 같은 문단을 넣되, 세션에
저장소를 붙이는 수단이 없으므로 `git clone` 으로 적는다.

```text
사내 보고서·발표자료·덱·회의록·공지·매뉴얼·보드·대시보드를 회사 양식이나 템플릿으로
만들라는 요청을 받으면, 새 스타일을 만들지 말고 먼저 아래를 받는다.

    git clone -b main https://github.com/hctinno/blue-report.git

이미 받아 둔 것이 있으면 git pull 로 갱신한다. 그다음 그 저장소의
docs/CODEX_DECK_PROMPT.md 를 전부 읽고 그대로 수행한다. 산출물은 그 저장소의
decks-out/ 에 넣는다. 완료 전에 그 저장소의 검사 스크립트를 돌리고 결과를 제시한다.
```

Codex 의 전역 지침 파일 위치는 그 도구의 현재 문서에서 확인한다. 확인하지 않은 경로에
그대로 쓰지 않는다. 설치를 자동화하려면 `scripts/install_codex_pointer.py` 를 쓴다.

```bash
python3 scripts/install_codex_pointer.py --check     # 상태만 본다
python3 scripts/install_codex_pointer.py --dry-run   # 무엇이 바뀔지만 출력
python3 scripts/install_codex_pointer.py             # 설치 또는 갱신
python3 scripts/install_codex_pointer.py --target <파일경로>
```

표식 블록 안만 관리하므로 사람이 직접 쓴 다른 내용은 건드리지 않는다.

## ③ Claude Code 플러그인 — PC 마다 한 번, 갱신은 GitHub 에서

계정 지침이 저장소를 **가져오게** 한다면, 플러그인은 저장소를 **미리 깔아 둔다.** 주력 PC 에는
둘 다 걸어 두는 편이 빠르다.

```bash
claude plugin marketplace add hctinno/blue-report
claude plugin install blue-report@blue-tools
```

이후 `claude plugin marketplace update` 가 GitHub 최신판을 당긴다.

## ④ 그 PC 안에서만

계정을 거치지 않고 이 PC 의 사용자 스킬 폴더에만 두려면 쓴다.

```bash
python3 scripts/install_blue_report_skill.py
```

---

## 걸었는지 확인하는 법

1. **세션을 새로 연다.** 실행 중인 세션은 새 지침·새 스킬을 읽지 않는다.
2. 템플릿과 무관한 폴더에서 한 줄 친다.

   ```
   우리 회사 양식으로 주간보고 덱 만들어줘
   ```

3. 에이전트가 **저장소를 먼저 가져오면** 제대로 걸린 것이다. 곧장 자기 스타일로 만들기
   시작하면 지침이 걸리지 않았거나 세션이 낡은 것이다.

## 판올림했을 때

| 경로 | 갱신 방법 |
|---|---|
| ① 계정 지침 | 없음. 경로만 적혀 있어 저장소가 바뀌면 저절로 최신 |
| ② Codex 전역 | 없음. 지침이 `git pull` 을 시킨다 |
| ③ 플러그인 | `claude plugin marketplace update` |
| ④ 사용자 스킬 폴더 | `git pull` 후 `install_blue_report_skill.py` 다시 실행 |
| 계정 스킬 zip | `build_account_skill_bundle.py` 로 다시 떠서 다시 업로드 |

①②가 손이 가장 덜 가는 이유는 **지침에 규격을 복사해 넣지 않기** 때문이다. 지침에 색값이나
덱 목록을 적으면 그 순간부터 저장소와 갈라진다. 경로만 적는다.
