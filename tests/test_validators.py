"""검증 유틸리티 테스트"""

import pytest

from patent_generator.models.invention import (
    InventionData,
    TechnicalField,
    BackgroundArt,
    ProblemToSolve,
    Solution,
    Effect,
    Claim,
)
from patent_generator.utils.validators import validate_invention_data, ValidationError


@pytest.fixture
def valid_invention():
    """유효한 발명자료"""
    return InventionData(
        title="테스트 발명의 명칭입니다",
        technical_field=TechnicalField(main_field="테스트 기술분야"),
        background_art=BackgroundArt(
            conventional_technology="종래 기술에 대한 상세한 설명입니다. 이 설명은 충분히 길어야 합니다. 최소 50자 이상이 필요합니다."
        ),
        problem_to_solve=ProblemToSolve(
            technical_problem="본 발명은 이러한 기술적 과제를 해결하고자 한다."
        ),
        solution=Solution(
            main_solution="본 발명은 이러한 해결 수단을 제공합니다."
        ),
        effect=Effect(main_effect="본 발명에 따르면 이러한 효과가 있다."),
    )


class TestValidation:
    """검증 테스트"""

    def test_valid_data(self, valid_invention):
        """유효한 데이터 검증"""
        errors = validate_invention_data(valid_invention)
        assert len(errors) == 0

    def test_short_title(self, valid_invention):
        """짧은 제목 검증"""
        valid_invention.title = "테스트"  # 5자 미만
        errors = validate_invention_data(valid_invention)
        assert any("발명의 명칭" in e for e in errors)

    def test_short_background(self, valid_invention):
        """짧은 배경기술 검증"""
        valid_invention.background_art.conventional_technology = "짧은 설명"
        errors = validate_invention_data(valid_invention)
        assert any("종래 기술 설명" in e for e in errors)

    def test_short_solution(self, valid_invention):
        """짧은 해결수단 검증"""
        valid_invention.solution.main_solution = "짧은 해결수단"
        errors = validate_invention_data(valid_invention)
        assert any("해결 수단 설명" in e for e in errors)

    def test_duplicate_claim_numbers(self, valid_invention):
        """중복 청구항 번호 검증"""
        valid_invention.claims = [
            Claim(claim_number=1, characterizing_portion="청구항 1"),
            Claim(claim_number=1, characterizing_portion="중복된 청구항 1"),
        ]
        errors = validate_invention_data(valid_invention)
        assert any("청구항 번호가 중복" in e for e in errors)

    def test_dependent_claim_without_target(self, valid_invention):
        """종속 대상 없는 종속항 검증"""
        valid_invention.claims = [
            Claim(
                claim_number=2,
                claim_type="dependent",
                dependent_on=None,  # 종속 대상 없음
                characterizing_portion="종속항",
            ),
        ]
        errors = validate_invention_data(valid_invention)
        assert any("종속 대상이 지정되지 않았습니다" in e for e in errors)

    def test_dependent_claim_invalid_target(self, valid_invention):
        """존재하지 않는 청구항에 종속 검증"""
        valid_invention.claims = [
            Claim(claim_number=1, characterizing_portion="독립항"),
            Claim(
                claim_number=2,
                claim_type="dependent",
                dependent_on=99,  # 존재하지 않는 청구항
                characterizing_portion="종속항",
            ),
        ]
        errors = validate_invention_data(valid_invention)
        assert any("존재하지 않습니다" in e for e in errors)

    def test_dependent_claim_self_reference(self, valid_invention):
        """자기 자신보다 뒤의 청구항에 종속 검증"""
        valid_invention.claims = [
            Claim(claim_number=1, characterizing_portion="독립항"),
            Claim(
                claim_number=2,
                claim_type="dependent",
                dependent_on=3,  # 자신보다 뒤의 청구항
                characterizing_portion="종속항",
            ),
            Claim(claim_number=3, characterizing_portion="독립항 2"),
        ]
        errors = validate_invention_data(valid_invention)
        assert any("뒤의 청구항에 종속될 수 없습니다" in e for e in errors)
