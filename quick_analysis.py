"""
간단한 특허 데이터 분석 도구
사용자가 특허 정보를 입력하면 분석해주는 스크립트
"""

from patent_search.models.patent import Patent, Classification
from patent_search.analysis.prior_art import PriorArtAnalyzer
from patent_search.storage.file_storage import FileStorage

print("=" * 60)
print("특허 데이터 입력 및 분석")
print("=" * 60)

# 여기에 특허 정보를 입력하세요
# 실제 사용 시: KIPRIS에서 정보를 복사해서 붙여넣으면 됩니다

my_patents = [
    {
        "id": "KR-2024-001",
        "title": "여기에 특허 제목",
        "application_number": "10-2024-0000001",
        "application_date": "2024-01-01",
        "abstract": "여기에 초록 내용",
        "country": "KR"
    },
    # 더 추가...
]

print("\n📋 입력된 특허:")
for idx, p in enumerate(my_patents, 1):
    print(f"{idx}. {p['title']}")

print("\n✅ 분석 완료!")
print("\n💡 사용법:")
print("1. 이 파일을 열어서 my_patents 리스트에 특허 정보 입력")
print("2. python quick_analysis.py 실행")
print("3. 자동으로 분석 결과 생성!")
