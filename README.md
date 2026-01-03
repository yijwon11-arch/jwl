# 자동 특허명세서 작성 시스템

발명자료를 기반으로 한국 특허명세서를 자동으로 생성하는 시스템입니다.

## 주요 기능

- **발명자료 입력**: YAML 또는 JSON 형식의 구조화된 발명자료 지원
- **특허명세서 자동 생성**: 한국 특허청 양식에 맞는 명세서 생성
- **다양한 출력 형식**: TXT, Markdown, DOCX 형식 지원
- **템플릿 커스터마이징**: Jinja2 기반 사용자 정의 템플릿 지원
- **데이터 검증**: 발명자료의 유효성 자동 검증

## 설치

```bash
# 저장소 클론
git clone <repository-url>
cd jwl

# 의존성 설치
pip install -e .

# 또는 개발 모드로 설치
pip install -e ".[dev]"
```

## 빠른 시작

### 1. 예제 발명자료 생성

```bash
patent-gen sample -o my_invention.yaml
```

### 2. 발명자료 파일 작성

생성된 `my_invention.yaml` 파일을 열어 발명 내용을 작성합니다:

```yaml
title: "발명의 명칭"

technical_field:
  main_field: "주요 기술분야"
  sub_fields:
    - "세부 기술분야 1"
    - "세부 기술분야 2"

background_art:
  conventional_technology: |
    종래 기술에 대한 설명...
  problems_of_prior_art:
    - "문제점 1"
    - "문제점 2"

problem_to_solve:
  technical_problem: "해결하려는 기술적 과제"
  objectives:
    - "목적 1"
    - "목적 2"

solution:
  main_solution: "과제의 해결 수단"
  technical_features:
    - "기술적 특징 1"
    - "기술적 특징 2"

effect:
  main_effect: "발명의 주요 효과"
  additional_effects:
    - "부가적 효과 1"
    - "부가적 효과 2"

claims:
  - claim_number: 1
    claim_type: "independent"
    characterizing_portion: "청구항 1의 내용"
```

### 3. 특허명세서 생성

```bash
# 기본 생성 (TXT 형식)
patent-gen generate my_invention.yaml

# Markdown 형식으로 생성
patent-gen generate my_invention.yaml -f md

# DOCX 형식으로 생성
patent-gen generate my_invention.yaml -f docx

# 출력 파일명 지정 + 통계 출력
patent-gen generate my_invention.yaml -o patent_spec.txt --stats
```

## CLI 명령어

### `patent-gen generate`

발명자료 파일에서 특허명세서를 생성합니다.

```bash
patent-gen generate [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH      출력 파일 경로
  -f, --format [txt|md|docx]  출력 형식 (기본: txt)
  --template PATH        사용자 정의 템플릿 디렉토리
  --validate/--no-validate    데이터 검증 여부 (기본: 검증함)
  --stats/--no-stats     통계 정보 출력
```

### `patent-gen sample`

예제 발명자료 파일을 생성합니다.

```bash
patent-gen sample [OPTIONS]

Options:
  -o, --output PATH           출력 파일 경로 (기본: sample_invention.yaml)
  -f, --format [yaml|json]    출력 형식 (기본: yaml)
```

### `patent-gen validate`

발명자료 파일의 유효성을 검증합니다.

```bash
patent-gen validate INPUT_FILE
```

### `patent-gen info`

발명자료 파일의 상세 정보를 출력합니다.

```bash
patent-gen info INPUT_FILE
```

### `patent-gen init-templates`

사용자 정의 템플릿을 초기화합니다.

```bash
patent-gen init-templates -o my_templates
```

## 발명자료 구조

발명자료는 다음 필드들로 구성됩니다:

| 필드 | 필수 | 설명 |
|------|------|------|
| `title` | O | 발명의 명칭 |
| `technical_field` | O | 기술분야 정보 |
| `background_art` | O | 발명의 배경이 되는 기술 |
| `problem_to_solve` | O | 해결하려는 과제 |
| `solution` | O | 과제의 해결 수단 |
| `effect` | O | 발명의 효과 |
| `applicants` | | 출원인 목록 |
| `inventors` | | 발명자 목록 |
| `drawings` | | 도면 설명 목록 |
| `embodiments` | | 실시예 목록 |
| `reference_signs` | | 부호의 설명 |
| `claims` | | 청구항 목록 |
| `abstract` | | 요약서 |

## Python API 사용

```python
from patent_generator import InventionData, PatentSpecificationGenerator

# 발명자료 로드
invention = InventionData.from_yaml("my_invention.yaml")

# 명세서 생성기 초기화
generator = PatentSpecificationGenerator(invention)

# 명세서 생성
specification_text = generator.generate()

# 파일로 저장
generator.save("output/patent_spec", format="md")

# 통계 정보 확인
stats = generator.get_statistics()
print(f"총 문자 수: {stats['total_characters']}")
print(f"청구항 수: {stats['num_claims']}")
```

## 템플릿 커스터마이징

Jinja2 템플릿을 사용하여 출력 형식을 커스터마이징할 수 있습니다:

```python
from patent_generator.templates import TemplateEngine

# 템플릿 엔진 초기화
engine = TemplateEngine("my_templates")

# 발명자료 로드
invention = InventionData.from_yaml("my_invention.yaml")

# 템플릿으로 명세서 생성
spec = engine.render(invention, template_name="my_template.j2")
```

## 테스트 실행

```bash
# pytest 설치
pip install pytest pytest-cov

# 테스트 실행
pytest tests/

# 커버리지 포함 테스트
pytest tests/ --cov=patent_generator
```

## 프로젝트 구조

```
jwl/
├── src/
│   └── patent_generator/
│       ├── __init__.py
│       ├── cli.py              # CLI 인터페이스
│       ├── models/
│       │   ├── __init__.py
│       │   └── invention.py    # 발명자료 데이터 모델
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── specification.py  # 명세서 생성기
│       │   └── sections.py       # 섹션별 생성 함수
│       ├── templates/
│       │   ├── __init__.py
│       │   └── template_engine.py  # Jinja2 템플릿 엔진
│       └── utils/
│           ├── __init__.py
│           ├── validators.py   # 데이터 검증
│           └── helpers.py      # 유틸리티 함수
├── examples/
│   └── sample_invention.yaml   # 예제 발명자료
├── tests/
│   ├── test_models.py
│   ├── test_generator.py
│   └── test_validators.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 라이선스

MIT License
