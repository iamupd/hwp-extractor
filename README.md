# hwp-extractor

> Claude Cowork 스킬 — HWP/HWPX 파일을 마크다운으로 변환

한컴오피스 문서 포맷인 `.hwp`(바이너리 OLE)와 `.hwpx`(ZIP+XML)에서 텍스트를 추출하여 마크다운으로 변환하는 Claude 스킬입니다. **별도 라이브러리 설치 없이 표준 Python만 사용합니다.**

---

## 설치

1. [Releases](../../releases) 에서 `hwp-extractor.skill` 다운로드
2. Claude 데스크탑 앱에서 "Save skill" 클릭

또는 이 저장소를 클론하면 스크립트를 직접 사용할 수 있습니다.

---

## 사용법

### Claude 스킬로 사용

Claude에게 자연어로 요청하면 자동으로 스킬이 실행됩니다:

```
"01.검토자료.hwp 마크다운으로 뽑아줘"
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
sys.path.insert(0, 'scripts/')

from hwp_extract import extract_hwp
from hwpx_extract import extract_hwpx

markdown = extract_hwp("문서.hwp")    # HWP 바이너리
markdown = extract_hwpx("문서.hwpx")  # HWPX ZIP+XML
print(markdown)
```

---

## 구조

```
hwp-extractor/
├── SKILL.md                    # Claude 스킬 정의 (트리거 조건 + 사용 지침)
├── scripts/
│   ├── hwp_to_markdown.py      # 통합 CLI (자동 감지 + 일괄 변환)
│   ├── hwp_extract.py          # HWP 바이너리(OLE CFB) 파서
│   └── hwpx_extract.py         # HWPX(ZIP+XML) 파서
└── references/                 # (예비)
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

## 라이선스

MIT
