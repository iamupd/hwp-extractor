#!/usr/bin/env python3
"""
HWP (한컴오피스 5.x, OLE/CFB 바이너리) 텍스트 추출기
- UTF-16LE 인코딩으로 저장된 본문 텍스트 스캔
- 한글, 영문, 숫자, 기호 포함 가독성 기준 필터링
- 중복 블록 제거
"""

import struct
import re
import sys
import os


def extract_text_blocks(data: bytes) -> list[str]:
    """바이너리 데이터에서 UTF-16LE 텍스트 블록 추출"""
    blocks = []
    current = []
    i = 0

    while i < len(data) - 1:
        word = struct.unpack_from('<H', data, i)[0]
        char = chr(word)

        # 허용 문자 범위: 한글, ASCII 출력 가능 문자, 한글 자모, 특수문자 일부
        if (
            0xAC00 <= word <= 0xD7A3 or   # 한글 완성형
            0x3131 <= word <= 0x318E or   # 한글 자모
            0x0020 <= word <= 0x007E or   # ASCII (공백~물결)
            word in (0x00B7, 0x2019, 0x2018, 0x201C, 0x201D,  # 중점, 따옴표
                     0x2022, 0x25A0, 0x25CF, 0x2665,           # 불릿 기호
                     0x3000, 0x3001, 0x3002,                    # 전각 문장부호
                     0xFF01, 0xFF08, 0xFF09, 0xFF1A,            # 전각 ASCII
                     0x0028, 0x0029, 0x002E, 0x003A, 0x002C,   # 괄호/점/콜론
                     )
        ):
            current.append(char)
        else:
            if len(current) > 4:
                blocks.append(''.join(current).strip())
            current = []
        i += 2

    if len(current) > 4:
        blocks.append(''.join(current).strip())

    return blocks


def is_readable(text: str, threshold: float = 0.6) -> bool:
    """
    가독성 비율 기준 필터 (한글+ASCII 비율)
    + 짧은 순수 한글 블록 중 의미 없는 바이너리 잔여물 제거
    """
    if not text:
        return False

    # 비율 기준
    readable = sum(
        1 for c in text
        if '\uAC00' <= c <= '\uD7A3' or c.isascii()
    )
    if (readable / len(text)) < threshold:
        return False

    # 짧은 순수 한글 블록 (공백·ASCII 없음) → 바이너리 잔여물 가능성 높음
    # 단, 5자 미만은 일반 단어일 수 있으므로 허용
    if len(text) >= 4:
        is_pure_hangul = all('\uAC00' <= c <= '\uD7A3' for c in text)
        if is_pure_hangul:
            # 일반적인 한국어 조사/어미가 없으면 잔여물로 판단
            common_endings = ('이', '가', '은', '는', '을', '를', '의', '에', '로', '와', '과',
                              '도', '만', '서', '다', '고', '며', '나', '니', '요', '야')
            has_ending = any(text.endswith(e) for e in common_endings)
            # 5자 이상 순수한글 + 조사/어미 없음 → 바이너리 잔여물로 판단
            if len(text) >= 5 and not has_ending:
                return False

    return True


def deduplicate(blocks: list[str]) -> list[str]:
    """동일 블록 중복 제거 (순서 유지)"""
    seen = set()
    result = []
    for b in blocks:
        if b not in seen:
            seen.add(b)
            result.append(b)
    return result


def blocks_to_markdown(blocks: list[str]) -> str:
    """추출된 텍스트 블록을 마크다운 구조로 변환"""
    lines = []
    for block in blocks:
        b = block.strip()
        if not b:
            continue

        # 날짜 패턴 제거 (HWP 메타 잔여물)
        if re.match(r'^\d{4}년 \d+월 \d+일', b):
            continue

        # 제목 감지: 숫자. 또는 로마자 + 공백
        if re.match(r'^[1-9Ⅰ-Ⅸ]\. .+', b) and len(b) < 60:
            lines.append(f'\n## {b}\n')
        # 소제목: 짧은 한글 단어
        elif len(b) < 25 and re.match(r'^[가-힣a-zA-Z\s]+$', b):
            lines.append(f'\n### {b}\n')
        # 글머리 기호 (ㅇ, ○)
        elif b.startswith('ㅇ ') or b.startswith('○ '):
            lines.append(f'- {b[2:].strip()}')
        # 주석 (* 로 시작)
        elif b.startswith('* ') or b.startswith('** '):
            lines.append(f'  > {b}')
        # 꺽쇠 제목
        elif b.startswith('<') and b.endswith('>') and len(b) < 80:
            lines.append(f'\n**{b[1:-1].strip()}**\n')
        else:
            lines.append(b)

    return '\n'.join(lines)


def extract_hwp(hwp_path: str) -> str:
    """HWP 파일에서 마크다운 텍스트 추출 (메인 함수)"""
    if not os.path.exists(hwp_path):
        raise FileNotFoundError(f"파일 없음: {hwp_path}")

    with open(hwp_path, 'rb') as f:
        data = f.read()

    # OLE CFB 시그니처 확인
    ole_sig = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
    if data[:8] != ole_sig:
        raise ValueError("HWP OLE 포맷이 아닙니다. HWPX 파일이라면 hwpx_extract.py를 사용하세요.")

    blocks = extract_text_blocks(data)
    readable_blocks = [b for b in blocks if is_readable(b) and b.strip()]
    unique_blocks = deduplicate(readable_blocks)

    # 한글 포함된 블록만 최종 선별 + 반복 패턴(RICS 텍스트 2회 이상 중복) 최소화
    korean_blocks = [
        b for b in unique_blocks
        if any('\uAC00' <= c <= '\uD7A3' for c in b)
    ]

    # 날짜 메타 패턴 제거
    korean_blocks = [
        b for b in korean_blocks
        if not re.match(r'^\d{4}년 \d+월 \d+일', b)
    ]

    if not korean_blocks:
        return "_텍스트를 추출할 수 없습니다. 문서가 이미지 기반이거나 암호화되어 있을 수 있습니다._"

    return blocks_to_markdown(korean_blocks)


def main():
    if len(sys.argv) < 2:
        print("사용법: python hwp_extract.py <파일.hwp> [출력.md]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        markdown = extract_hwp(input_path)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✓ 저장 완료: {output_path}")
        else:
            print(markdown)

    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
