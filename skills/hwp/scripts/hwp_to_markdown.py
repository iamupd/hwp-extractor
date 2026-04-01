#!/usr/bin/env python3
"""
HWP/HWPX → Markdown 통합 변환 CLI
- 파일 확장자에 따라 hwp_extract.py 또는 hwpx_extract.py 자동 선택
- 단일 파일 또는 디렉토리 일괄 변환 지원
- 출력: 마크다운 텍스트 (stdout 또는 .md 파일)

사용법:
  python hwp_to_markdown.py <파일.hwp|hwpx>            # stdout 출력
  python hwp_to_markdown.py <파일.hwp|hwpx> -o out.md  # 파일 저장
  python hwp_to_markdown.py <디렉토리>                  # 일괄 변환
"""

import sys
import os
import argparse
from pathlib import Path

# 같은 scripts/ 디렉토리의 모듈 import
sys.path.insert(0, os.path.dirname(__file__))
from hwp_extract import extract_hwp
from hwpx_extract import extract_hwpx


def convert_file(input_path: str, output_path: str = None, title: str = None) -> str:
    """
    HWP 또는 HWPX 파일을 마크다운으로 변환

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 .md 파일 경로 (None이면 내용 반환)
        title: 마크다운 H1 제목 (None이면 파일명 사용)

    Returns:
        변환된 마크다운 문자열
    """
    path = Path(input_path)
    ext = path.suffix.lower()

    if ext == '.hwp':
        body = extract_hwp(str(path))
    elif ext in ('.hwpx', '.hml'):
        body = extract_hwpx(str(path))
    else:
        raise ValueError(f"지원하지 않는 형식: {ext} (지원: .hwp, .hwpx, .hml)")

    # 제목 설정
    doc_title = title or path.stem
    markdown = f"# {doc_title}\n\n> 출처: {path.name}\n\n---\n\n{body}"

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"✓ {path.name} → {output_path}")

    return markdown


def convert_directory(dir_path: str, output_dir: str = None) -> list[str]:
    """
    디렉토리 내 모든 HWP/HWPX 파일 일괄 변환

    Returns:
        변환된 출력 파일 경로 리스트
    """
    dir_p = Path(dir_path)
    out_dir = Path(output_dir) if output_dir else dir_p / 'markdown'
    out_dir.mkdir(exist_ok=True)

    converted = []
    extensions = ('.hwp', '.hwpx', '.hml')

    for file_path in sorted(dir_p.iterdir()):
        if file_path.suffix.lower() not in extensions:
            continue

        out_path = out_dir / (file_path.stem + '.md')
        try:
            convert_file(str(file_path), str(out_path))
            converted.append(str(out_path))
        except Exception as e:
            print(f"✗ {file_path.name}: {e}", file=sys.stderr)

    print(f"\n총 {len(converted)}개 파일 변환 완료 → {out_dir}")
    return converted


def main():
    parser = argparse.ArgumentParser(
        description='HWP/HWPX 파일을 마크다운으로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input', help='입력 파일 또는 디렉토리')
    parser.add_argument('-o', '--output', help='출력 파일 경로 (.md)', default=None)
    parser.add_argument('--title', help='마크다운 H1 제목', default=None)
    parser.add_argument('--outdir', help='일괄 변환 시 출력 디렉토리', default=None)

    args = parser.parse_args()

    input_p = Path(args.input)

    if input_p.is_dir():
        convert_directory(str(input_p), args.outdir)
    elif input_p.is_file():
        result = convert_file(str(input_p), args.output, args.title)
        if not args.output:
            print(result)
    else:
        print(f"오류: 경로를 찾을 수 없음: {args.input}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
