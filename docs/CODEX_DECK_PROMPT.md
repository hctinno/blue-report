# Codex 및 다른 에이전트의 발표자료 제작 진입점

## Codex 대화창에서 한 줄로 시작

```text
블루 리포트를 설치하고 이 대화에서 바로 발표자료 만들기를 시작해 줘. 설치 지침: https://github.com/hctinno/blue-report/blob/main/INSTALL.md
```

에이전트가 [설치·시작 지침](../INSTALL.md)에 따라 다운로드·백업·설치 확인을 수행하고 현재 대화에서 기획 질문으로 이어간다. 사용자가 ZIP을 직접 내려받을 필요는 없다. 뒤에 주제·자료 경로를 추가할 수도 있다.

## 한 번 설치하고 호출

저장소 루트에서 `python scripts/install_codex_skill.py`를 실행한다. macOS·Linux는 `python3`를 사용한다.
Codex의 개인 스킬 폴더에 회사 브랜드 자산과 렌더 스크립트를 함께 설치한다.
다음 요청부터 `/skills`에서 blue-report를 선택하거나 `$blue-report`로 호출한다.
기존 설치본 갱신은 `python scripts/install_codex_skill.py --update`다. 이전 설치본은 별도 백업한다.

```text
$blue-report 이 자료로 발표자료를 만들고 싶어. 처음이니 필요한 것부터 쉽게 물어봐 줘.
```

자료 파일·폴더·링크 또는 주제만 제공해도 시작할 수 있다. 긴 프롬프트나 JSON을 작성할 필요가 없다.
스킬이 자료를 읽고 중요한 것만 질문하며, 목적에 맞는 구성·형식·스타일을 이유와 함께 추천한다.
이미 정한 조건은 반복해서 묻지 않는다. “나머지는 추천대로”라고 위임할 수도 있다.
스타일은 실제 PNG를 보고 번호나 말로 고른다. 완성 후에도 “결론을 앞에”, “3장을 간단히”처럼 수정할 수 있다.

## 저장소 없이 다른 직원에게 전달

직원은 [최신 Codex 스킬 ZIP](https://github.com/hctinno/blue-report/releases/latest/download/blue-report-codex.zip)을 받아 아래 설치 방법을 따른다.

관리자는 다음 명령으로 회사 자산·지침·내장 검사기를 담은 독립 Codex 스킬 ZIP을 만든다.

```bash
python scripts/install_codex_skill.py --bundle decks-out/blue-report-codex.zip
```

받는 사람은 ZIP을 Codex에 제공하고 “이 ZIP을 개인 스킬로 설치해 줘”라고 요청할 수 있다.
설치를 수행하는 에이전트는 ZIP의 blue-report 폴더를 개인 스킬 폴더에 넣는다. 기본은 ~/.agents/skills이며 CODEX_HOME을 쓰는 환경에서는 그 아래 skills다. 기존 폴더가 있으면 백업한 뒤 갱신한다.
설치 후 /skills에서 블루 리포트를 선택하거나 $blue-report로 호출한다. UI 표시는 환경에 따라 이름 또는 설명으로 나타날 수 있다.
GitHub 계정·원본 저장소·추가 디자인 스킬을 받는 사람의 PC에 둘 필요는 없다. 이 ZIP도 판올림 때 새 묶음으로 갱신한다.

## 실행 환경

파일 읽기·쓰기와 명령 실행이 가능한 Codex 환경에서 사용한다. 렌더링은 Python·로컬 브라우저를 사용하고, PPTX 생성에는 Node.js도 필요하다.
스킬은 요청한 형식의 도구만 확인하고 허용된 설치를 수행한다. 상태 확인은 scripts/ensure_deps.py --for html --check, 준비는 같은 명령의 --check를 --prepare로 바꾼다. PDF·PPTX는 --for pdf·pptx를 사용한다.
조직 정책이나 실행 도구 제한으로 준비가 막히면 필요한 조건을 구체적으로 알린다. 채팅만 가능한 환경에서 파일 생성·렌더 검증까지 된다고 약속하지 않는다.
기획 대화·회사 디자인·내장 검수에는 다른 스킬이나 특정 MCP 서비스가 필요하지 않다. 외부 조사·이미지 생성은 사용 가능한 도구와 사용자가 요청한 범위에서 별도로 수행한다.

## 저장소에서 직접 작업하는 경우

`.claude/skills/blue-report/SKILL.md`를 읽고 그 절차를 따른다. 기획 절차를 이 문서에 복제하지 않는다.
스킬 루트는 `.claude/skills/blue-report/`이며 회사 브랜드는 저장소 루트의 `brand/hct/brand.json`이다.
출력은 요청한 작업 폴더 또는 저장소의 `decks-out/`에 저장한다.
기존 변경사항을 보존하며 작업 중인 저장소에 자동 git pull을 실행하지 않는다.

## 공통 흐름

1. 제공 자료와 앞선 대화를 확인하고 목적·청중·용도·형식·분량·효과의 미결 사항을 하나씩 질문한다.
2. 같은 내용의 스타일 후보를 실제 PNG로 렌더링해 보여주고, 선택 또는 명시적 위임을 받는다.
3. 장별 메시지와 확정한 디자인 방향을 적용해 요청한 형식으로 제작한다.
4. 결과 형식별 검사와 실제 화면 확인 후 파일을 전달한다.

작업 폴더의 기획 기록으로 선택한 방향을 이어가며, 품질 기준은 스킬의 references/quality-and-delivery.md를 따른다.

시각 비교의 명령과 파일은 [STYLE_PREVIEWS.md](STYLE_PREVIEWS.md)에 있다.
PNG는 정지 화면이며 애니메이션·상호작용의 구현 확인을 대신하지 않는다.
기획·원본·검사에서 확인하지 않은 내용이나 동작을 완료로 보고하지 않는다.
