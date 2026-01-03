"""
Jinja2 기반 템플릿 엔진
========================

사용자 정의 템플릿을 지원하는 특허명세서 생성 엔진입니다.
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from patent_generator.models.invention import InventionData


class TemplateEngine:
    """
    Jinja2 기반 특허명세서 템플릿 엔진

    사용자 정의 템플릿을 사용하여 특허명세서를 생성할 수 있습니다.
    """

    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "defaults"

    def __init__(self, template_dir: str | Path | None = None):
        """
        Args:
            template_dir: 템플릿 디렉토리 경로. None이면 기본 템플릿 사용
        """
        if template_dir is None:
            template_dir = self.DEFAULT_TEMPLATE_DIR
        else:
            template_dir = Path(template_dir)

        self.template_dir = template_dir
        self._ensure_template_dir()

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # 사용자 정의 필터 등록
        self._register_filters()

    def _ensure_template_dir(self) -> None:
        """템플릿 디렉토리 존재 확인 및 생성"""
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # 기본 템플릿이 없으면 생성
        default_template = self.template_dir / "specification.txt.j2"
        if not default_template.exists():
            default_template.write_text(self._get_default_template(), encoding="utf-8")

    def _register_filters(self) -> None:
        """Jinja2 사용자 정의 필터 등록"""

        def korean_number(n: int) -> str:
            """숫자를 한글로 변환"""
            korean_nums = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
            if n < 10:
                return korean_nums[n]
            return str(n)

        def claim_reference(claim_num: int) -> str:
            """청구항 참조 형식"""
            return f"제{claim_num}항"

        self.env.filters["korean_number"] = korean_number
        self.env.filters["claim_reference"] = claim_reference

    def _get_default_template(self) -> str:
        """기본 템플릿 문자열 반환"""
        return '''============================================================
특허명세서
============================================================

발명의 명칭: {{ invention.title }}
작성일: {{ generation_date }}

{% if invention.applicants %}
【출원인】
{% for applicant in invention.applicants %}
  - {{ applicant.name }} ({{ applicant.nationality }})
{% endfor %}
{% endif %}

{% if invention.inventors %}
【발명자】
{% for inventor in invention.inventors %}
  - {{ inventor.name }} ({{ inventor.nationality }})
{% endfor %}
{% endif %}

============================================================

【명세서】

【발명의 명칭】
{{ invention.title }}

【기술분야】

본 발명은 {{ invention.technical_field.main_field }}에 관한 것{% if invention.technical_field.sub_fields %}으로, 보다 상세하게는 {{ invention.technical_field.sub_fields | join(", ") }}에 관한 것이다.{% else %}이다.{% endif %}

{% if invention.technical_field.ipc_codes %}
[IPC 분류: {{ invention.technical_field.ipc_codes | join(", ") }}]
{% endif %}

【발명의 배경이 되는 기술】

{{ invention.background_art.conventional_technology }}

{% if invention.background_art.problems_of_prior_art %}
그러나, 종래 기술은 다음과 같은 문제점이 있다.

{% for problem in invention.background_art.problems_of_prior_art %}
{{ loop.index }}) {{ problem }}
{% endfor %}
{% endif %}

{% if invention.background_art.prior_art_documents %}
【선행기술문헌】

{% for doc in invention.background_art.prior_art_documents %}
- {{ doc }}
{% endfor %}
{% endif %}

【발명의 내용】

【해결하려는 과제】

{{ invention.problem_to_solve.technical_problem }}

{% if invention.problem_to_solve.objectives %}
본 발명의 목적은 다음과 같다.

{% for objective in invention.problem_to_solve.objectives %}
{{ loop.index }}) {{ objective }}
{% endfor %}
{% endif %}

【과제의 해결 수단】

상기한 목적을 달성하기 위하여, 본 발명은 다음과 같은 구성을 포함한다.

{{ invention.solution.main_solution }}

{% if invention.solution.technical_features %}
본 발명의 기술적 특징은 다음과 같다.

{% for feature in invention.solution.technical_features %}
- {{ feature }}
{% endfor %}
{% endif %}

{% if invention.solution.key_components %}
본 발명의 핵심 구성요소는 다음을 포함한다.

{% for component in invention.solution.key_components %}
- {{ component }}
{% endfor %}
{% endif %}

{% if invention.solution.operation_principle %}
본 발명의 작동 원리는 다음과 같다.

{{ invention.solution.operation_principle }}
{% endif %}

【발명의 효과】

{{ invention.effect.main_effect }}

{% if invention.effect.additional_effects %}
또한, 본 발명은 다음과 같은 부가적인 효과를 제공한다.

{% for effect in invention.effect.additional_effects %}
{{ loop.index }}) {{ effect }}
{% endfor %}
{% endif %}

{% if invention.effect.industrial_applicability %}
【산업상 이용가능성】

{{ invention.effect.industrial_applicability }}
{% endif %}

{% if invention.drawings %}
【도면의 간단한 설명】

{% for drawing in invention.drawings | sort(attribute='figure_number') %}
도 {{ drawing.figure_number }}은 {{ drawing.title }}을 나타내는 {{ drawing.description }}이다.
{% endfor %}
{% endif %}

{% if invention.embodiments %}
【발명을 실시하기 위한 구체적인 내용】

이하, 첨부된 도면을 참조하여 본 발명의 바람직한 실시예를 상세히 설명한다.

{% for embodiment in invention.embodiments | sort(attribute='embodiment_number') %}
{% if invention.embodiments | length > 1 %}
<실시예 {{ embodiment.embodiment_number }}: {{ embodiment.title }}>

{% endif %}
{{ embodiment.description }}

{% if embodiment.operation_description %}
상기 구성의 동작을 설명하면 다음과 같다.

{{ embodiment.operation_description }}
{% endif %}

{% if embodiment.variations %}
한편, 본 실시예는 다음과 같은 변형예를 포함할 수 있다.

{% for variation in embodiment.variations %}
- {{ variation }}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if invention.reference_signs %}
【부호의 설명】

{% for ref in invention.reference_signs %}
{{ ref.sign }}: {{ ref.name }}
{% endfor %}
{% endif %}

{% if invention.claims %}
【청구범위】

{% for claim in invention.claims | sort(attribute='claim_number') %}
【청구항 {{ claim.claim_number }}】
{% if claim.claim_type == 'dependent' and claim.dependent_on %}
제{{ claim.dependent_on }}항에 있어서,
{% endif %}
{% if claim.preamble %}
{{ claim.preamble }}
{% endif %}
{{ claim.characterizing_portion }}

{% endfor %}
{% endif %}

【요약서】

【요약】

{% if invention.abstract %}
【과제】 {{ invention.abstract.problem }}

【해결수단】 {{ invention.abstract.solution }}

【효과】 {{ invention.abstract.effect }}

{% if invention.abstract.representative_figure %}
【대표도】 도 {{ invention.abstract.representative_figure }}
{% endif %}
{% else %}
【과제】 {{ invention.problem_to_solve.technical_problem }}

【해결수단】 {{ invention.solution.main_solution }}

【효과】 {{ invention.effect.main_effect }}
{% endif %}
'''

    def render(
        self,
        invention_data: InventionData,
        template_name: str = "specification.txt.j2",
        **extra_context: Any,
    ) -> str:
        """
        템플릿을 사용하여 특허명세서 생성

        Args:
            invention_data: 발명자료 데이터
            template_name: 사용할 템플릿 파일명
            **extra_context: 추가 컨텍스트 변수

        Returns:
            생성된 특허명세서 텍스트
        """
        from datetime import datetime

        template = self.env.get_template(template_name)

        context = {
            "invention": invention_data,
            "generation_date": datetime.now().strftime("%Y년 %m월 %d일"),
            **extra_context,
        }

        return template.render(**context)

    def list_templates(self) -> list[str]:
        """사용 가능한 템플릿 목록 반환"""
        return [
            f.name for f in self.template_dir.iterdir() if f.suffix in (".j2", ".jinja2", ".jinja")
        ]

    def create_custom_template(
        self, template_name: str, template_content: str
    ) -> Path:
        """
        사용자 정의 템플릿 생성

        Args:
            template_name: 템플릿 파일명 (.j2 확장자 권장)
            template_content: 템플릿 내용

        Returns:
            생성된 템플릿 파일 경로
        """
        template_path = self.template_dir / template_name
        template_path.write_text(template_content, encoding="utf-8")
        return template_path
