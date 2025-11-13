"""
쿼리 빌더 테스트
Query Builder Tests
"""

import unittest
from patent_search.query.query_builder import QueryBuilder, AdvancedQueryBuilder, SearchField, PatentStatus


class TestQueryBuilder(unittest.TestCase):
    """QueryBuilder 테스트 클래스"""

    def setUp(self):
        """각 테스트 전 실행"""
        self.builder = QueryBuilder()

    def test_keyword_query(self):
        """키워드 검색 테스트"""
        query = self.builder.keyword("인공지능").build()
        self.assertEqual(query['keyword'], "인공지능")

    def test_applicant_query(self):
        """출원인 검색 테스트"""
        query = self.builder.applicant("삼성전자").build()
        self.assertEqual(query['applicant'], "삼성전자")

    def test_inventor_query(self):
        """발명자 검색 테스트"""
        query = self.builder.inventor("홍길동").build()
        self.assertEqual(query['inventor'], "홍길동")

    def test_ipc_query(self):
        """IPC 분류 검색 테스트"""
        query = self.builder.ipc_classification("H04L29/06").build()
        self.assertEqual(query['ipc'], "H04L29/06")

    def test_date_range_query(self):
        """날짜 범위 검색 테스트"""
        query = self.builder.application_date_range("2020-01-01", "2023-12-31").build()
        self.assertEqual(query['application_date_start'], "20200101")
        self.assertEqual(query['application_date_end'], "20231231")

    def test_country_query(self):
        """국가 검색 테스트"""
        query = self.builder.country("kr").build()
        self.assertEqual(query['country'], "KR")

    def test_chained_query(self):
        """체인 쿼리 테스트"""
        query = (self.builder
                 .keyword("머신러닝")
                 .applicant("엘지전자")
                 .country("KR")
                 .build())

        self.assertEqual(query['keyword'], "머신러닝")
        self.assertEqual(query['applicant'], "엘지전자")
        self.assertEqual(query['country'], "KR")

    def test_reset_query(self):
        """쿼리 초기화 테스트"""
        self.builder.keyword("테스트").applicant("회사명")
        self.builder.reset()
        query = self.builder.build()
        self.assertEqual(len(query), 0)


class TestAdvancedQueryBuilder(unittest.TestCase):
    """AdvancedQueryBuilder 테스트 클래스"""

    def setUp(self):
        """각 테스트 전 실행"""
        self.builder = AdvancedQueryBuilder()

    def test_and_keyword(self):
        """AND 조건 테스트"""
        query = self.builder.and_keyword("AI").and_keyword("machine learning").build()
        self.assertIn("AND", query['keyword'])

    def test_or_keyword(self):
        """OR 조건 테스트"""
        query = self.builder.or_keyword("AI").or_keyword("인공지능").build()
        self.assertIn("OR", query['keyword'])

    def test_phrase_search(self):
        """구문 검색 테스트"""
        query = self.builder.phrase("deep learning algorithm").build()
        self.assertIn('"', query['keyword'])


if __name__ == '__main__':
    unittest.main()
