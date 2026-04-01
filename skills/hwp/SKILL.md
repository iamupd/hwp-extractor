---
name: hwp
description: >
  HWP 및 HWPX 파일(한컴오피스 문서)에서 텍스트를 추출해 마크다운으로 변환하는 스킬.
  사용자가 .hwp 또는 .hwpx 파일을 언급하거나, 한컴 문서를 읽거나 변환하거나 내용을 뽑아달라고
  할 때 반드시 이 스킬을 사용할 것. "hwp 열어줘", "hwpx 마크다운으로", "한글 파일 내용 추출",
  "hwp 텍스트 뽑아줘", 디렉토리 내 문서 일괄 변환 요청 등이 모두 해당됨.
  단일 파일 및 폴더 내 일괄 변환 모두 지원.
argument-hint: "<파일경로 또는 디렉토리> [-o 출력파일]"
allowed-tools: "Bash(python *), Bash(python3 *), Read, Write, Glob"
---

# HWP / HWPX 텍스트 추출 스킬

## 개요

이 스킬은 한컴오피스 문서 포맷인 `.hwp`(바이너리 OLE)와 `.hwpx`(ZIP + XML)에서 텍스트를 추출하여 마크다운으로 변환합니다. 표준 Python만 사용하며 별도 라이브러리 설치가 필요 없습니다.

---

## 스크립트 위치

이 스킬 디렉토리의 `scripts/` 폴더에 세 개의 스크립트가 있습니다:

| 파일 | 용도 |
|---|---|
| `hwp_to_markdown.py` | **메인 CLI** — HWP/HWPX 자동 감지, 단일/일괄 변환 |
| `hwp_extract.py` | HWP 바이너리(OLE CFB) 파싱 모듈 |
| `hwpx_extract.py` | HWPX(ZIP+XML) 파싱 모듈 |

---

## 작업 흐름

### 1단계: 파일 형식 판별

| 조건 | 처리 방법 |
|---|---|
| `.hwp` 파일 | `hwp_extract.py` — UTF-16LE 바이너리 스캔 |
| `.hwpx` 파일 | `hwpx_extract.py` — ZIP 압축 해제 후 XML 파싱 |
| 디렉토리 | 내부의 모든 `.hwp` / `.hwpx` 파일 일괄 처리 |

### 2단계: 스크립트 실행

**단일 파일 변환 (stdout 출력):**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/hwp_to_markdown.py "파일.hwp"
```

**단일 파일 → .md 저장:**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/hwp_to_markdown.py "파일.hwp" -o "출력.md"
```

**디렉토리 일괄 변환 (자동으로 markdown/ 서브폴더 생성):**
```bash
python ${CLAUDE_SKILL_DIR}/scripts/hwp_to_markdown.py "/경로/폴더/"
```

### 3단계: 결과 조합

스크립트가 반환한 마크다운에 다음을 추가하여 최종 문서 완성:
- `# 제목` (파일명 또는 사용자 지정)
- `> 출처: 파일명` (원본 파일 정보)
- `> 작성일 / 부서` (문서 내 메타정보 발견 시)

---

## 출력 마크다운 구조

추출된 텍스트는 아래 규칙에 따라 자동 구조화됩니다:

| 원본 패턴 | 변환 결과 |
|---|---|
| `1. 제목`, `Ⅰ. 제목` | `## 제목` (H2) |
| 짧은 소제목 (25자 이하 한글) | `### 소제목` (H3) |
| `ㅇ 내용`, `○ 내용` | `- 내용` (불릿 리스트) |
| `* 주석`, `** 주석` | `> 주석` (인용) |
| `<제목>` 꺽쇠 형태 | **굵은 제목** |
| 표 (tr/tc) | `\| 셀1 \| 셀2 \|` 마크다운 표 |
| 그 외 단락 | 그대로 단락 텍스트 |

---

## 한계 및 주의사항

HWP/HWPX 포맷의 특성상 다음 내용은 추출되지 않을 수 있습니다:

- **이미지/그림** 안에 삽입된 텍스트
- **그리기 개체**(도형, 말풍선) 내부 텍스트
- **암호화된** 문서
- 복잡한 **수식** (MathML 형태)
- **머리글/바닥글** 일부

이러한 경우 사용자에게 안내하고, 가능하다면 LibreOffice를 통한 변환을 제안하세요:
```bash
libreoffice --headless --convert-to txt:Text 파일.hwpx
```

---

## 코드에서 직접 사용하기

Python 코드에서 임포트하여 사용할 수도 있습니다:

```python
import sys
sys.path.insert(0, '${CLAUDE_SKILL_DIR}/scripts')

from hwp_extract import extract_hwp
from hwpx_extract import extract_hwpx

# HWP
markdown = extract_hwp("문서.hwp")

# HWPX
markdown = extract_hwpx("문서.hwpx")

print(markdown)
```

---

## 예시 출력

**입력:** `RICS 개선방향.hwp`

**출력 (마크다운):**
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
