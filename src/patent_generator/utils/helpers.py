"""
헬퍼 유틸리티 함수
===================

발명자료 로드 및 기타 유틸리티 함수들입니다.
"""

from pathlib import Path
from typing import Literal

from patent_generator.models.invention import (
    InventionData,
    TechnicalField,
    BackgroundArt,
    ProblemToSolve,
    Solution,
    Effect,
    DrawingDescription,
    Embodiment,
    ReferenceSign,
    Claim,
    Abstract,
    ApplicantInfo,
    InventorInfo,
)


def detect_file_format(file_path: str | Path) -> Literal["yaml", "json", "unknown"]:
    """
    파일 확장자로 형식 감지

    Args:
        file_path: 파일 경로

    Returns:
        파일 형식 ("yaml", "json", "unknown")
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        return "yaml"
    elif suffix == ".json":
        return "json"
    else:
        return "unknown"


def load_invention_file(file_path: str | Path) -> InventionData:
    """
    파일에서 발명자료 로드 (형식 자동 감지)

    Args:
        file_path: 발명자료 파일 경로

    Returns:
        로드된 InventionData 객체

    Raises:
        ValueError: 지원하지 않는 파일 형식
        FileNotFoundError: 파일이 존재하지 않음
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    file_format = detect_file_format(path)

    if file_format == "yaml":
        return InventionData.from_yaml(str(path))
    elif file_format == "json":
        return InventionData.from_json(str(path))
    else:
        raise ValueError(
            f"지원하지 않는 파일 형식입니다: {path.suffix}. "
            "YAML(.yaml, .yml) 또는 JSON(.json) 파일을 사용하세요."
        )


def create_sample_invention_data() -> InventionData:
    """
    예제 발명자료 생성

    특허명세서 작성 테스트용 샘플 데이터를 생성합니다.

    Returns:
        샘플 InventionData 객체
    """
    return InventionData(
        title="인공지능 기반 실시간 번역 장치 및 방법",
        applicants=[
            ApplicantInfo(
                name="주식회사 테크이노베이션",
                nationality="대한민국",
                address="서울특별시 강남구 테헤란로 123",
            )
        ],
        inventors=[
            InventorInfo(
                name="김발명",
                nationality="대한민국",
                address="서울특별시 서초구",
            ),
            InventorInfo(
                name="이기술",
                nationality="대한민국",
                address="경기도 성남시",
            ),
        ],
        technical_field=TechnicalField(
            main_field="인공지능 기반 자연어 처리",
            sub_fields=["기계번역", "음성인식", "실시간 처리"],
            ipc_codes=["G06F 40/58", "G06N 3/08", "G10L 15/26"],
            description="본 발명은 딥러닝 기술을 활용한 실시간 다국어 번역 시스템에 관한 것이다.",
        ),
        background_art=BackgroundArt(
            conventional_technology=(
                "종래의 기계번역 시스템은 통계 기반 번역(SMT) 또는 규칙 기반 번역 방식을 "
                "사용하였다. 통계 기반 번역은 대용량 병렬 코퍼스를 필요로 하며, 규칙 기반 "
                "번역은 언어 전문가의 수작업 규칙 작성이 필요하다. 최근에는 신경망 기반 "
                "번역(NMT)이 등장하여 번역 품질이 크게 향상되었으나, 실시간 처리 속도와 "
                "리소스 효율성 측면에서 여전히 개선이 필요한 상황이다."
            ),
            prior_art_documents=[
                "대한민국 공개특허공보 제10-2020-0012345호",
                "미국 특허 US 10,123,456 B2",
                "Vaswani et al., 'Attention Is All You Need', NeurIPS 2017",
            ],
            problems_of_prior_art=[
                "실시간 번역 시 지연시간(latency)이 크다",
                "GPU 등 고가의 하드웨어가 필수적이다",
                "문맥을 충분히 반영하지 못해 번역 품질이 떨어지는 경우가 있다",
                "저자원 언어쌍에 대한 번역 성능이 낮다",
            ],
        ),
        problem_to_solve=ProblemToSolve(
            technical_problem=(
                "본 발명은 상기한 종래 기술의 문제점을 해결하기 위한 것으로, "
                "경량화된 신경망 모델을 사용하여 저사양 기기에서도 실시간 번역이 "
                "가능하면서도 높은 번역 품질을 유지하는 번역 장치 및 방법을 제공하고자 한다."
            ),
            objectives=[
                "실시간 번역 시 100ms 이하의 지연시간 달성",
                "모바일 기기에서 구동 가능한 경량 모델 제공",
                "문맥 인식 기반의 고품질 번역 제공",
                "저자원 언어쌍에 대한 번역 성능 향상",
            ],
        ),
        solution=Solution(
            main_solution=(
                "본 발명에 따른 인공지능 기반 실시간 번역 장치는, "
                "입력 텍스트를 수신하는 입력부; "
                "지식 증류(Knowledge Distillation) 기법으로 경량화된 "
                "트랜스포머 기반 번역 모델을 포함하는 번역 엔진부; "
                "문맥 정보를 저장하고 관리하는 문맥 관리부; 및 "
                "번역 결과를 출력하는 출력부를 포함한다."
            ),
            technical_features=[
                "지식 증류를 통해 대형 모델의 성능을 소형 모델로 전이",
                "동적 양자화(Dynamic Quantization)를 적용한 추론 최적화",
                "슬라이딩 윈도우 기반의 효율적인 문맥 관리",
                "다국어 공유 임베딩을 통한 저자원 언어 지원",
            ],
            key_components=[
                "경량화 트랜스포머 인코더-디코더",
                "문맥 캐시 모듈",
                "동적 배칭 처리기",
                "적응형 어텐션 메커니즘",
            ],
            operation_principle=(
                "입력 텍스트가 수신되면, 먼저 토크나이저를 통해 서브워드 단위로 분할된다. "
                "분할된 토큰은 다국어 공유 임베딩 레이어를 거쳐 벡터로 변환되고, "
                "경량화된 트랜스포머 인코더에 입력된다. 인코더는 문맥 캐시에 저장된 "
                "이전 문맥 정보를 참조하여 현재 입력의 맥락을 파악한다. "
                "디코더는 인코더 출력과 타겟 언어의 이전 토큰을 기반으로 "
                "번역 결과를 순차적으로 생성한다."
            ),
        ),
        effect=Effect(
            main_effect=(
                "본 발명에 따르면, 경량화된 모델 구조와 최적화 기법을 통해 "
                "모바일 기기에서도 50ms 이하의 지연시간으로 실시간 번역이 가능하며, "
                "문맥 인식 기능을 통해 BLEU 스코어 기준 종래 기술 대비 15% 향상된 "
                "번역 품질을 달성할 수 있다."
            ),
            additional_effects=[
                "모델 크기를 기존 대비 80% 축소하여 저장 공간 절약",
                "저전력 동작으로 배터리 소모 감소",
                "저자원 언어쌍에서도 안정적인 번역 품질 제공",
                "점진적 번역 출력으로 사용자 경험 향상",
            ],
            industrial_applicability=(
                "본 발명은 스마트폰 번역 앱, 화상회의 실시간 자막, "
                "국제 고객 서비스 챗봇, 다국어 콘텐츠 제작 도구 등 "
                "다양한 산업 분야에 적용될 수 있다."
            ),
        ),
        drawings=[
            DrawingDescription(
                figure_number=1,
                title="본 발명의 전체 시스템 구성",
                description="블록도",
            ),
            DrawingDescription(
                figure_number=2,
                title="경량화 트랜스포머 모델의 구조",
                description="구조도",
            ),
            DrawingDescription(
                figure_number=3,
                title="문맥 관리부의 동작 흐름",
                description="순서도",
            ),
            DrawingDescription(
                figure_number=4,
                title="번역 처리 과정",
                description="흐름도",
            ),
        ],
        embodiments=[
            Embodiment(
                embodiment_number=1,
                title="시스템 전체 구성",
                description=(
                    "도 1을 참조하면, 본 발명의 실시간 번역 장치(100)는 "
                    "입력부(110), 번역 엔진부(120), 문맥 관리부(130), 및 출력부(140)를 포함한다. "
                    "입력부(110)는 사용자로부터 텍스트 또는 음성 입력을 수신한다. "
                    "번역 엔진부(120)는 경량화된 트랜스포머 모델을 사용하여 번역을 수행한다. "
                    "문맥 관리부(130)는 이전 번역 문맥을 저장하고 현재 번역에 활용한다. "
                    "출력부(140)는 번역 결과를 텍스트 또는 음성으로 출력한다."
                ),
                components=[
                    {"sign": "100", "name": "실시간 번역 장치", "description": "본 발명의 전체 장치를 나타낸다"},
                    {"sign": "110", "name": "입력부", "description": "텍스트 또는 음성 입력을 수신한다"},
                    {"sign": "120", "name": "번역 엔진부", "description": "신경망 기반 번역을 수행한다"},
                    {"sign": "130", "name": "문맥 관리부", "description": "번역 문맥을 관리한다"},
                    {"sign": "140", "name": "출력부", "description": "번역 결과를 출력한다"},
                ],
                operation_description=(
                    "사용자가 입력부(110)를 통해 원문 텍스트를 입력하면, "
                    "번역 엔진부(120)는 문맥 관리부(130)로부터 이전 문맥 정보를 조회한다. "
                    "번역 엔진부(120)는 조회된 문맥 정보와 현재 입력을 함께 처리하여 "
                    "번역 결과를 생성한다. 생성된 번역 결과는 출력부(140)를 통해 "
                    "사용자에게 제공되며, 동시에 문맥 관리부(130)에 저장되어 "
                    "이후 번역에 활용된다."
                ),
                variations=[
                    "입력부는 음성 인식 모듈을 포함하여 음성 입력을 지원할 수 있다",
                    "출력부는 음성 합성 모듈을 포함하여 번역 결과를 음성으로 출력할 수 있다",
                    "복수의 언어쌍을 지원하는 다중 번역 모델을 포함할 수 있다",
                ],
            ),
        ],
        reference_signs=[
            ReferenceSign(sign="100", name="실시간 번역 장치"),
            ReferenceSign(sign="110", name="입력부"),
            ReferenceSign(sign="120", name="번역 엔진부"),
            ReferenceSign(sign="121", name="트랜스포머 인코더"),
            ReferenceSign(sign="122", name="트랜스포머 디코더"),
            ReferenceSign(sign="130", name="문맥 관리부"),
            ReferenceSign(sign="131", name="문맥 캐시"),
            ReferenceSign(sign="140", name="출력부"),
        ],
        claims=[
            Claim(
                claim_number=1,
                claim_type="independent",
                preamble="인공지능 기반 실시간 번역 장치에 있어서,",
                characterizing_portion=(
                    "원문 텍스트를 수신하는 입력부;\n"
                    "지식 증류 기법으로 경량화된 트랜스포머 기반 번역 모델을 포함하며, "
                    "상기 원문 텍스트를 목표 언어로 번역하는 번역 엔진부;\n"
                    "이전 번역의 문맥 정보를 저장하고, 현재 번역 시 상기 문맥 정보를 "
                    "상기 번역 엔진부에 제공하는 문맥 관리부; 및\n"
                    "상기 번역된 텍스트를 출력하는 출력부를 포함하는 것을 특징으로 하는 "
                    "인공지능 기반 실시간 번역 장치."
                ),
                claim_category="apparatus",
            ),
            Claim(
                claim_number=2,
                claim_type="dependent",
                dependent_on=1,
                characterizing_portion=(
                    "상기 번역 엔진부는 동적 양자화가 적용된 추론 엔진을 포함하는 것을 "
                    "특징으로 하는 인공지능 기반 실시간 번역 장치."
                ),
                claim_category="apparatus",
            ),
            Claim(
                claim_number=3,
                claim_type="dependent",
                dependent_on=1,
                characterizing_portion=(
                    "상기 문맥 관리부는 슬라이딩 윈도우 방식으로 문맥 정보를 관리하며, "
                    "미리 설정된 윈도우 크기를 초과하는 이전 문맥은 삭제하는 것을 "
                    "특징으로 하는 인공지능 기반 실시간 번역 장치."
                ),
                claim_category="apparatus",
            ),
            Claim(
                claim_number=4,
                claim_type="independent",
                preamble="인공지능 기반 실시간 번역 방법에 있어서,",
                characterizing_portion=(
                    "입력부가 원문 텍스트를 수신하는 단계;\n"
                    "문맥 관리부가 이전 번역의 문맥 정보를 조회하는 단계;\n"
                    "번역 엔진부가 지식 증류 기법으로 경량화된 트랜스포머 모델을 사용하여, "
                    "상기 문맥 정보를 참조하면서 상기 원문 텍스트를 목표 언어로 번역하는 단계;\n"
                    "상기 문맥 관리부가 현재 번역 결과를 문맥 정보로 저장하는 단계; 및\n"
                    "출력부가 상기 번역된 텍스트를 출력하는 단계를 포함하는 것을 특징으로 하는 "
                    "인공지능 기반 실시간 번역 방법."
                ),
                claim_category="method",
            ),
            Claim(
                claim_number=5,
                claim_type="dependent",
                dependent_on=4,
                characterizing_portion=(
                    "상기 번역하는 단계는 동적 양자화된 모델을 사용하여 수행되는 것을 "
                    "특징으로 하는 인공지능 기반 실시간 번역 방법."
                ),
                claim_category="method",
            ),
        ],
        abstract=Abstract(
            title="인공지능 기반 실시간 번역 장치 및 방법",
            technical_field="인공지능 기반 자연어 처리 및 기계번역",
            problem=(
                "종래 기계번역 기술은 실시간 처리 시 지연시간이 크고, "
                "고성능 하드웨어를 필요로 하는 문제가 있었다."
            ),
            solution=(
                "지식 증류로 경량화된 트랜스포머 모델과 문맥 관리부를 포함하는 "
                "실시간 번역 장치를 제공한다."
            ),
            effect=(
                "모바일 기기에서 50ms 이하 지연시간으로 실시간 번역이 가능하며, "
                "문맥 인식으로 번역 품질이 15% 향상된다."
            ),
            representative_figure=1,
        ),
    )
