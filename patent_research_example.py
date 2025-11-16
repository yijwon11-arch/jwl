"""
실제 특허 조사 예제
- 특정 기술 분야의 특허를 수동으로 입력하고 분석
"""

from patent_search.models.patent import Patent, Classification
from patent_search.analysis.prior_art import PriorArtAnalyzer
from patent_search.storage.database import PatentDatabase
from patent_search.storage.file_storage import FileStorage

print("=" * 80)
print("특허 선행기술 조사 시작")
print("=" * 80)

# 1. 조사할 특허들을 입력 (KIPRIS나 Google Patents에서 정보를 복사해서 입력)
print("\n[1] 특허 데이터 입력")

# 예: 블록체인 관련 특허들
patents = [
    Patent(
        id="KR-2020-0001",
        title="블록체인 기반 전자 투표 시스템",
        application_number="10-2020-0100001",
        application_date="2020-08-10",
        abstract="블록체인 기술을 이용하여 투표의 무결성과 익명성을 보장하는 전자 투표 시스템",
        country="KR",
        status="granted"
    ),

    Patent(
        id="KR-2020-0002",
        title="분산 원장 기술을 활용한 투표 관리 방법",
        application_number="10-2020-0100002",
        application_date="2020-09-15",
        abstract="분산 원장 기술을 활용하여 투표 데이터를 안전하게 관리하는 방법",
        country="KR",
        status="pending"
    ),

    Patent(
        id="KR-2021-0001",
        title="블록체인 네트워크를 이용한 온라인 투표 시스템",
        application_number="10-2021-0100001",
        application_date="2021-03-20",
        abstract="블록체인 네트워크를 통해 온라인 투표의 신뢰성을 확보하는 시스템",
        country="KR",
        status="granted"
    ),

    Patent(
        id="US-2020-0001",
        title="Blockchain-based Secure Voting System",
        application_number="US16/900,001",
        application_date="2020-10-05",
        abstract="A secure voting system utilizing blockchain technology for vote integrity",
        country="US",
        status="granted"
    ),

    Patent(
        id="KR-2021-0002",
        title="암호화폐 기반 보상 시스템을 갖는 전자 투표 플랫폼",
        application_number="10-2021-0200001",
        application_date="2021-07-10",
        abstract="투표 참여자에게 암호화폐로 보상을 제공하는 블록체인 기반 전자 투표 플랫폼",
        country="KR",
        status="pending"
    )
]

# IPC 분류 추가 (실제 특허에서 확인한 정보 입력)
patents[0].classifications = Classification(ipc=["G06Q50/26", "H04L9/32"])
patents[1].classifications = Classification(ipc=["G06Q50/26", "G06F21/64"])
patents[2].classifications = Classification(ipc=["G06Q50/26", "H04L9/32"])
patents[3].classifications = Classification(ipc=["G06Q50/26", "H04L9/32"])
patents[4].classifications = Classification(ipc=["G06Q50/26", "G06Q20/38"])

# 출원인 정보 추가
patents[0].add_applicant("한국전자투표기술(주)", "KR", "company")
patents[1].add_applicant("서울대학교 산학협력단", "KR", "university")
patents[2].add_applicant("블록체인투표 주식회사", "KR", "company")
patents[3].add_applicant("SecureVote Inc.", "US", "company")
patents[4].add_applicant("크립토보팅 주식회사", "KR", "company")

print(f"✓ {len(patents)}건의 특허 데이터 입력 완료")

# 2. 데이터베이스에 저장
print("\n[2] 데이터베이스 저장")
db = PatentDatabase("data/research_patents.db")
for patent in patents:
    db.save_patent(patent)
print(f"✓ {len(patents)}건 저장 완료")

# 3. 특허군 분석
print("\n[3] 특허군 전체 분석")
analyzer = PriorArtAnalyzer()
analysis = analyzer.analyze_patent_family(patents)

print(f"\n총 특허 수: {analysis['total_patents']}건")
print(f"\n주요 키워드:")
for keyword, count in analysis['top_keywords'][:10]:
    print(f"  - {keyword}: {count}회")

print(f"\n주요 IPC 분류:")
for ipc, count in analysis['top_ipc_classes']:
    print(f"  - {ipc}: {count}건")

print(f"\n주요 출원인:")
for applicant, count in analysis['top_applicants']:
    print(f"  - {applicant}: {count}건")

print(f"\n국가별 분포:")
for country, count in analysis['countries']:
    print(f"  - {country}: {count}건")

# 4. 특정 특허와 다른 특허들의 유사도 비교
print("\n" + "=" * 80)
print("[4] 선행기술 유사도 분석")
print("=" * 80)

target_patent = patents[0]  # 첫 번째 특허를 기준으로
print(f"\n기준 특허: {target_patent.title}")
print(f"출원번호: {target_patent.application_number}\n")

similar_patents = analyzer.find_similar_patents(
    target_patent,
    patents[1:],  # 나머지 특허들과 비교
    threshold=10.0,  # 낮은 임계값으로 모두 표시
    limit=10
)

print(f"유사 특허 {len(similar_patents)}건 발견:\n")
for idx, (patent, similarity) in enumerate(similar_patents, 1):
    print(f"[{idx}] 유사도: {similarity:.1f}%")
    print(f"    제목: {patent.title}")
    print(f"    출원번호: {patent.application_number}")
    print(f"    출원일: {patent.application_date}")
    print()

# 5. 상세 비교 (가장 유사한 특허와 비교)
if similar_patents:
    print("=" * 80)
    print("[5] 가장 유사한 특허와 상세 비교")
    print("=" * 80)

    most_similar = similar_patents[0][0]
    comparison = analyzer.compare_patents(target_patent, most_similar)

    report = analyzer.generate_comparison_report(comparison)
    print(report)

# 6. 결과 파일로 저장
print("\n" + "=" * 80)
print("[6] 분석 결과 저장")
print("=" * 80)

storage = FileStorage("data/exports")

# CSV로 저장
csv_file = storage.save_patents_csv(patents, "blockchain_voting_patents.csv")
print(f"✓ CSV 저장: {csv_file}")

# Excel로 저장
try:
    excel_file = storage.save_patents_excel(patents, "blockchain_voting_patents.xlsx")
    print(f"✓ Excel 저장: {excel_file}")
except Exception as e:
    print(f"  Excel 저장 실패: {e}")

# 7. 분석 결과 요약 텍스트 저장
summary_file = "data/exports/analysis_summary.txt"
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("블록체인 투표 시스템 특허 분석 보고서\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"분석 일자: 2025-11-16\n")
    f.write(f"분석 특허 수: {len(patents)}건\n\n")

    f.write("1. 주요 키워드\n")
    for keyword, count in analysis['top_keywords'][:15]:
        f.write(f"   - {keyword}: {count}회\n")

    f.write("\n2. IPC 분류 분포\n")
    for ipc, count in analysis['top_ipc_classes']:
        f.write(f"   - {ipc}: {count}건\n")

    f.write("\n3. 주요 출원인\n")
    for applicant, count in analysis['top_applicants']:
        f.write(f"   - {applicant}: {count}건\n")

    f.write("\n4. 국가별 분포\n")
    for country, count in analysis['countries']:
        f.write(f"   - {country}: {count}건\n")

    f.write("\n5. 선행기술 유사도 분석\n")
    f.write(f"   기준 특허: {target_patent.title}\n\n")
    for idx, (patent, similarity) in enumerate(similar_patents, 1):
        f.write(f"   [{idx}] {similarity:.1f}% - {patent.title}\n")

print(f"✓ 분석 요약 저장: {summary_file}")

db.close()

print("\n" + "=" * 80)
print("특허 조사 완료!")
print("=" * 80)
print("\n생성된 파일:")
print(f"  - 데이터베이스: data/research_patents.db")
print(f"  - CSV 파일: {csv_file}")
if 'excel_file' in locals():
    print(f"  - Excel 파일: {excel_file}")
print(f"  - 분석 보고서: {summary_file}")
