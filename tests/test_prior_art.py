"""
선행기술 분석 테스트
Prior Art Analysis Tests
"""

import unittest
from patent_search.models.patent import Patent, Classification
from patent_search.analysis.prior_art import PriorArtAnalyzer


class TestPriorArtAnalyzer(unittest.TestCase):
    """PriorArtAnalyzer 테스트 클래스"""

    def setUp(self):
        """각 테스트 전 실행"""
        self.analyzer = PriorArtAnalyzer()

        # 테스트용 특허 1
        self.patent1 = Patent(
            id="TEST001",
            title="인공지능 기반 이미지 인식 시스템",
            application_number="10-2023-0001234",
            application_date="2023-01-15",
            abstract="본 발명은 인공지능을 이용한 이미지 인식 방법에 관한 것이다.",
            source="TEST"
        )
        self.patent1.classifications = Classification(
            ipc=["G06N3/08", "G06T7/00"]
        )

        # 테스트용 특허 2
        self.patent2 = Patent(
            id="TEST002",
            title="딥러닝을 활용한 이미지 분석 장치",
            application_number="10-2023-0005678",
            application_date="2023-02-20",
            abstract="본 발명은 딥러닝 기술을 활용하여 이미지를 분석하는 장치에 관한 것이다.",
            source="TEST"
        )
        self.patent2.classifications = Classification(
            ipc=["G06N3/08", "G06T1/00"]
        )

    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        text = "인공지능 기반 이미지 인식 시스템"
        keywords = self.analyzer.extract_keywords(text)
        self.assertIsInstance(keywords, list)
        self.assertIn("인공지능", keywords)
        self.assertIn("이미지", keywords)

    def test_text_similarity(self):
        """텍스트 유사도 테스트"""
        text1 = "인공지능 기반 이미지 인식"
        text2 = "인공지능을 이용한 이미지 분석"
        similarity = self.analyzer.calculate_text_similarity(text1, text2)
        self.assertGreater(similarity, 0)
        self.assertLessEqual(similarity, 100)

    def test_ipc_similarity(self):
        """IPC 유사도 테스트"""
        ipc1 = ["G06N3/08", "G06T7/00"]
        ipc2 = ["G06N3/08", "G06T1/00"]
        similarity = self.analyzer.calculate_ipc_similarity(ipc1, ipc2)
        self.assertGreater(similarity, 0)
        self.assertLessEqual(similarity, 100)

    def test_compare_patents(self):
        """특허 비교 테스트"""
        comparison = self.analyzer.compare_patents(self.patent1, self.patent2)

        self.assertIsNotNone(comparison)
        self.assertEqual(comparison.patent1.id, "TEST001")
        self.assertEqual(comparison.patent2.id, "TEST002")
        self.assertGreater(comparison.similarity.overall, 0)

    def test_find_similar_patents(self):
        """유사 특허 찾기 테스트"""
        patent_list = [self.patent2]
        similar = self.analyzer.find_similar_patents(
            self.patent1,
            patent_list,
            threshold=0,
            limit=5
        )

        self.assertIsInstance(similar, list)
        if similar:
            self.assertIsInstance(similar[0], tuple)
            self.assertEqual(len(similar[0]), 2)

    def test_generate_comparison_report(self):
        """비교 리포트 생성 테스트"""
        comparison = self.analyzer.compare_patents(self.patent1, self.patent2)
        report = self.analyzer.generate_comparison_report(comparison)

        self.assertIsInstance(report, str)
        self.assertIn("특허 비교 분석 리포트", report)
        self.assertIn("유사도 분석", report)


if __name__ == '__main__':
    unittest.main()
