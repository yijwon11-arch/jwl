"""발명자료 모델 테스트"""

import pytest
import tempfile
import json
from pathlib import Path

from patent_generator.models.invention import (
    InventionData,
    TechnicalField,
    BackgroundArt,
    ProblemToSolve,
    Solution,
    Effect,
    Claim,
    ApplicantInfo,
    InventorInfo,
)


@pytest.fixture
def minimal_invention_data():
    """최소 필수 필드만 포함하는 발명자료"""
    return InventionData(
        title="테스트 발명",
        technical_field=TechnicalField(main_field="테스트 기술분야"),
        background_art=BackgroundArt(
            conventional_technology="종래 기술에 대한 설명입니다. 이 설명은 최소 50자 이상이어야 합니다."
        ),
        problem_to_solve=ProblemToSolve(
            technical_problem="해결하려는 기술적 과제입니다."
        ),
        solution=Solution(
            main_solution="본 발명은 이러한 해결 수단을 제공합니다."
        ),
        effect=Effect(main_effect="본 발명의 효과입니다."),
    )


@pytest.fixture
def full_invention_data():
    """모든 필드를 포함하는 발명자료"""
    return InventionData(
        title="인공지능 기반 테스트 장치",
        applicants=[
            ApplicantInfo(name="테스트 회사", nationality="대한민국")
        ],
        inventors=[
            InventorInfo(name="홍길동", nationality="대한민국")
        ],
        technical_field=TechnicalField(
            main_field="인공지능",
            sub_fields=["머신러닝", "딥러닝"],
            ipc_codes=["G06N 3/08"],
        ),
        background_art=BackgroundArt(
            conventional_technology="종래 기술에 대한 상세한 설명입니다. 이 부분은 최소 50자 이상이어야 합니다.",
            problems_of_prior_art=["문제점 1", "문제점 2"],
        ),
        problem_to_solve=ProblemToSolve(
            technical_problem="본 발명은 종래 기술의 문제점을 해결하고자 한다.",
            objectives=["목적 1", "목적 2"],
        ),
        solution=Solution(
            main_solution="본 발명은 신규한 해결 수단을 제공합니다.",
            technical_features=["특징 1", "특징 2"],
        ),
        effect=Effect(
            main_effect="본 발명에 따르면 우수한 효과를 달성할 수 있다.",
            additional_effects=["부가 효과 1"],
        ),
        claims=[
            Claim(
                claim_number=1,
                claim_type="independent",
                characterizing_portion="청구항 1의 내용",
            ),
            Claim(
                claim_number=2,
                claim_type="dependent",
                dependent_on=1,
                characterizing_portion="청구항 2의 내용",
            ),
        ],
    )


class TestInventionData:
    """InventionData 모델 테스트"""

    def test_minimal_creation(self, minimal_invention_data):
        """최소 필드로 생성 테스트"""
        assert minimal_invention_data.title == "테스트 발명"
        assert minimal_invention_data.technical_field.main_field == "테스트 기술분야"

    def test_full_creation(self, full_invention_data):
        """전체 필드로 생성 테스트"""
        assert full_invention_data.title == "인공지능 기반 테스트 장치"
        assert len(full_invention_data.applicants) == 1
        assert len(full_invention_data.inventors) == 1
        assert len(full_invention_data.claims) == 2

    def test_yaml_roundtrip(self, full_invention_data):
        """YAML 저장/로드 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            full_invention_data.to_yaml(str(yaml_path))

            loaded = InventionData.from_yaml(str(yaml_path))
            assert loaded.title == full_invention_data.title
            assert len(loaded.claims) == len(full_invention_data.claims)

    def test_json_roundtrip(self, full_invention_data):
        """JSON 저장/로드 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "test.json"
            full_invention_data.to_json(str(json_path))

            loaded = InventionData.from_json(str(json_path))
            assert loaded.title == full_invention_data.title
            assert len(loaded.claims) == len(full_invention_data.claims)


class TestClaim:
    """Claim 모델 테스트"""

    def test_independent_claim(self):
        """독립항 생성 테스트"""
        claim = Claim(
            claim_number=1,
            claim_type="independent",
            characterizing_portion="테스트 청구항",
        )
        assert claim.claim_type == "independent"
        assert claim.dependent_on is None

    def test_dependent_claim(self):
        """종속항 생성 테스트"""
        claim = Claim(
            claim_number=2,
            claim_type="dependent",
            dependent_on=1,
            characterizing_portion="종속 청구항",
        )
        assert claim.claim_type == "dependent"
        assert claim.dependent_on == 1
