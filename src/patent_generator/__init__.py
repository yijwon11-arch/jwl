"""
자동 특허명세서 작성 시스템
============================

발명자료를 기반으로 한국 특허명세서를 자동으로 생성하는 시스템입니다.

주요 기능:
- 발명자료 입력 (YAML/JSON 형식)
- 특허명세서 자동 생성
- 다양한 출력 형식 지원 (Markdown, DOCX, TXT)
"""

from patent_generator.models.invention import InventionData
from patent_generator.generators.specification import PatentSpecificationGenerator

__version__ = "1.0.0"
__all__ = ["InventionData", "PatentSpecificationGenerator"]
