"""
발명자료 데이터 모델
====================

한국 특허명세서 작성에 필요한 발명자료의 구조화된 데이터 모델을 정의합니다.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TechnicalField(BaseModel):
    """기술분야 정보"""

    main_field: str = Field(..., description="주요 기술분야")
    sub_fields: list[str] = Field(default_factory=list, description="세부 기술분야")
    ipc_codes: list[str] = Field(default_factory=list, description="IPC 분류코드")
    description: Optional[str] = Field(None, description="기술분야 상세 설명")


class BackgroundArt(BaseModel):
    """발명의 배경이 되는 기술"""

    conventional_technology: str = Field(..., description="종래 기술 설명")
    prior_art_documents: list[str] = Field(default_factory=list, description="선행기술문헌")
    problems_of_prior_art: list[str] = Field(
        default_factory=list, description="종래 기술의 문제점"
    )


class ProblemToSolve(BaseModel):
    """해결하려는 과제"""

    technical_problem: str = Field(..., description="기술적 과제")
    objectives: list[str] = Field(default_factory=list, description="발명의 목적들")


class Solution(BaseModel):
    """과제의 해결 수단"""

    main_solution: str = Field(..., description="주요 해결 수단")
    technical_features: list[str] = Field(default_factory=list, description="기술적 특징들")
    key_components: list[str] = Field(default_factory=list, description="핵심 구성요소")
    operation_principle: Optional[str] = Field(None, description="작동 원리")


class Effect(BaseModel):
    """발명의 효과"""

    main_effect: str = Field(..., description="주요 효과")
    additional_effects: list[str] = Field(default_factory=list, description="부가적 효과들")
    industrial_applicability: Optional[str] = Field(None, description="산업상 이용가능성")


class DrawingDescription(BaseModel):
    """도면의 간단한 설명"""

    figure_number: int = Field(..., description="도면 번호")
    title: str = Field(..., description="도면 제목")
    description: str = Field(..., description="도면 설명")


class Embodiment(BaseModel):
    """발명을 실시하기 위한 구체적인 내용 (실시예)"""

    embodiment_number: int = Field(default=1, description="실시예 번호")
    title: str = Field(..., description="실시예 제목")
    description: str = Field(..., description="실시예 상세 설명")
    components: list[dict[str, str]] = Field(
        default_factory=list, description="구성요소 목록 (번호, 명칭, 설명)"
    )
    operation_description: Optional[str] = Field(None, description="동작 설명")
    variations: list[str] = Field(default_factory=list, description="변형예")


class ReferenceSign(BaseModel):
    """부호의 설명"""

    sign: str = Field(..., description="부호 (예: 10, 100, S100)")
    name: str = Field(..., description="명칭")


class Claim(BaseModel):
    """청구항"""

    claim_number: int = Field(..., description="청구항 번호")
    claim_type: str = Field(
        default="independent", description="청구항 유형 (independent/dependent)"
    )
    dependent_on: Optional[int] = Field(None, description="종속 대상 청구항 번호")
    preamble: Optional[str] = Field(None, description="전제부")
    characterizing_portion: str = Field(..., description="특징부 또는 청구항 본문")
    claim_category: str = Field(
        default="apparatus", description="청구항 카테고리 (apparatus/method/composition)"
    )


class Abstract(BaseModel):
    """요약서"""

    title: str = Field(..., description="발명의 명칭")
    technical_field: str = Field(..., description="기술분야 요약")
    problem: str = Field(..., description="해결 과제 요약")
    solution: str = Field(..., description="해결 수단 요약")
    effect: str = Field(..., description="효과 요약")
    representative_figure: Optional[int] = Field(None, description="대표 도면 번호")


class ApplicantInfo(BaseModel):
    """출원인 정보"""

    name: str = Field(..., description="출원인 명칭")
    nationality: str = Field(default="대한민국", description="국적")
    address: Optional[str] = Field(None, description="주소")


class InventorInfo(BaseModel):
    """발명자 정보"""

    name: str = Field(..., description="발명자 성명")
    nationality: str = Field(default="대한민국", description="국적")
    address: Optional[str] = Field(None, description="주소")


class InventionData(BaseModel):
    """
    발명자료 전체 데이터 모델

    한국 특허명세서 작성에 필요한 모든 정보를 포함하는 통합 모델입니다.
    """

    # 기본 정보
    title: str = Field(..., description="발명의 명칭")
    applicants: list[ApplicantInfo] = Field(default_factory=list, description="출원인 목록")
    inventors: list[InventorInfo] = Field(default_factory=list, description="발명자 목록")

    # 명세서 본문 구성요소
    technical_field: TechnicalField = Field(..., description="기술분야")
    background_art: BackgroundArt = Field(..., description="발명의 배경이 되는 기술")
    problem_to_solve: ProblemToSolve = Field(..., description="해결하려는 과제")
    solution: Solution = Field(..., description="과제의 해결 수단")
    effect: Effect = Field(..., description="발명의 효과")

    # 도면 및 실시예
    drawings: list[DrawingDescription] = Field(default_factory=list, description="도면 설명")
    embodiments: list[Embodiment] = Field(default_factory=list, description="실시예")
    reference_signs: list[ReferenceSign] = Field(default_factory=list, description="부호의 설명")

    # 청구범위 및 요약
    claims: list[Claim] = Field(default_factory=list, description="청구항 목록")
    abstract: Optional[Abstract] = Field(None, description="요약서")

    # 메타정보
    priority_claims: list[str] = Field(default_factory=list, description="우선권 주장")
    related_applications: list[str] = Field(default_factory=list, description="관련 출원")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "인공지능 기반 음성 인식 장치 및 방법",
                "technical_field": {
                    "main_field": "인공지능",
                    "sub_fields": ["음성 인식", "딥러닝", "자연어 처리"],
                    "ipc_codes": ["G10L 15/00", "G06N 3/08"],
                },
                "background_art": {
                    "conventional_technology": "종래의 음성 인식 기술은...",
                    "problems_of_prior_art": ["인식률이 낮음", "노이즈에 취약"],
                },
                "problem_to_solve": {
                    "technical_problem": "본 발명은 높은 인식률과 노이즈 강건성을 갖는 음성 인식 기술을 제공하고자 한다.",
                    "objectives": ["인식률 향상", "노이즈 강건성 확보"],
                },
                "solution": {
                    "main_solution": "본 발명은 트랜스포머 기반의 음성 인식 모델을 제안한다.",
                    "technical_features": ["어텐션 메커니즘", "멀티헤드 어텐션"],
                },
                "effect": {
                    "main_effect": "본 발명에 따르면 95% 이상의 음성 인식률을 달성할 수 있다.",
                    "additional_effects": ["실시간 처리 가능", "저전력 동작"],
                },
            }
        }

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "InventionData":
        """YAML 파일에서 발명자료 로드"""
        import yaml

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_json(cls, json_path: str) -> "InventionData":
        """JSON 파일에서 발명자료 로드"""
        import json

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_yaml(self, yaml_path: str) -> None:
        """YAML 파일로 발명자료 저장"""
        import yaml

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(), f, allow_unicode=True, default_flow_style=False, sort_keys=False
            )

    def to_json(self, json_path: str) -> None:
        """JSON 파일로 발명자료 저장"""
        import json

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)
