"""
데이터 검증 유틸리티
=====================

발명자료의 유효성을 검증하는 함수들입니다.
"""

from patent_generator.models.invention import InventionData


class ValidationError(Exception):
    """발명자료 검증 오류"""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"검증 오류 {len(errors)}건 발생: {'; '.join(errors)}")


def validate_invention_data(data: InventionData) -> list[str]:
    """
    발명자료의 유효성 검증

    Args:
        data: 검증할 발명자료

    Returns:
        검증 오류 메시지 리스트 (비어있으면 유효함)
    """
    errors = []

    # 필수 필드 검증
    if not data.title or len(data.title.strip()) < 5:
        errors.append("발명의 명칭은 5자 이상이어야 합니다.")

    # 기술분야 검증
    if not data.technical_field.main_field:
        errors.append("주요 기술분야가 지정되어야 합니다.")

    # 배경기술 검증
    if not data.background_art.conventional_technology:
        errors.append("종래 기술 설명이 필요합니다.")

    if len(data.background_art.conventional_technology) < 50:
        errors.append("종래 기술 설명이 너무 짧습니다. (최소 50자)")

    # 해결 과제 검증
    if not data.problem_to_solve.technical_problem:
        errors.append("해결하려는 기술적 과제가 지정되어야 합니다.")

    # 해결 수단 검증
    if not data.solution.main_solution:
        errors.append("주요 해결 수단이 지정되어야 합니다.")

    if len(data.solution.main_solution) < 30:
        errors.append("해결 수단 설명이 너무 짧습니다. (최소 30자)")

    # 효과 검증
    if not data.effect.main_effect:
        errors.append("주요 효과가 지정되어야 합니다.")

    # 청구항 검증
    if data.claims:
        claim_numbers = [c.claim_number for c in data.claims]
        if len(claim_numbers) != len(set(claim_numbers)):
            errors.append("청구항 번호가 중복되었습니다.")

        for claim in data.claims:
            if claim.claim_type == "dependent":
                if claim.dependent_on is None:
                    errors.append(
                        f"청구항 {claim.claim_number}은 종속항이지만 종속 대상이 지정되지 않았습니다."
                    )
                elif claim.dependent_on not in claim_numbers:
                    errors.append(
                        f"청구항 {claim.claim_number}의 종속 대상 {claim.dependent_on}이 존재하지 않습니다."
                    )
                elif claim.dependent_on >= claim.claim_number:
                    errors.append(
                        f"청구항 {claim.claim_number}은 자신보다 뒤의 청구항에 종속될 수 없습니다."
                    )

    # 도면 검증
    if data.drawings:
        figure_numbers = [d.figure_number for d in data.drawings]
        if len(figure_numbers) != len(set(figure_numbers)):
            errors.append("도면 번호가 중복되었습니다.")

    # 실시예 검증
    if data.embodiments:
        embodiment_numbers = [e.embodiment_number for e in data.embodiments]
        if len(embodiment_numbers) != len(set(embodiment_numbers)):
            errors.append("실시예 번호가 중복되었습니다.")

    return errors


def validate_and_raise(data: InventionData) -> None:
    """
    발명자료 검증 후 오류 시 예외 발생

    Args:
        data: 검증할 발명자료

    Raises:
        ValidationError: 검증 오류 발생 시
    """
    errors = validate_invention_data(data)
    if errors:
        raise ValidationError(errors)
