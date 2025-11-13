"""
특허 검색 CLI 메인 인터페이스
Patent Search CLI Main Interface
"""

import click
import json
import time
from pathlib import Path
from typing import Optional

from ..api.kipris import KiprisAPI
from ..api.google_patents import GooglePatentsAPI
from ..query.query_builder import QueryBuilder, AdvancedQueryBuilder
from ..models.patent import Patent
from ..models.search_result import SearchResult, SearchMetadata
from ..storage.database import PatentDatabase
from ..storage.file_storage import FileStorage
from ..analysis.prior_art import PriorArtAnalyzer


def load_config(config_path: str = "config/config.json") -> dict:
    """설정 파일 로드"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"설정 파일을 찾을 수 없습니다: {config_path}")
        return {}
    except json.JSONDecodeError:
        click.echo(f"설정 파일 형식이 잘못되었습니다: {config_path}")
        return {}


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """특허 검색 및 선행기술 조사 시스템"""
    pass


@cli.command()
@click.option('--keyword', '-k', help='검색 키워드')
@click.option('--applicant', '-a', help='출원인명')
@click.option('--inventor', '-i', help='발명자명')
@click.option('--ipc', help='IPC 분류 코드')
@click.option('--source', '-s',
              type=click.Choice(['kipris', 'google'], case_sensitive=False),
              default='kipris',
              help='검색 소스')
@click.option('--limit', '-l', default=20, help='최대 결과 개수')
@click.option('--save', is_flag=True, help='결과를 데이터베이스에 저장')
@click.option('--export', type=click.Choice(['json', 'csv', 'excel']), help='결과 내보내기 형식')
def search(keyword, applicant, inventor, ipc, source, limit, save, export):
    """특허 검색 수행"""

    click.echo("=" * 80)
    click.echo("특허 검색 시작")
    click.echo("=" * 80)

    # 쿼리 빌더로 검색 조건 구성
    query_builder = QueryBuilder()

    if keyword:
        query_builder.keyword(keyword)
        click.echo(f"키워드: {keyword}")

    if applicant:
        query_builder.applicant(applicant)
        click.echo(f"출원인: {applicant}")

    if inventor:
        query_builder.inventor(inventor)
        click.echo(f"발명자: {inventor}")

    if ipc:
        query_builder.ipc_classification(ipc)
        click.echo(f"IPC: {ipc}")

    query = query_builder.build()

    if not query:
        click.echo("검색 조건을 입력해주세요.")
        return

    # 검색 수행
    config = load_config()
    start_time = time.time()

    try:
        if source.lower() == 'kipris':
            api_key = config.get('api', {}).get('kipris', {}).get('api_key', '')
            if not api_key:
                click.echo("⚠ KIPRIS API 키가 설정되지 않았습니다.")
                click.echo("config/config.json 파일에서 API 키를 설정해주세요.")
                return

            with KiprisAPI(api_key) as api:
                click.echo(f"\n🔍 KIPRIS에서 검색 중...")
                results = api.search(query, limit)

        else:  # google
            with GooglePatentsAPI() as api:
                click.echo(f"\n🔍 Google Patents에서 검색 중...")
                results = api.search(query, limit)

        search_time = time.time() - start_time

        if not results:
            click.echo("\n검색 결과가 없습니다.")
            return

        # SearchResult 객체 생성
        patents = [Patent.from_dict(r) if isinstance(r, dict) else r for r in results]

        metadata = SearchMetadata(
            query=query,
            total_results=len(results),
            retrieved_count=len(results),
            search_time=search_time,
            source=source.upper()
        )

        search_result = SearchResult(metadata=metadata, patents=patents)

        # 결과 출력
        click.echo(f"\n✅ {len(results)}건의 특허를 찾았습니다. (소요 시간: {search_time:.2f}초)")
        click.echo("=" * 80)

        for idx, patent in enumerate(patents[:10], 1):  # 상위 10개만 출력
            click.echo(f"\n[{idx}] {patent.title}")
            click.echo(f"    출원번호: {patent.application_number}")
            click.echo(f"    출원일: {patent.application_date}")
            if patent.abstract:
                abstract = patent.abstract[:100] + "..." if len(patent.abstract) > 100 else patent.abstract
                click.echo(f"    초록: {abstract}")

        if len(patents) > 10:
            click.echo(f"\n... 외 {len(patents) - 10}건")

        # 데이터베이스 저장
        if save:
            db = PatentDatabase()
            db.save_search_result(search_result)
            click.echo(f"\n💾 검색 결과가 데이터베이스에 저장되었습니다. (ID: {search_result.search_id})")
            db.close()

        # 파일 내보내기
        if export:
            storage = FileStorage()

            if export == 'json':
                filepath = storage.save_search_result_json(search_result)
                click.echo(f"\n📄 JSON 파일로 저장: {filepath}")

            elif export == 'csv':
                filepath = storage.save_patents_csv(patents)
                click.echo(f"\n📄 CSV 파일로 저장: {filepath}")

            elif export == 'excel':
                filepath = storage.save_patents_excel(patents)
                click.echo(f"\n📄 Excel 파일로 저장: {filepath}")

    except Exception as e:
        click.echo(f"\n❌ 검색 중 오류 발생: {str(e)}")


@cli.command()
@click.argument('patent_id')
@click.option('--source', '-s',
              type=click.Choice(['kipris', 'google'], case_sensitive=False),
              default='kipris',
              help='검색 소스')
@click.option('--save', is_flag=True, help='결과를 데이터베이스에 저장')
def detail(patent_id, source, save):
    """특허 상세 정보 조회"""

    click.echo(f"특허 상세 정보 조회: {patent_id}")

    config = load_config()

    try:
        if source.lower() == 'kipris':
            api_key = config.get('api', {}).get('kipris', {}).get('api_key', '')
            if not api_key:
                click.echo("⚠ KIPRIS API 키가 설정되지 않았습니다.")
                return

            with KiprisAPI(api_key) as api:
                patent_data = api.get_patent_detail(patent_id)

        else:  # google
            with GooglePatentsAPI() as api:
                patent_data = api.get_patent_detail(patent_id)

        if not patent_data:
            click.echo("특허 정보를 찾을 수 없습니다.")
            return

        # Patent 객체 생성
        patent = Patent.from_dict(patent_data) if isinstance(patent_data, dict) else patent_data

        # 상세 정보 출력
        click.echo("=" * 80)
        click.echo(f"제목: {patent.title}")
        click.echo("=" * 80)
        click.echo(f"출원번호: {patent.application_number}")
        click.echo(f"출원일: {patent.application_date}")

        if patent.registration_number:
            click.echo(f"등록번호: {patent.registration_number}")
        if patent.registration_date:
            click.echo(f"등록일: {patent.registration_date}")

        click.echo(f"상태: {patent.status or 'N/A'}")
        click.echo(f"국가: {patent.country or 'N/A'}")

        if patent.applicants:
            applicants = ', '.join([a.name for a in patent.applicants])
            click.echo(f"출원인: {applicants}")

        if patent.inventors:
            inventors = ', '.join([i.name for i in patent.inventors])
            click.echo(f"발명자: {inventors}")

        ipc_codes = patent.get_ipc_codes()
        if ipc_codes:
            click.echo(f"IPC: {', '.join(ipc_codes)}")

        if patent.abstract:
            click.echo(f"\n초록:\n{patent.abstract}")

        if patent.url:
            click.echo(f"\nURL: {patent.url}")

        # 저장
        if save:
            db = PatentDatabase()
            db.save_patent(patent)
            click.echo(f"\n💾 특허 정보가 데이터베이스에 저장되었습니다.")
            db.close()

    except Exception as e:
        click.echo(f"❌ 오류 발생: {str(e)}")


@cli.command()
@click.option('--limit', '-l', default=20, help='최대 표시 개수')
def history(limit):
    """검색 이력 조회"""

    click.echo("검색 이력")
    click.echo("=" * 80)

    try:
        db = PatentDatabase()
        search_history = db.get_search_history(limit)

        if not search_history:
            click.echo("검색 이력이 없습니다.")
            return

        for idx, record in enumerate(search_history, 1):
            click.echo(f"\n[{idx}] {record['search_id']}")
            click.echo(f"    소스: {record['source']}")
            click.echo(f"    검색 조건: {record['query']}")
            click.echo(f"    결과: {record['retrieved_count']}건")
            click.echo(f"    시간: {record['timestamp']}")

        db.close()

    except Exception as e:
        click.echo(f"❌ 오류 발생: {str(e)}")


@cli.command()
@click.argument('patent_id1')
@click.argument('patent_id2')
def compare(patent_id1, patent_id2):
    """두 특허 비교"""

    click.echo(f"특허 비교: {patent_id1} vs {patent_id2}")

    try:
        db = PatentDatabase()

        patent1 = db.get_patent(patent_id1)
        patent2 = db.get_patent(patent_id2)

        if not patent1:
            click.echo(f"특허를 찾을 수 없습니다: {patent_id1}")
            return

        if not patent2:
            click.echo(f"특허를 찾을 수 없습니다: {patent_id2}")
            return

        # 비교 분석
        analyzer = PriorArtAnalyzer()
        comparison = analyzer.compare_patents(patent1, patent2)

        # 리포트 출력
        report = analyzer.generate_comparison_report(comparison)
        click.echo(report)

        db.close()

    except Exception as e:
        click.echo(f"❌ 오류 발생: {str(e)}")


@cli.command()
@click.argument('patent_id')
@click.option('--threshold', '-t', default=30.0, help='최소 유사도 (0-100)')
@click.option('--limit', '-l', default=10, help='최대 결과 개수')
def similar(patent_id, threshold, limit):
    """유사 특허 찾기"""

    click.echo(f"유사 특허 검색: {patent_id}")

    try:
        db = PatentDatabase()

        target_patent = db.get_patent(patent_id)
        if not target_patent:
            click.echo(f"특허를 찾을 수 없습니다: {patent_id}")
            return

        # 모든 특허 조회
        all_patents = db.search_patents()

        if len(all_patents) < 2:
            click.echo("비교할 특허가 충분하지 않습니다.")
            return

        # 유사 특허 찾기
        analyzer = PriorArtAnalyzer()
        similar_patents = analyzer.find_similar_patents(
            target_patent,
            all_patents,
            threshold,
            limit
        )

        if not similar_patents:
            click.echo(f"유사도 {threshold}% 이상인 특허가 없습니다.")
            return

        click.echo("=" * 80)
        click.echo(f"유사 특허 {len(similar_patents)}건")
        click.echo("=" * 80)

        for idx, (patent, similarity) in enumerate(similar_patents, 1):
            click.echo(f"\n[{idx}] 유사도: {similarity}%")
            click.echo(f"    ID: {patent.id}")
            click.echo(f"    제목: {patent.title}")
            click.echo(f"    출원번호: {patent.application_number}")

        db.close()

    except Exception as e:
        click.echo(f"❌ 오류 발생: {str(e)}")


@cli.command()
@click.option('--format', '-f',
              type=click.Choice(['json', 'csv', 'excel'], case_sensitive=False),
              default='csv',
              help='내보내기 형식')
@click.option('--output', '-o', help='출력 파일명')
def export_db(format, output):
    """데이터베이스의 모든 특허 내보내기"""

    click.echo("데이터베이스 내보내기")

    try:
        db = PatentDatabase()
        patents = db.search_patents()

        if not patents:
            click.echo("저장된 특허가 없습니다.")
            return

        storage = FileStorage()

        if format == 'json':
            from ..models.search_result import SearchMetadata, SearchResult
            metadata = SearchMetadata(
                query={},
                total_results=len(patents),
                retrieved_count=len(patents),
                search_time=0,
                source="Database"
            )
            search_result = SearchResult(metadata=metadata, patents=patents)
            filepath = storage.save_search_result_json(search_result, output)

        elif format == 'csv':
            filepath = storage.save_patents_csv(patents, output)

        elif format == 'excel':
            filepath = storage.save_patents_excel(patents, output)

        click.echo(f"✅ {len(patents)}건의 특허를 내보냈습니다: {filepath}")

        db.close()

    except Exception as e:
        click.echo(f"❌ 오류 발생: {str(e)}")


if __name__ == '__main__':
    cli()
