"""
특허명세서 각 섹션 생성 함수
=============================

한국 특허명세서의 각 섹션을 생성하는 개별 함수들입니다.
"""

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
)


def generate_technical_field_section(technical_field: TechnicalField) -> str:
    """기술분야 섹션 생성"""
    lines = ["【기술분야】", ""]

    main_text = f"본 발명은 {technical_field.main_field}에 관한 것"

    if technical_field.sub_fields:
        sub_fields_text = ", ".join(technical_field.sub_fields)
        main_text += f"으로, 보다 상세하게는 {sub_fields_text}에 관한 것이다."
    else:
        main_text += "이다."

    lines.append(main_text)

    if technical_field.description:
        lines.append("")
        lines.append(technical_field.description)

    if technical_field.ipc_codes:
        lines.append("")
        lines.append(f"[IPC 분류: {', '.join(technical_field.ipc_codes)}]")

    lines.append("")
    return "\n".join(lines)


def generate_background_art_section(background_art: BackgroundArt) -> str:
    """발명의 배경이 되는 기술 섹션 생성"""
    lines = ["【발명의 배경이 되는 기술】", ""]

    lines.append(background_art.conventional_technology)
    lines.append("")

    if background_art.problems_of_prior_art:
        lines.append("그러나, 종래 기술은 다음과 같은 문제점이 있다.")
        lines.append("")
        for i, problem in enumerate(background_art.problems_of_prior_art, 1):
            lines.append(f"{i}) {problem}")
        lines.append("")

    if background_art.prior_art_documents:
        lines.append("【선행기술문헌】")
        lines.append("")
        for doc in background_art.prior_art_documents:
            lines.append(f"- {doc}")
        lines.append("")

    return "\n".join(lines)


def generate_problem_section(problem: ProblemToSolve) -> str:
    """해결하려는 과제 섹션 생성"""
    lines = ["【해결하려는 과제】", ""]

    lines.append(problem.technical_problem)
    lines.append("")

    if problem.objectives:
        lines.append("본 발명의 목적은 다음과 같다.")
        lines.append("")
        for i, objective in enumerate(problem.objectives, 1):
            lines.append(f"{i}) {objective}")
        lines.append("")

    return "\n".join(lines)


def generate_solution_section(solution: Solution) -> str:
    """과제의 해결 수단 섹션 생성"""
    lines = ["【과제의 해결 수단】", ""]

    lines.append("상기한 목적을 달성하기 위하여, 본 발명은 다음과 같은 구성을 포함한다.")
    lines.append("")
    lines.append(solution.main_solution)
    lines.append("")

    if solution.technical_features:
        lines.append("본 발명의 기술적 특징은 다음과 같다.")
        lines.append("")
        for feature in solution.technical_features:
            lines.append(f"- {feature}")
        lines.append("")

    if solution.key_components:
        lines.append("본 발명의 핵심 구성요소는 다음을 포함한다.")
        lines.append("")
        for component in solution.key_components:
            lines.append(f"- {component}")
        lines.append("")

    if solution.operation_principle:
        lines.append("본 발명의 작동 원리는 다음과 같다.")
        lines.append("")
        lines.append(solution.operation_principle)
        lines.append("")

    return "\n".join(lines)


def generate_effect_section(effect: Effect) -> str:
    """발명의 효과 섹션 생성"""
    lines = ["【발명의 효과】", ""]

    lines.append(effect.main_effect)
    lines.append("")

    if effect.additional_effects:
        lines.append("또한, 본 발명은 다음과 같은 부가적인 효과를 제공한다.")
        lines.append("")
        for i, add_effect in enumerate(effect.additional_effects, 1):
            lines.append(f"{i}) {add_effect}")
        lines.append("")

    if effect.industrial_applicability:
        lines.append("【산업상 이용가능성】")
        lines.append("")
        lines.append(effect.industrial_applicability)
        lines.append("")

    return "\n".join(lines)


def generate_drawings_section(drawings: list[DrawingDescription]) -> str:
    """도면의 간단한 설명 섹션 생성"""
    if not drawings:
        return ""

    lines = ["【도면의 간단한 설명】", ""]

    for drawing in sorted(drawings, key=lambda x: x.figure_number):
        lines.append(f"도 {drawing.figure_number}은 {drawing.title}을 나타내는 {drawing.description}이다.")

    lines.append("")
    return "\n".join(lines)


def generate_embodiments_section(embodiments: list[Embodiment]) -> str:
    """발명을 실시하기 위한 구체적인 내용 섹션 생성"""
    if not embodiments:
        return ""

    lines = ["【발명을 실시하기 위한 구체적인 내용】", ""]

    lines.append("이하, 첨부된 도면을 참조하여 본 발명의 바람직한 실시예를 상세히 설명한다.")
    lines.append("")
    lines.append(
        "본 발명의 이점 및 특징, 그리고 그것들을 달성하는 방법은 첨부되는 도면과 함께 "
        "상세하게 후술되어 있는 실시예들을 참조하면 명확해질 것이다. 그러나 본 발명은 "
        "이하에서 개시되는 실시예들에 한정되는 것이 아니라 서로 다른 다양한 형태로 "
        "구현될 수 있으며, 단지 본 실시예들은 본 발명의 개시가 완전하도록 하고, "
        "본 발명이 속하는 기술분야에서 통상의 지식을 가진 자에게 발명의 범주를 "
        "완전하게 알려주기 위해 제공되는 것이며, 본 발명은 청구항의 범주에 의해 정의될 뿐이다."
    )
    lines.append("")

    for embodiment in sorted(embodiments, key=lambda x: x.embodiment_number):
        if len(embodiments) > 1:
            lines.append(f"<실시예 {embodiment.embodiment_number}: {embodiment.title}>")
            lines.append("")

        lines.append(embodiment.description)
        lines.append("")

        if embodiment.components:
            for comp in embodiment.components:
                sign = comp.get("sign", "")
                name = comp.get("name", "")
                desc = comp.get("description", "")
                if sign and name:
                    lines.append(f"{name}({sign})은 {desc}")
            lines.append("")

        if embodiment.operation_description:
            lines.append("상기 구성의 동작을 설명하면 다음과 같다.")
            lines.append("")
            lines.append(embodiment.operation_description)
            lines.append("")

        if embodiment.variations:
            lines.append("한편, 본 실시예는 다음과 같은 변형예를 포함할 수 있다.")
            lines.append("")
            for variation in embodiment.variations:
                lines.append(f"- {variation}")
            lines.append("")

    return "\n".join(lines)


def generate_reference_signs_section(reference_signs: list[ReferenceSign]) -> str:
    """부호의 설명 섹션 생성"""
    if not reference_signs:
        return ""

    lines = ["【부호의 설명】", ""]

    for ref in reference_signs:
        lines.append(f"{ref.sign}: {ref.name}")

    lines.append("")
    return "\n".join(lines)


def generate_claims_section(claims: list[Claim]) -> str:
    """청구범위 섹션 생성"""
    if not claims:
        return ""

    lines = ["【청구범위】", ""]

    for claim in sorted(claims, key=lambda x: x.claim_number):
        lines.append(f"【청구항 {claim.claim_number}】")

        if claim.claim_type == "dependent" and claim.dependent_on is not None:
            lines.append(f"제{claim.dependent_on}항에 있어서,")

        if claim.preamble:
            lines.append(claim.preamble)

        lines.append(claim.characterizing_portion)
        lines.append("")

    return "\n".join(lines)


def generate_abstract_section(abstract: Abstract | None, invention_data: InventionData) -> str:
    """요약서 섹션 생성"""
    lines = ["【요약서】", ""]

    if abstract:
        lines.append("【요약】")
        lines.append("")
        lines.append(f"【과제】 {abstract.problem}")
        lines.append("")
        lines.append(f"【해결수단】 {abstract.solution}")
        lines.append("")
        lines.append(f"【효과】 {abstract.effect}")
        lines.append("")

        if abstract.representative_figure is not None:
            lines.append(f"【대표도】 도 {abstract.representative_figure}")
            lines.append("")
    else:
        # 요약서가 없으면 자동 생성
        lines.append("【요약】")
        lines.append("")
        lines.append(f"【과제】 {invention_data.problem_to_solve.technical_problem}")
        lines.append("")
        lines.append(f"【해결수단】 {invention_data.solution.main_solution}")
        lines.append("")
        lines.append(f"【효과】 {invention_data.effect.main_effect}")
        lines.append("")

    return "\n".join(lines)
