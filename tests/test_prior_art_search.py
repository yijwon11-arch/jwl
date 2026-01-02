"""
특허 선행기술 조사 시스템 테스트

주요 기능들을 테스트합니다.
"""

import sys
import unittest
from pathlib import Path

# src 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from patent_parser import PatentParser
from search_engine import PriorArtSearchEngine
from similarity_analyzer import SimilarityAnalyzer
from report_generator import ReportGenerator


class TestPatentParser(unittest.TestCase):
    """PatentParser 테스트"""

    def setUp(self):
        self.parser = PatentParser()

    def test_parse_basic_patent(self):
        """기본 특허 데이터 파싱 테스트"""
        patent_data = {
            'title': '인공지능 기반 이미지 처리 방법',
            'abstract': '본 발명은 인공지능을 이용한 이미지 처리 방법에 관한 것이다.',
            'claims': ['청구항 1: 이미지를 입력받는 단계']
        }

        parsed = self.parser.parse(patent_data)

        self.assertEqual(parsed['title'], patent_data['title'])
        self.assertEqual(parsed['abstract'], patent_data['abstract'])
        self.assertTrue(len(parsed['keywords']) > 0)

    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        patent_data = {
            'title': 'AI image processing method',
            'abstract': 'This invention relates to AI-based image processing.',
            'claims': []
        }

        keywords = self.parser.extract_keywords(patent_data, max_keywords=5)

        self.assertTrue(len(keywords) <= 5)
        self.assertIsInstance(keywords, list)

    def test_validate_patent_data(self):
        """특허 데이터 유효성 검증 테스트"""
        valid_data = {
            'title': '테스트 특허',
            'abstract': '테스트 초록'
        }

        invalid_data = {
            'title': '',
            'abstract': ''
        }

        self.assertTrue(self.parser.validate_patent_data(valid_data))
        self.assertFalse(self.parser.validate_patent_data(invalid_data))


class TestSearchEngine(unittest.TestCase):
    """PriorArtSearchEngine 테스트"""

    def setUp(self):
        self.search_engine = PriorArtSearchEngine(max_results=5)

    def test_search_returns_results(self):
        """검색 결과 반환 테스트"""
        results = self.search_engine.search('artificial intelligence', language='en')

        self.assertIsInstance(results, list)
        self.assertTrue(len(results) <= 5)

    def test_search_result_structure(self):
        """검색 결과 구조 테스트"""
        results = self.search_engine.search('machine learning', language='en')

        if results:
            result = results[0]
            self.assertIn('title', result)
            self.assertIn('abstract', result)
            self.assertIn('patent_number', result)
            self.assertIn('url', result)
            self.assertIn('source', result)


class TestSimilarityAnalyzer(unittest.TestCase):
    """SimilarityAnalyzer 테스트"""

    def setUp(self):
        self.analyzer = SimilarityAnalyzer()

    def test_analyze_similarity(self):
        """유사도 분석 테스트"""
        source_patent = {
            'title': '인공지능 기반 이미지 처리',
            'abstract': '본 발명은 딥러닝을 이용한 이미지 분석 기술이다.',
            'claims': ['청구항 1'],
            'keywords': ['인공지능', '이미지', '딥러닝']
        }

        candidate_patents = [
            {
                'title': '딥러닝 기반 이미지 인식',
                'abstract': '딥러닝 알고리즘을 사용한 이미지 인식 방법',
                'patent_number': 'TEST001'
            },
            {
                'title': '전혀 다른 기술',
                'abstract': '기계공학 분야의 새로운 발명',
                'patent_number': 'TEST002'
            }
        ]

        results = self.analyzer.analyze(source_patent, candidate_patents)

        self.assertEqual(len(results), 2)
        self.assertIn('similarity_score', results[0])
        self.assertIn('similarity_percentage', results[0])

        # 첫 번째 특허가 두 번째보다 유사도가 높아야 함
        self.assertGreater(
            results[0]['similarity_score'],
            results[1]['similarity_score']
        )

    def test_keyword_overlap(self):
        """키워드 중복도 계산 테스트"""
        patent1 = {
            'title': 'AI technology',
            'abstract': 'Artificial intelligence and machine learning',
            'keywords': ['ai', 'machine', 'learning']
        }

        patent2 = {
            'title': 'Machine learning system',
            'abstract': 'Deep learning and neural networks',
            'keywords': ['machine', 'learning', 'neural']
        }

        overlap, common = self.analyzer.calculate_keyword_overlap(patent1, patent2)

        self.assertGreater(overlap, 0)
        self.assertIsInstance(common, list)


class TestReportGenerator(unittest.TestCase):
    """ReportGenerator 테스트"""

    def setUp(self):
        self.report_gen = ReportGenerator()

    def test_generate_console_report(self):
        """콘솔 리포트 생성 테스트"""
        source_patent = {
            'title': '테스트 특허',
            'abstract': '테스트 초록',
            'keywords': ['키워드1', '키워드2']
        }

        results = [
            {
                'title': '관련 특허 1',
                'abstract': '관련 초록',
                'patent_number': 'TEST001',
                'similarity_score': 0.85,
                'similarity_percentage': '85.00%',
                'url': 'http://example.com',
                'source': 'Test'
            }
        ]

        report = self.report_gen.generate_console_report(source_patent, results)

        self.assertIsInstance(report, str)
        self.assertIn('특허 선행기술 조사 결과', report)
        self.assertIn('TEST001', report)

    def test_generate_json_report(self):
        """JSON 리포트 생성 테스트"""
        import json

        source_patent = {'title': '테스트', 'abstract': '초록'}
        results = []

        report = self.report_gen.generate_json_report(source_patent, results)

        # JSON 파싱이 가능한지 확인
        parsed = json.loads(report)
        self.assertIn('timestamp', parsed)
        self.assertIn('source_patent', parsed)
        self.assertIn('results', parsed)
        self.assertIn('statistics', parsed)

    def test_generate_summary(self):
        """요약 생성 테스트"""
        results = [
            {'similarity_score': 0.8},
            {'similarity_score': 0.5},
            {'similarity_score': 0.3}
        ]

        summary = self.report_gen.generate_summary(results)

        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['high_similarity'], 1)
        self.assertEqual(summary['medium_similarity'], 1)
        self.assertEqual(summary['low_similarity'], 1)


def run_tests():
    """테스트 실행"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
