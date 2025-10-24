"""
특허 문서 파싱 모듈

특허 제목, 초록, 청구항을 파싱하고 키워드를 추출합니다.
"""

import re
from typing import Dict, List, Optional
import json


class PatentParser:
    """특허 문서를 파싱하고 구조화하는 클래스"""

    def __init__(self):
        """PatentParser 초기화"""
        self.stop_words = {
            # 한국어 불용어
            '이', '그', '저', '것', '수', '등', '및', '또는', '에', '를', '을', '의', '가', '이다',
            '있다', '하는', '되는', '하다', '되다', '있는', '없는', '통해', '위한', '대한', '따른',
            # 영어 불용어
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could'
        }

    def parse(self, patent_data: Dict) -> Dict:
        """
        특허 데이터를 파싱합니다.

        Args:
            patent_data: 특허 정보를 담은 딕셔너리
                - title: 특허 제목
                - abstract: 초록
                - claims: 청구항 리스트
                - keywords: 선택적 키워드 리스트

        Returns:
            파싱된 특허 정보 딕셔너리
        """
        parsed = {
            'title': patent_data.get('title', ''),
            'abstract': patent_data.get('abstract', ''),
            'claims': patent_data.get('claims', []),
            'keywords': patent_data.get('keywords', [])
        }

        # 자동으로 키워드 추출 (제공되지 않은 경우)
        if not parsed['keywords']:
            parsed['keywords'] = self.extract_keywords(parsed)

        return parsed

    def parse_from_file(self, file_path: str) -> Dict:
        """
        JSON 파일에서 특허 데이터를 읽고 파싱합니다.

        Args:
            file_path: JSON 파일 경로

        Returns:
            파싱된 특허 정보 딕셔너리
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            patent_data = json.load(f)

        return self.parse(patent_data)

    def extract_keywords(self, patent_data: Dict, max_keywords: int = 20) -> List[str]:
        """
        특허 데이터에서 키워드를 추출합니다.

        Args:
            patent_data: 특허 정보 딕셔너리
            max_keywords: 추출할 최대 키워드 수

        Returns:
            추출된 키워드 리스트
        """
        # 모든 텍스트 결합
        text = ' '.join([
            patent_data.get('title', ''),
            patent_data.get('abstract', ''),
            ' '.join(patent_data.get('claims', []))
        ])

        # 단어 추출 (알파벳, 한글, 숫자만)
        words = re.findall(r'[a-zA-Z가-힣0-9]+', text.lower())

        # 불용어 제거 및 빈도 계산
        word_freq = {}
        for word in words:
            if len(word) > 1 and word not in self.stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # 상위 키워드 반환
        keywords = [word for word, freq in sorted_words[:max_keywords]]

        return keywords

    def get_search_query(self, patent_data: Dict) -> str:
        """
        특허 데이터로부터 검색 쿼리를 생성합니다.

        Args:
            patent_data: 특허 정보 딕셔너리

        Returns:
            검색 쿼리 문자열
        """
        # 키워드가 있으면 사용, 없으면 제목과 주요 키워드 사용
        if patent_data.get('keywords'):
            return ' '.join(patent_data['keywords'][:10])

        # 제목에서 주요 단어 추출
        title_words = re.findall(r'[a-zA-Z가-힣0-9]+', patent_data.get('title', ''))
        title_words = [w for w in title_words if w.lower() not in self.stop_words]

        # 초록에서 키워드 추출
        keywords = self.extract_keywords(patent_data, max_keywords=5)

        # 결합
        query_words = list(set(title_words[:5] + keywords[:5]))

        return ' '.join(query_words)

    def validate_patent_data(self, patent_data: Dict) -> bool:
        """
        특허 데이터의 유효성을 검증합니다.

        Args:
            patent_data: 특허 정보 딕셔너리

        Returns:
            유효하면 True, 아니면 False
        """
        # 최소한 제목이나 초록이 있어야 함
        has_title = bool(patent_data.get('title', '').strip())
        has_abstract = bool(patent_data.get('abstract', '').strip())

        return has_title or has_abstract
