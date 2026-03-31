#!/usr/bin/env python3
"""
HWPX (한컴오피스 XML 기반) 텍스트 추출기
- HWPX는 ZIP 아카이브 내 XML 파일로 구성됨
- Contents/section*.xml 에서 단락(p) 및 텍스트(t) 추출
- 표(tbl), 행(tr), 셀(tc) 구조 보존
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import sys
import os
from typing import Optional


def get_tag(elem) -> str:
    """네임스페이스 제거한 태그명 반환"""
    tag = elem.tag
    return tag.split('}')[-1] if '}' in tag else tag


def extract_cell_text(tc_elem) -> str:
    """테이블 셀(tc)에서 텍스트 추출"""
    texts = []
    for elem in tc_elem.iter():
        if get_tag(elem) == 't' and elem.text:
            texts.append(elem.text)
    return ' '.join(texts).strip()


def extract_section_text(root) -> list[dict]:
    """
    섹션 XML 루트에서 단락 및 표 구조 추출
    반환: [{'type': 'paragraph'|'table', 'content': str|list}]
    """
    items = []

    for elem in root:
        tag = get_tag(elem)

        if tag == 'p':  # 단락
            texts = []
            for child in elem.iter():
                if get_tag(child) == 't' and child.text:
                    texts.append(child.text)
            line = ''.join(texts).strip()
            if line:
                items.append({'type': 'paragraph', 'content': line})

        elif tag == 'tbl':  # 표
            table_rows = []
            for tr in elem:
                if get_tag(tr) != 'tr':
                    continue
                row = []
                for tc in tr:
                    if get_tag(tc) != 'tc':
                        continue
                    cell_text = extract_cell_text(tc)
                    row.append(cell_text)
                if any(c.strip() for c in row):
                    table_rows.append(row)

            if table_rows:
                items.append({'type': 'table', 'content': table_rows})

        # 중첩된 섹션 처리 (재귀적으로 하위 p 탐색)
        else:
            for sub_p in elem.iter():
                if get_tag(sub_p) == 'p':
                    texts = []
                    for child in sub_p.iter():
                        if get_tag(child) == 't' and child.text:
                            texts.append(child.text)
                    line = ''.join(texts).strip()
                    if line:
                        items.append({'type': 'paragraph', 'content': line})
                elif get_tag(sub_p) == 'tbl':
                    # 재귀 탐색 중 tbl 처리
                    pass  # 최상위 tbl만 처리

    return items


def items_to_markdown(items: list[dict]) -> str:
    """구조화된 항목을 마크다운으로 변환"""
    lines = []

    for item in items:
        if item['type'] == 'paragraph':
            content = item['content']

            # 제목 감지
            if re.match(r'^[1-9Ⅰ-Ⅸ]\. .+', content) and len(content) < 60:
                lines.append(f'\n## {content}\n')
            elif len(content) < 25 and re.match(r'^[가-힣a-zA-Z\s·\-]+$', content):
                lines.append(f'\n### {content}\n')
            elif content.startswith('ㅇ ') or content.startswith('○ '):
                lines.append(f'- {content[2:].strip()}')
            elif content.startswith('* ') or content.startswith('** '):
                lines.append(f'  > {content}')
            elif content.startswith('<') and content.endswith('>') and len(content) < 80:
                lines.append(f'\n**{content[1:-1].strip()}**\n')
            else:
                lines.append(content)

        elif item['type'] == 'table':
            rows = item['content']
            if not rows:
                continue

            lines.append('')  # 테이블 앞 공백 줄

            # 헤더 행
            header = rows[0]
            lines.append('| ' + ' | '.join(header) + ' |')
            lines.append('|' + ' --- |' * len(header))

            # 데이터 행
            for row in rows[1:]:
                # 열 수 맞추기
                while len(row) < len(header):
                    row.append('')
                lines.append('| ' + ' | '.join(row) + ' |')

            lines.append('')  # 테이블 뒤 공백 줄

    return '\n'.join(lines)


def extract_hwpx(hwpx_path: str) -> str:
    """HWPX 파일에서 마크다운 텍스트 추출 (메인 함수)"""
    if not os.path.exists(hwpx_path):
        raise FileNotFoundError(f"파일 없음: {hwpx_path}")

    try:
        with zipfile.ZipFile(hwpx_path, 'r') as zf:
            file_list = zf.namelist()
    except zipfile.BadZipFile:
        raise ValueError("HWPX ZIP 포맷이 아닙니다. .hwp 파일이라면 hwp_extract.py를 사용하세요.")

    all_items = []

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        sections = sorted([
            n for n in file_list
            if re.match(r'Contents/section\d+\.xml', n)
        ])

        if not sections:
            # 섹션이 없으면 PrvText.txt (미리보기 텍스트) 시도
            if 'Preview/PrvText.txt' in file_list:
                with zf.open('Preview/PrvText.txt') as f:
                    raw = f.read()
                    try:
                        text = raw.decode('utf-8')
                    except UnicodeDecodeError:
                        text = raw.decode('utf-16-le', errors='replace')
                return text

        for section_name in sections:
            with zf.open(section_name) as f:
                content = f.read()

            root = ET.fromstring(content)
            items = extract_section_text(root)
            all_items.extend(items)

    if not all_items:
        return "_텍스트를 추출할 수 없습니다. 문서가 이미지 기반일 수 있습니다._"

    return items_to_markdown(all_items)


def main():
    if len(sys.argv) < 2:
        print("사용법: python hwpx_extract.py <파일.hwpx> [출력.md]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        markdown = extract_hwpx(input_path)

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
