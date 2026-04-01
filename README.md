# hwp-extractor

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Claude Skill](https://img.shields.io/badge/Claude-Cowork%20Skill-blueviolet?logo=anthropic&logoColor=white)
![Plugin](https://img.shields.io/badge/Claude-Plugin-blue?logo=anthropic&logoColor=white)
![Format](https://img.shields.io/badge/지원포맷-.hwp%20%7C%20.hwpx-blue)
![Dependencies](https://img.shields.io/badge/의존성-없음-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

> Claude Code 플러그인 — HWP/HWPX 파일을 마크다운으로 변환

한컴오피스 문서 포맷인 `.hwp`(바이너리 OLE)와 `.hwpx`(ZIP+XML)에서 텍스트를 추출하여 마크다운으로 변환하는 Claude Code 플러그인입니다. **별도 라이브러리 설치 없이 표준 Python만 사용합니다.**

---

## 설치

### 방법 1: 플러그인으로 설치 (권장)

```bash
git clone https://github.com/iamupd/hwp-extractor.git
claude --plugin-dir ./hwp-extractor
```

### 방법 2: 스킬 파일만 복사

```bash
mkdir -p .claude/skills/hwp
cp -r hwp-extractor/skills/hwp/* .claude/skills/hwp/
```

### 방법 3: 스크립트만 직접 사용

```bash
git clone https://github.com/iamupd/hwp-extractor.git
python hwp-extractor/skills/hwp/scripts/hwp_to_markdown.py "문서.hwp"
```

---

## 사용법

### Claude 스킬로 사용

Claude에게 자연어로 요청하면 자동으로 스킬이 실행됩니다:

```
"RICS 개선방향.hwp 마크다운으로 뽑아줘"
"docs 폴더 hwp 파일 전부 변환해줘"
"이 hwpx 파일 내용 읽어줘"
```

### 스크립트 직접 실행

```bash
# 단일 HWP 파일 변환 (stdout 출력)
python scripts/hwp_to_markdown.py "문서.hwp"

# 단일 HWPX 파일 → .md 저장
python scripts/hwp_to_markdown.py "문서.hwpx" -o "출력.md"

# 디렉토리 일괄 변환 (자동으로 markdown/ 서브폴더 생성)
python scripts/hwp_to_markdown.py "/경로/폴더/"
```

### Python 모듈로 임포트

```python
import sys
sys.path.insert(0, 'skills/hwp/scripts')

from hwp_extract import extract_hwp
from hwpx_extract import extract_hwpx

markdown = extract_hwp("문서.hwp")    # HWP 바이너리
markdown = extract_hwpx("문서.hwpx")  # HWPX ZIP+XML
print(markdown)
```

---

## 출력 예시

**입력:** `RICS 개선방향.hwp`

```markdown
# 실시간 종합건설정보 시스템(RICS) 개선방향

> 출처: RICS 개선방향.hwp

---

**실시간 종합건설정보 시스템(RICS) 개선방향**

## 1. 현황 및 문제점

- 전국 320여개의 건설공사 현황, 현장별 안전 정보 등을 실시간으로 확인할 수 있는
  종합건설정보(RICS) 시스템을 구축

## 2. 개선방향

### 시스템 기능 고도화

- 과거 데이터를 축적 및 비교분석 할 수 있는 기능 도입
```

---

## 구조

```
hwp-extractor/
├── .claude-plugin/
│   └── plugin.json                 # 플러그인 매니페스트
├── skills/
│   └── hwp/
│       ├── SKILL.md                # 스킬 정의 (트리거 조건 + 사용 지침)
│       └── scripts/
│           ├── hwp_to_markdown.py  # 통합 CLI (자동 감지 + 일괄 변환)
│           ├── hwp_extract.py      # HWP 바이너리(OLE CFB) 파서
│           └── hwpx_extract.py     # HWPX(ZIP+XML) 파서
├── README.md                       # 이 문서
└── LICENSE                         # MIT
```

---

## 파싱 방식

| 포맷 | 방식 | 비고 |
|---|---|---|
| `.hwp` | UTF-16LE 바이너리 스캔 | OLE CFB 구조, 순수 텍스트 레이어 추출 |
| `.hwpx` | ZIP 압축 해제 → XML 파싱 | section*.xml에서 단락·표 구조 보존 |

**마크다운 자동 구조화:**

| 원본 패턴 | 변환 |
|---|---|
| `1.`, `Ⅰ.` 시작 제목 | `## H2` |
| 짧은 소제목 | `### H3` |
| `ㅇ`, `○` 글머리 | `- 불릿` |
| `*` 주석 | `> 인용` |
| `<제목>` 꺽쇠 | **굵게** |
| 표(tbl/tr/tc) | 마크다운 테이블 |

---

## 지원 플랫폼

| 플랫폼 | 지원 |
|--------|:----:|
| Claude Code CLI | O |
| Claude Code Desktop (Mac/Windows) | O |
| Claude Code Web (claude.ai/code) | O |
| Claude Code IDE Extensions (VS Code, JetBrains) | O |

---

## 한계

HWP/HWPX 포맷 특성상 아래 내용은 추출되지 않을 수 있습니다:

- 이미지·도형 안에 삽입된 텍스트
- 암호화된 문서
- 복잡한 수식(MathML)
- 머리글/바닥글 일부

이 경우 LibreOffice를 통한 변환을 권장합니다:
```bash
libreoffice --headless --convert-to txt:Text 문서.hwpx
```

---

## 관련 프로젝트

- [claude-law-skill](https://github.com/iamupd/claude-law-skill) — 한국 법령 조회·검색·개정 감지 플러그인

---

## 라이선스

![License](https://img.shields.io/badge/License-MIT-green)

MIT
