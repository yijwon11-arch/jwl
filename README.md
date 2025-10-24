# Patent Prior Art Search System

특허 선행기술 조사를 자동화하는 시스템입니다.

## 기능

- **특허 문서 파싱**: 특허 제목, 초록, 청구항 추출
- **키워드 추출**: 기술 용어 및 핵심 개념 자동 추출
- **선행기술 검색**: Google Patents 및 공개 특허 데이터베이스 검색
- **유사도 분석**: TF-IDF 기반 유사도 계산
- **리포트 생성**: 관련 특허 목록 및 유사도 점수 제공

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

```bash
python main.py --title "특허 제목" --abstract "특허 초록" --claims "청구항"
```

또는 JSON 파일로 입력:

```bash
python main.py --input patent.json
```

### 입력 형식 (JSON)

```json
{
  "title": "특허 제목",
  "abstract": "특허 초록 내용",
  "claims": ["청구항 1", "청구항 2"],
  "keywords": ["선택적 키워드"]
}
```

## 프로젝트 구조

```
jwl/
├── src/
│   ├── patent_parser.py       # 특허 문서 파싱
│   ├── search_engine.py       # 선행기술 검색
│   ├── similarity_analyzer.py # 유사도 분석
│   └── report_generator.py    # 결과 리포팅
├── tests/
│   └── test_prior_art_search.py
├── main.py
├── requirements.txt
└── README.md
```

## 라이선스

MIT License
