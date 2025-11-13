"""
특허 모델 테스트
Patent Model Tests
"""

import unittest
from patent_search.models.patent import Patent, Inventor, Applicant, Classification


class TestPatent(unittest.TestCase):
    """Patent 모델 테스트 클래스"""

    def setUp(self):
        """각 테스트 전 실행"""
        self.patent = Patent(
            id="TEST001",
            title="테스트 특허",
            application_number="10-2023-0001234",
            application_date="2023-01-15",
            abstract="이것은 테스트 특허입니다.",
            source="TEST"
        )

    def test_patent_creation(self):
        """특허 생성 테스트"""
        self.assertEqual(self.patent.id, "TEST001")
        self.assertEqual(self.patent.title, "테스트 특허")
        self.assertEqual(self.patent.application_number, "10-2023-0001234")

    def test_add_inventor(self):
        """발명자 추가 테스트"""
        self.patent.add_inventor("홍길동", "KR")
        self.assertEqual(len(self.patent.inventors), 1)
        self.assertEqual(self.patent.inventors[0].name, "홍길동")

    def test_add_applicant(self):
        """출원인 추가 테스트"""
        self.patent.add_applicant("테스트 회사", "KR", "company")
        self.assertEqual(len(self.patent.applicants), 1)
        self.assertEqual(self.patent.applicants[0].name, "테스트 회사")

    def test_to_dict(self):
        """딕셔너리 변환 테스트"""
        patent_dict = self.patent.to_dict()
        self.assertIsInstance(patent_dict, dict)
        self.assertEqual(patent_dict['id'], "TEST001")
        self.assertEqual(patent_dict['title'], "테스트 특허")

    def test_from_dict(self):
        """딕셔너리로부터 생성 테스트"""
        patent_dict = self.patent.to_dict()
        new_patent = Patent.from_dict(patent_dict)
        self.assertEqual(new_patent.id, self.patent.id)
        self.assertEqual(new_patent.title, self.patent.title)

    def test_to_json_from_json(self):
        """JSON 변환 테스트"""
        json_str = self.patent.to_json()
        new_patent = Patent.from_json(json_str)
        self.assertEqual(new_patent.id, self.patent.id)
        self.assertEqual(new_patent.title, self.patent.title)

    def test_add_claim(self):
        """청구항 추가 테스트"""
        self.patent.add_claim(1, "청구항 1 내용")
        self.patent.add_claim(2, "청구항 2 내용", dependent_on=1)
        self.assertEqual(len(self.patent.claims), 2)
        self.assertEqual(self.patent.claims[1].dependent_on, 1)

    def test_ipc_codes(self):
        """IPC 코드 테스트"""
        self.patent.classifications = Classification(
            ipc=["H04L29/06", "G06F21/00"]
        )
        ipc_codes = self.patent.get_ipc_codes()
        self.assertEqual(len(ipc_codes), 2)
        self.assertEqual(self.patent.get_main_ipc(), "H04L29/06")


if __name__ == '__main__':
    unittest.main()
