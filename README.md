# Patent Prior Art Search System

특허 선행기술 조사를 자동화하는 시스템입니다.

## 기능

- **다양한 파일 형식 지원**: JSON, TXT, PDF, DOCX, 이미지(OCR) 파일에서 특허 정보 자동 추출
- **특허 문서 파싱**: 특허 제목, 초록, 청구항 자동 인식 및 추출
- **키워드 추출**: 기술 용어 및 핵심 개념 자동 추출
- **선행기술 검색**: Google Patents 및 공개 특허 데이터베이스 검색
- **유사도 분석**: TF-IDF 기반 유사도 계산
- **리포트 생성**: 콘솔, JSON, Markdown 형식으로 결과 출력

## 설치

### 기본 설치 (필수)
```bash
pip install requests beautifulsoup4 scikit-learn numpy pandas
```

### 추가 파일 형식 지원 (선택)
```bash
# PDF 파일 지원
pip install PyPDF2

# DOCX 파일 지원
pip install python-docx

# 이미지 OCR 지원
pip install pytesseract Pillow
```

또는 전체 설치:
```bash
pip install -r requirements.txt
```

## 사용법

### 1. 파일에서 특허 정보 읽기

**JSON 파일** (권장):
```bash
python main.py --input patent.json
```

**텍스트 파일** (자동 파싱):
```bash
python main.py --input patent.txt
```

**PDF 파일**:
```bash
python main.py --input patent.pdf
```

**DOCX 파일**:
```bash
python main.py --input patent.docx
```

**이미지 파일** (OCR):
```bash
python main.py --input patent.png
```

### 2. 커맨드라인으로 직접 입력

```bash
python main.py --title "특허 제목" --abstract "특허 초록" --claims "청구항"
```

### 3. 결과를 파일로 저장

**Markdown 리포트**:
```bash
python main.py --input patent.json --format markdown --output report
```

**JSON 형식**:
```bash
python main.py --input patent.json --format json --output results
```

## 지원하는 파일 형식

| 형식 | 확장자 | 필요 라이브러리 | 설명 |
|------|--------|-----------------|------|
| JSON | `.json` | 없음 (기본) | 구조화된 특허 데이터 |
| 텍스트 | `.txt` | 없음 (기본) | 자동으로 제목, 초록, 청구항 추출 |
| PDF | `.pdf` | PyPDF2 | PDF 문서에서 텍스트 추출 |
| Word | `.docx`, `.doc` | python-docx | Word 문서 파싱 |
| 이미지 | `.png`, `.jpg`, `.jpeg` | pytesseract, Pillow | OCR로 텍스트 인식 |

### 입력 형식 예제

#### JSON 파일 (patent.json)

```json
{
  "title": "특허 제목",
  "abstract": "특허 초록 내용",
  "claims": ["청구항 1", "청구항 2"],
  "keywords": ["선택적 키워드"]
}
```

#### 텍스트 파일 (patent.txt)
```
제목: 블록체인 기반 스마트 계약 시스템

초록:
본 발명은 블록체인 기술을 활용한 스마트 계약 시스템에 관한 것이다.

청구항 1: 블록체인 네트워크를 포함하는 시스템
청구항 2: 자동으로 계약을 실행하는 방법
```

시스템이 자동으로 제목, 초록, 청구항을 인식하여 파싱합니다.

## 프로젝트 구조

```
jwl/
├── src/
│   ├── patent_parser.py       # 특허 데이터 파싱 및 키워드 추출
│   ├── file_parser.py         # 다양한 파일 형식 파싱 (NEW!)
│   ├── search_engine.py       # 선행기술 검색
│   ├── similarity_analyzer.py # 유사도 분석
│   └── report_generator.py    # 결과 리포팅
├── tests/
│   └── test_prior_art_search.py
├── main.py                    # CLI 진입점
├── example_patent.json        # JSON 예제
├── example_patent.txt         # 텍스트 예제
├── requirements.txt
└── README.md
```

## 주요 개선사항

### v2.0 - 다양한 파일 형식 지원
- ✅ PDF 파일 파싱 지원
- ✅ DOCX/DOC 파일 파싱 지원
- ✅ 이미지 OCR 지원 (PNG, JPG, JPEG)
- ✅ 텍스트 파일 자동 파싱
- ✅ 기존 JSON 형식 호환성 유지

## 라이선스

MIT License
