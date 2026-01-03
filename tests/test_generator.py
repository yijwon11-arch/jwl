"""특허명세서 생성기 테스트"""

import pytest
import tempfile
from pathlib import Path

from patent_generator.models.invention import (
    InventionData,
    TechnicalField,
    BackgroundArt,
    ProblemToSolve,
    Solution,
    Effect,
    Claim,
    DrawingDescription,
    Embodiment,
    ReferenceSign,
)
from patent_generator.generators.specification import PatentSpecificationGenerator
from patent_generator.utils.helpers import create_sample_invention_data


@pytest.fixture
def sample_invention():
    """테스트용 샘플 발명자료"""
    return create_sample_invention_data()


@pytest.fixture
def minimal_invention():
    """최소 발명자료"""
    return InventionData(
        title="테스트 발명의 명칭입니다",
        technical_field=TechnicalField(main_field="테스트 기술분야"),
        background_art=BackgroundArt(
            conventional_technology="종래 기술에 대한 설명입니다. 이 설명은 충분히 길어야 합니다. 최소 50자 이상이 필요합니다."
        ),
        problem_to_solve=ProblemToSolve(
            technical_problem="본 발명은 이러한 기술적 과제를 해결하고자 한다."
        ),
        solution=Solution(
            main_solution="본 발명은 이러한 해결 수단을 제공합니다."
        ),
        effect=Effect(main_effect="본 발명에 따르면 이러한 효과가 있다."),
    )


class TestPatentSpecificationGenerator:
    """PatentSpecificationGenerator 테스트"""

    def test_generate_minimal(self, minimal_invention):
        """최소 데이터로 명세서 생성 테스트"""
        generator = PatentSpecificationGenerator(minimal_invention)
        spec = generator.generate()

        assert "테스트 발명의 명칭입니다" in spec
        assert "【기술분야】" in spec
        assert "【발명의 배경이 되는 기술】" in spec
        assert "【해결하려는 과제】" in spec
        assert "【과제의 해결 수단】" in spec
        assert "【발명의 효과】" in spec

    def test_generate_full(self, sample_invention):
        """전체 데이터로 명세서 생성 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        spec = generator.generate()

        # 필수 섹션 확인
        assert "【명세서】" in spec
        assert "【발명의 명칭】" in spec
        assert "【기술분야】" in spec
        assert "【발명의 배경이 되는 기술】" in spec
        assert "【발명의 내용】" in spec
        assert "【해결하려는 과제】" in spec
        assert "【과제의 해결 수단】" in spec
        assert "【발명의 효과】" in spec
        assert "【청구범위】" in spec
        assert "【요약서】" in spec

        # 도면 관련 섹션
        assert "【도면의 간단한 설명】" in spec

        # 실시예 섹션
        assert "【발명을 실시하기 위한 구체적인 내용】" in spec

    def test_save_txt(self, sample_invention):
        """TXT 저장 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        generator.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_spec"
            saved_path = generator.save(str(output_path), format="txt")

            assert saved_path.endswith(".txt")
            assert Path(saved_path).exists()

            content = Path(saved_path).read_text(encoding="utf-8")
            assert "인공지능 기반 실시간 번역" in content

    def test_save_markdown(self, sample_invention):
        """Markdown 저장 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        generator.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_spec"
            saved_path = generator.save(str(output_path), format="md")

            assert saved_path.endswith(".md")
            assert Path(saved_path).exists()

            content = Path(saved_path).read_text(encoding="utf-8")
            assert "# 특허명세서" in content
            assert "## 기술분야" in content

    def test_statistics(self, sample_invention):
        """통계 정보 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        generator.generate()

        stats = generator.get_statistics()

        assert "title" in stats
        assert "total_characters" in stats
        assert "total_lines" in stats
        assert "num_claims" in stats
        assert stats["num_claims"] == len(sample_invention.claims)

    def test_from_yaml(self, sample_invention):
        """YAML 파일에서 생성기 초기화 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            sample_invention.to_yaml(str(yaml_path))

            generator = PatentSpecificationGenerator.from_yaml(str(yaml_path))
            spec = generator.generate()

            assert sample_invention.title in spec


class TestSectionGeneration:
    """개별 섹션 생성 테스트"""

    def test_claims_section(self, sample_invention):
        """청구항 섹션 생성 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        spec = generator.generate()

        # 모든 청구항이 포함되어 있는지 확인
        for claim in sample_invention.claims:
            assert f"【청구항 {claim.claim_number}】" in spec

    def test_drawings_section(self, sample_invention):
        """도면 설명 섹션 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        spec = generator.generate()

        for drawing in sample_invention.drawings:
            assert f"도 {drawing.figure_number}" in spec

    def test_reference_signs_section(self, sample_invention):
        """부호 설명 섹션 테스트"""
        generator = PatentSpecificationGenerator(sample_invention)
        spec = generator.generate()

        assert "【부호의 설명】" in spec
        for ref in sample_invention.reference_signs:
            assert ref.sign in spec
            assert ref.name in spec
