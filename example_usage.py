"""
특허 검색 시스템 간단한 사용 예제
"""

from patent_search.models.patent import Patent, Inventor, Applicant, Classification
from patent_search.query.query_builder import QueryBuilder
from patent_search.analysis.prior_art import PriorArtAnalyzer
from patent_search.storage.database import PatentDatabase
from patent_search.storage.file_storage import FileStorage

print("=" * 80)
print("특허 검색 시스템 테스트")
print("=" * 80)

# 1. 특허 객체 생성
print("\n[1] 특허 객체 생성")
patent1 = Patent(
    id="TEST001",
    title="인공지능 기반 이미지 인식 시스템",
    application_number="10-2023-0001234",
    application_date="2023-01-15",
    abstract="본 발명은 딥러닝 기술을 활용하여 이미지를 자동으로 인식하고 분류하는 시스템에 관한 것이다.",
    country="KR",
    status="granted"
)

patent1.add_inventor("홍길동", "KR")
patent1.add_inventor("김철수", "KR")
patent1.add_applicant("테크놀로지 주식회사", "KR", "company")
patent1.classifications = Classification(ipc=["G06N3/08", "G06T7/00"])

print(f"특허 제목: {patent1.title}")
print(f"출원번호: {patent1.application_number}")
print(f"발명자: {', '.join([i.name for i in patent1.inventors])}")
print(f"IPC: {', '.join(patent1.get_ipc_codes())}")

# 2. 두 번째 특허 생성
print("\n[2] 두 번째 특허 객체 생성")
patent2 = Patent(
    id="TEST002",
    title="머신러닝을 이용한 이미지 분석 방법",
    application_number="10-2023-0005678",
    application_date="2023-02-20",
    abstract="본 발명은 머신러닝 알고리즘을 사용하여 이미지를 효율적으로 분석하는 방법에 관한 것이다.",
    country="KR",
    status="pending"
)

patent2.add_inventor("이영희", "KR")
patent2.add_applicant("AI 연구소", "KR", "university")
patent2.classifications = Classification(ipc=["G06N3/08", "G06T1/00"])

print(f"특허 제목: {patent2.title}")
print(f"출원번호: {patent2.application_number}")

# 3. 특허 비교 분석
print("\n[3] 특허 유사도 분석")
analyzer = PriorArtAnalyzer()
comparison = analyzer.compare_patents(patent1, patent2)

print(f"전체 유사도: {comparison.similarity.overall}%")
print(f"제목 유사도: {comparison.similarity.title}%")
print(f"초록 유사도: {comparison.similarity.abstract}%")
print(f"IPC 유사도: {comparison.similarity.ipc}%")

if comparison.common_keywords:
    print(f"공통 키워드: {', '.join(comparison.common_keywords[:5])}")

# 4. 쿼리 빌더 사용
print("\n[4] 검색 쿼리 생성")
query = QueryBuilder() \
    .keyword("인공지능") \
    .applicant("삼성전자") \
    .application_date_range("2020-01-01", "2023-12-31") \
    .country("KR") \
    .build()

print(f"생성된 쿼리: {query}")

# 5. 데이터베이스 저장
print("\n[5] 데이터베이스에 저장")
db = PatentDatabase("data/test_patents.db")
db.save_patent(patent1)
db.save_patent(patent2)
print("✓ 2건의 특허가 저장되었습니다.")

# 데이터베이스에서 검색
saved_patents = db.search_patents(country="KR")
print(f"✓ 저장된 특허 {len(saved_patents)}건을 조회했습니다.")

db.close()

# 6. 파일로 내보내기
print("\n[6] 파일로 내보내기")
storage = FileStorage("data/exports")

# CSV 저장
csv_file = storage.save_patents_csv([patent1, patent2], "test_patents.csv")
print(f"✓ CSV 파일 저장: {csv_file}")

# JSON 저장
from patent_search.models.search_result import SearchResult, SearchMetadata

metadata = SearchMetadata(
    query=query,
    total_results=2,
    retrieved_count=2,
    search_time=0.5,
    source="TEST"
)
search_result = SearchResult(metadata=metadata, patents=[patent1, patent2])
json_file = storage.save_search_result_json(search_result, "test_result.json")
print(f"✓ JSON 파일 저장: {json_file}")

print("\n" + "=" * 80)
print("테스트 완료!")
print("=" * 80)
