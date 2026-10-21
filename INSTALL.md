# Codex에서 한 줄로 설치하고 바로 시작하기

사용자는 Codex 대화창에 다음 한 줄을 붙여넣는다.

```text
블루 리포트를 설치하고 이 대화에서 바로 발표자료 만들기를 시작해 줘. 설치 지침: https://github.com/hctinno/blue-report/blob/main/INSTALL.md
```

이하 내용은 설치를 수행하는 에이전트의 작업 지침이다. 사용자가 ZIP을 직접 다운로드하거나 명령을 조합하게 하지 않는다.

## 1. 공개 설치본 받기

GitHub 공개 저장소 hctinno/blue-report의 최신 릴리스에서 blue-report-codex.zip을 받는다.
릴리스 메타데이터는 https://api.github.com/repos/hctinno/blue-report/releases/latest 이며,
설치 파일 주소는 https://github.com/hctinno/blue-report/releases/latest/download/blue-report-codex.zip 이다.
공개 파일이므로 GitHub 로그인이나 API 키를 요구하지 않는다. 다운로드·압축 해제는 에이전트가 수행한다.

임시 폴더에 받고 메타데이터의 SHA-256 digest와 다운로드 파일을 비교한다. 불일치하거나 릴리스·파일이 없으면 설치하지 않고 정확한 원인을 알린다.
ZIP의 모든 경로가 압축 해제 폴더 안에 머무는지 확인하고 해제한다. blue-report/SKILL.md, agents/openai.yaml, brand/hct/brand.json, scripts/style_previews.py, scripts/check_pptx.py가 있어야 한다.
이 패키지는 회사 자산과 내장 검사기를 포함한다. 저장소의 .claude/skills/blue-report 폴더만 복사하는 것으로 대신하면 회사 자산이 빠질 수 있다.

## 2. 개인 스킬 설치·갱신

현재 활성 blue-report 설치 위치를 확인할 수 있으면 그 위치를 사용한다. 새 설치는 CODEX_HOME이 있으면 그 아래 skills/blue-report, 없으면 ~/.agents/skills/blue-report에 넣는다.
대상은 실제 blue-report 폴더여야 하며 다른 위치를 가리키는 링크에 설치하지 않는다.
기존 설치본은 스킬 탐색 폴더 밖의 skill-backups/blue-report 아래에 시각을 붙인 폴더로 먼저 복사한다. 예: ~/.agents/skill-backups/blue-report/<시각>.
사용 중인 Windows 폴더는 이름 변경이 막힐 수 있으므로 내용을 백업하고 파일을 갱신한다. 개인이 추가한 파일은 보존하며 설치 실패 시 백업으로 이전 파일을 복원한다.
패키지의 blue-report 폴더 내용을 설치 위치로 복사한다. .claude-plugin/plugin.json을 설치해 스킬 이름에 Claude 플러그인 접두사가 붙게 하지 않는다. 기존 설치본에 이 파일이 있으면 백업에 보존한 후 설치 위치에서는 해당 파일만 제거한다. INSTALLATION.json으로 버전과 출처를 확인한다.
전역 AGENTS.md·인증·모델·승인 정책을 바꾸거나 실행 중인 다른 세션을 중단하지 않는다.

## 3. 같은 대화에서 사용 시작

설치된 SKILL.md와 references/business-presentation-intake.md를 직접 읽고 그 지침을 현재 대화에 적용한다.
자동 스킬 목록 반영은 다음 턴부터일 수 있으므로, 현재 작업은 설치된 파일을 읽어 이어간다. 재시작이나 새 대화를 사용 시작의 필수 조건으로 요구하지 않는다.
다른 Codex CLI·에이전트를 새로 실행하거나 외부 유료 AI를 호출하지 않는다.

설치 버전과 준비 상태를 짧게 알린 뒤, 이미 제공된 자료와 대화에서 조건을 파악한다. 미결인 중요한 질문 하나로 발표자료 기획을 바로 시작한다.
주제가 없으면 어떤 내용의 발표자료인지 묻는다. 주제를 알면 목적·청중 등 실제로 모르는 항목으로 이어간다. 사용자가 자료 경로나 주제를 한 줄에 덧붙였으면 먼저 반영한다.
필요한 출력 형식이 정해진 뒤 scripts/ensure_deps.py로 해당 도구를 확인·준비한다. 설치 단계에서 모든 제작 도구를 미리 설치하지 않는다.
파일·네트워크·실행 권한 때문에 설치를 완료하지 못했으면 그 범위와 필요한 조건을 알리고 완료했다고 말하지 않는다.
