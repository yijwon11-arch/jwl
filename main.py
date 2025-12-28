#!/usr/bin/env python3
"""
특허 선행기술 조사 시스템 - 메인 프로그램

특허 정보를 입력받아 선행기술을 검색하고 유사도를 분석합니다.
"""

import argparse
import sys
import json
from pathlib import Path

# src 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from patent_parser import PatentParser
from file_parser import FileParser
from search_engine import PriorArtSearchEngine
from similarity_analyzer import SimilarityAnalyzer
from report_generator import ReportGenerator


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='특허 선행기술 조사 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # JSON 파일로 입력
  python main.py --input patent.json

  # 커맨드라인으로 입력
  python main.py --title "인공지능 기반 이미지 처리 방법" --abstract "본 발명은..."

  # 결과를 파일로 저장
  python main.py --input patent.json --output report --format markdown
        """
    )

    # 입력 옵션
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='특허 정보가 담긴 파일 경로 (지원 형식: .json, .txt, .pdf, .docx, .png, .jpg)'
    )
    input_group.add_argument(
        '--title', '-t',
        type=str,
        help='특허 제목'
    )

    # 추가 입력 필드
    parser.add_argument(
        '--abstract', '-a',
        type=str,
        help='특허 초록'
    )
    parser.add_argument(
        '--claims', '-c',
        type=str,
        nargs='+',
        help='특허 청구항 (여러 개 가능)'
    )
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        nargs='+',
        help='키워드 (여러 개 가능)'
    )

    # 검색 옵션
    parser.add_argument(
        '--max-results', '-m',
        type=int,
        default=10,
        help='최대 검색 결과 수 (기본값: 10)'
    )
    parser.add_argument(
        '--language', '-l',
        type=str,
        choices=['ko', 'en', 'any'],
        default='ko',
        help='검색 언어 (기본값: ko)'
    )

    # 출력 옵션
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='출력 파일명 (확장자 제외)'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['console', 'json', 'markdown'],
        default='console',
        help='출력 형식 (기본값: console)'
    )
    parser.add_argument(
        '--top-n', '-n',
        type=int,
        default=10,
        help='리포트에 표시할 결과 수 (기본값: 10)'
    )

    args = parser.parse_args()

    try:
        # 1. 특허 데이터 파싱
        print("특허 데이터를 파싱하는 중...")
        parser_obj = PatentParser()

        if args.input:
            # 파일에서 읽기 (다양한 형식 지원)
            file_parser = FileParser()

            # 파일 형식 자동 감지 및 파싱
            try:
                patent_data = file_parser.parse_file(args.input)
                print(f"✓ 파일 파싱 완료: {args.input}")
            except ImportError as e:
                print(f"경고: {e}")
                print("필요한 라이브러리를 설치하거나 JSON 파일을 사용하세요.")
                sys.exit(1)
            except Exception as e:
                print(f"파일 파싱 오류: {e}")
                sys.exit(1)

            # 키워드가 없으면 자동 추출
            if not patent_data.get('keywords'):
                patent_data = parser_obj.parse(patent_data)
        else:
            # 커맨드라인 인자에서 구성
            patent_data = parser_obj.parse({
                'title': args.title or '',
                'abstract': args.abstract or '',
                'claims': args.claims or [],
                'keywords': args.keywords or []
            })

        # 유효성 검증
        if not parser_obj.validate_patent_data(patent_data):
            print("오류: 유효한 특허 데이터가 아닙니다. 최소한 제목이나 초록이 필요합니다.")
            sys.exit(1)

        print(f"특허 제목: {patent_data['title'][:50]}...")
        print(f"추출된 키워드: {', '.join(patent_data['keywords'][:5])}...")
        print()

        # 2. 검색 쿼리 생성
        search_query = parser_obj.get_search_query(patent_data)
        print(f"검색 쿼리: {search_query}")
        print()

        # 3. 선행기술 검색
        print("선행기술을 검색하는 중...")
        search_engine = PriorArtSearchEngine(max_results=args.max_results)
        search_results = search_engine.search(search_query, language=args.language)

        print(f"검색 결과: {len(search_results)}건 발견")
        print()

        if not search_results:
            print("검색 결과가 없습니다.")
            sys.exit(0)

        # 4. 유사도 분석
        print("유사도를 분석하는 중...")
        analyzer = SimilarityAnalyzer(language=args.language)
        analyzed_results = analyzer.analyze(patent_data, search_results)

        print("유사도 분석 완료")
        print()

        # 5. 리포트 생성
        print("리포트를 생성하는 중...")
        report_gen = ReportGenerator()

        if args.format == 'console':
            report = report_gen.generate_console_report(
                patent_data,
                analyzed_results,
                top_n=args.top_n
            )
            print(report)

        elif args.format == 'json':
            report = report_gen.generate_json_report(
                patent_data,
                analyzed_results
            )
            if args.output:
                report_gen.save_report(report, args.output, 'json')
            else:
                print(report)

        elif args.format == 'markdown':
            report = report_gen.generate_markdown_report(
                patent_data,
                analyzed_results,
                top_n=args.top_n
            )
            if args.output:
                report_gen.save_report(report, args.output, 'md')
            else:
                print(report)

        # 요약 정보 출력
        print()
        summary = report_gen.generate_summary(analyzed_results)
        print("[ 요약 ]")
        print(f"총 발견 특허: {summary['total']}건")
        print(f"고유사도 (>70%): {summary['high_similarity']}건")
        print(f"중간유사도 (40-70%): {summary['medium_similarity']}건")
        print(f"저유사도 (<40%): {summary['low_similarity']}건")
        print(f"평균 유사도: {summary['average_similarity'] * 100:.2f}%")

    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다 - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파싱 실패 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
