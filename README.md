# 특허 검색 및 선행기술 조사 시스템
Patent Search and Prior Art Research System

특허 정보를 검색하고 선행기술을 분석하는 Python 기반 CLI 도구입니다.

## 주요 기능

### 1. 특허 검색
- **다중 소스 지원**: KIPRIS (한국 특허청), Google Patents
- **유연한 검색**: 키워드, 출원인, 발명자, IPC 분류 등 다양한 조건으로 검색
- **쿼리 빌더**: 복잡한 검색 조건을 쉽게 구성

### 2. 선행기술 분석
- **유사도 계산**: 텍스트 유사도, IPC 분류 유사도 분석
- **특허 비교**: 두 특허의 상세 비교 및 리포트 생성
- **유사 특허 발견**: 대상 특허와 유사한 특허 자동 검색

### 3. 데이터 관리
- **데이터베이스 저장**: SQLite 기반 검색 결과 및 특허 정보 저장
- **검색 이력**: 과거 검색 기록 추적 및 재검색
- **다양한 내보내기**: JSON, CSV, Excel 형식으로 결과 내보내기

### 4. CLI 인터페이스
- 사용하기 쉬운 명령줄 인터페이스
- 검색, 분석, 비교, 내보내기 등 모든 기능 지원

## 설치

### 요구사항
- Python 3.8 이상
- pip

### 의존성 설치
```bash
pip install -r requirements.txt
```

또는 개발 모드로 설치:
```bash
pip install -e .
```

## 설정

`config/config.json` 파일을 편집하여 API 키를 설정하세요:

```json
{
  "api": {
    "kipris": {
      "base_url": "http://plus.kipris.or.kr/openapi/rest",
      "api_key": "YOUR_KIPRIS_API_KEY"
    }
  }
}
```

KIPRIS API 키는 [특허정보넷 키프리스](https://www.kipris.or.kr)에서 발급받을 수 있습니다.

## 사용법

### 기본 검색

키워드로 검색:
```bash
python -m patent_search.cli.main search --keyword "인공지능"
```

출원인으로 검색:
```bash
python -m patent_search.cli.main search --applicant "삼성전자" --limit 50
```

복합 검색 조건:
```bash
python -m patent_search.cli.main search \
  --keyword "머신러닝" \
  --applicant "네이버" \
  --ipc "G06N" \
  --limit 100
```

### 검색 결과 저장 및 내보내기

데이터베이스에 저장:
```bash
python -m patent_search.cli.main search --keyword "블록체인" --save
```

CSV 파일로 내보내기:
```bash
python -m patent_search.cli.main search --keyword "5G" --export csv
```

Excel 파일로 내보내기:
```bash
python -m patent_search.cli.main search --keyword "자율주행" --export excel
```

### 특허 상세 정보 조회

```bash
python -m patent_search.cli.main detail "10-2023-0001234" --save
```

### 검색 이력 확인

```bash
python -m patent_search.cli.main history --limit 20
```

### 특허 비교

두 특허를 비교하고 유사도 분석:
```bash
python -m patent_search.cli.main compare TEST001 TEST002
```

### 유사 특허 찾기

특정 특허와 유사한 특허 검색:
```bash
python -m patent_search.cli.main similar TEST001 --threshold 30 --limit 10
```

### 데이터베이스 내보내기

저장된 모든 특허를 파일로 내보내기:
```bash
python -m patent_search.cli.main export-db --format excel --output patents_all.xlsx
```

## Python 코드에서 사용

### 검색 예제

```python
from patent_search.api.kipris import KiprisAPI
from patent_search.query.query_builder import QueryBuilder

# 쿼리 구성
query = QueryBuilder() \
    .keyword("인공지능") \
    .applicant("삼성전자") \
    .application_date_range("2020-01-01", "2023-12-31") \
    .build()

# KIPRIS 검색
with KiprisAPI(api_key="YOUR_API_KEY") as api:
    results = api.search(query, limit=100)

for patent in results:
    print(f"{patent['title']} - {patent['application_number']}")
```

### 선행기술 분석 예제

```python
from patent_search.analysis.prior_art import PriorArtAnalyzer
from patent_search.models.patent import Patent

# 특허 객체 생성
patent1 = Patent(id="P1", title="AI 기반 이미지 인식", ...)
patent2 = Patent(id="P2", title="딥러닝 이미지 분석", ...)

# 유사도 분석
analyzer = PriorArtAnalyzer()
comparison = analyzer.compare_patents(patent1, patent2)

print(f"전체 유사도: {comparison.similarity.overall}%")
print(f"제목 유사도: {comparison.similarity.title}%")
print(f"초록 유사도: {comparison.similarity.abstract}%")

# 리포트 생성
report = analyzer.generate_comparison_report(comparison)
print(report)
```

### 데이터베이스 사용 예제

```python
from patent_search.storage.database import PatentDatabase

with PatentDatabase("data/patents.db") as db:
    # 특허 저장
    db.save_patent(patent)

    # 특허 검색
    patents = db.search_patents(country="KR", status="granted")

    # 검색 이력 조회
    history = db.get_search_history(limit=10)
```

## 프로젝트 구조

```
jwl/
├── patent_search/           # 메인 패키지
│   ├── api/                # API 클라이언트
│   │   ├── base.py        # 기본 API 클래스
│   │   ├── kipris.py      # KIPRIS API
│   │   └── google_patents.py  # Google Patents API
│   ├── models/             # 데이터 모델
│   │   ├── patent.py      # 특허 모델
│   │   └── search_result.py  # 검색 결과 모델
│   ├── query/              # 쿼리 빌더
│   │   └── query_builder.py
│   ├── analysis/           # 분석 도구
│   │   └── prior_art.py   # 선행기술 분석
│   ├── storage/            # 저장소
│   │   ├── database.py    # SQLite 데이터베이스
│   │   └── file_storage.py  # 파일 저장
│   └── cli/                # CLI 인터페이스
│       └── main.py
├── tests/                   # 테스트
│   ├── test_query_builder.py
│   ├── test_patent_model.py
│   └── test_prior_art.py
├── data/                    # 데이터 저장소
├── config/                  # 설정 파일
│   └── config.json
├── requirements.txt         # 의존성
├── setup.py                # 패키지 설정
└── README.md               # 문서
```

## 테스트

단위 테스트 실행:
```bash
python -m pytest tests/
```

또는:
```bash
python -m unittest discover tests/
```

## 개발 로드맵

- [ ] 추가 특허 DB 지원 (USPTO, EPO, JPO)
- [ ] 웹 UI 구현
- [ ] 특허 분석 리포트 자동 생성
- [ ] 특허 포트폴리오 관리
- [ ] 특허 비용 추적
- [ ] 기한 관리 및 알림

## 라이선스

MIT License

## 기여

풀 리퀘스트와 이슈는 언제나 환영합니다!

## 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.
