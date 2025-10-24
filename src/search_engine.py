"""
선행기술 검색 엔진 모듈

Google Patents 및 기타 특허 데이터베이스를 검색합니다.
"""

import time
from typing import List, Dict, Optional
from urllib.parse import quote

# Optional imports - 설치되지 않은 경우 더미 데이터 사용
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class PriorArtSearchEngine:
    """선행기술을 검색하는 엔진 클래스"""

    def __init__(self, max_results: int = 10):
        """
        PriorArtSearchEngine 초기화

        Args:
            max_results: 반환할 최대 검색 결과 수
        """
        self.max_results = max_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search(self, query: str, language: str = 'ko') -> List[Dict]:
        """
        특허를 검색합니다.

        Args:
            query: 검색 쿼리
            language: 검색 언어 ('ko', 'en', 'any')

        Returns:
            검색된 특허 정보 리스트
        """
        results = []

        # Google Patents 검색 시뮬레이션
        # 실제 환경에서는 Google Patents Public Data API 또는 웹 스크래핑 사용
        google_results = self._search_google_patents(query, language)
        results.extend(google_results)

        return results[:self.max_results]

    def _search_google_patents(self, query: str, language: str) -> List[Dict]:
        """
        Google Patents에서 검색합니다.

        Args:
            query: 검색 쿼리
            language: 검색 언어

        Returns:
            검색된 특허 정보 리스트
        """
        results = []

        # 필수 라이브러리가 없으면 더미 데이터 반환
        if not HAS_REQUESTS or not HAS_BS4:
            print("참고: requests 또는 beautifulsoup4가 설치되지 않아 더미 데이터를 사용합니다.")
            return self._get_dummy_results(query)

        try:
            # Google Patents 검색 URL 구성
            encoded_query = quote(query)
            url = f"https://patents.google.com/?q={encoded_query}"

            if language == 'ko':
                url += "&country=KR"
            elif language == 'en':
                url += "&country=US"

            # 요청 전송
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')

            # 특허 결과 파싱 (실제 구조는 Google Patents 페이지 구조에 따라 달라짐)
            # 여기서는 시뮬레이션을 위한 기본 구조
            patent_items = soup.find_all('article', limit=self.max_results)

            for item in patent_items:
                try:
                    patent_info = self._parse_patent_item(item)
                    if patent_info:
                        results.append(patent_info)
                except Exception as e:
                    # 개별 항목 파싱 실패는 무시하고 계속 진행
                    continue

        except requests.RequestException as e:
            print(f"검색 중 오류 발생: {e}")
            # 네트워크 오류 시 더미 데이터 반환 (테스트용)
            results = self._get_dummy_results(query)

        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            results = self._get_dummy_results(query)

        return results

    def _parse_patent_item(self, item) -> Optional[Dict]:
        """
        특허 항목을 파싱합니다.

        Args:
            item: BeautifulSoup 특허 항목

        Returns:
            파싱된 특허 정보 또는 None
        """
        try:
            # 실제 Google Patents 구조에 맞게 수정 필요
            title_elem = item.find('h3') or item.find('a')
            title = title_elem.get_text(strip=True) if title_elem else "제목 없음"

            abstract_elem = item.find('p') or item.find('div', class_='abstract')
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else "초록 없음"

            link_elem = item.find('a', href=True)
            link = link_elem['href'] if link_elem else ""

            # 특허 번호 추출 (링크나 제목에서)
            patent_number = self._extract_patent_number(link or title)

            return {
                'title': title,
                'abstract': abstract,
                'patent_number': patent_number,
                'url': f"https://patents.google.com{link}" if link and not link.startswith('http') else link,
                'source': 'Google Patents'
            }

        except Exception:
            return None

    def _extract_patent_number(self, text: str) -> str:
        """
        텍스트에서 특허 번호를 추출합니다.

        Args:
            text: 추출할 텍스트

        Returns:
            특허 번호
        """
        import re

        # US 특허 패턴
        us_pattern = r'US[\s-]?(\d{7,10})'
        # KR 특허 패턴
        kr_pattern = r'KR[\s-]?(\d{7,10})'
        # 일반 번호 패턴
        general_pattern = r'[A-Z]{2}[\s-]?\d{7,10}'

        for pattern in [us_pattern, kr_pattern, general_pattern]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return "번호 없음"

    def _get_dummy_results(self, query: str) -> List[Dict]:
        """
        테스트용 더미 검색 결과를 반환합니다.

        Args:
            query: 검색 쿼리

        Returns:
            더미 특허 정보 리스트
        """
        # 실제 검색 실패 시 또는 테스트용으로 사용
        return [
            {
                'title': f'관련 특허 1: {query[:30]}...',
                'abstract': '이 특허는 관련 기술에 대한 설명을 포함합니다. ' * 3,
                'patent_number': 'US1234567',
                'url': 'https://patents.google.com/patent/US1234567',
                'source': 'Google Patents (Dummy)'
            },
            {
                'title': f'관련 특허 2: {query[:30]}...',
                'abstract': '이 특허는 유사한 기술적 특징을 설명합니다. ' * 3,
                'patent_number': 'KR1020210001234',
                'url': 'https://patents.google.com/patent/KR1020210001234',
                'source': 'Google Patents (Dummy)'
            },
            {
                'title': f'관련 특허 3: {query[:30]}...',
                'abstract': '본 발명은 개선된 방법을 제공합니다. ' * 3,
                'patent_number': 'US2345678',
                'url': 'https://patents.google.com/patent/US2345678',
                'source': 'Google Patents (Dummy)'
            }
        ]

    def search_by_classification(self, classification_code: str) -> List[Dict]:
        """
        특허 분류 코드로 검색합니다.

        Args:
            classification_code: IPC 또는 CPC 분류 코드

        Returns:
            검색된 특허 정보 리스트
        """
        # 분류 코드 기반 검색 (실제 API 사용 시 구현)
        query = f"classification:{classification_code}"
        return self.search(query)

    def get_patent_details(self, patent_number: str) -> Optional[Dict]:
        """
        특허 번호로 상세 정보를 조회합니다.

        Args:
            patent_number: 특허 번호

        Returns:
            특허 상세 정보 또는 None
        """
        try:
            url = f"https://patents.google.com/patent/{patent_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 상세 정보 파싱 (실제 구조에 맞게 수정 필요)
            title = soup.find('h1')
            abstract = soup.find('div', {'class': 'abstract'})

            return {
                'title': title.get_text(strip=True) if title else '',
                'abstract': abstract.get_text(strip=True) if abstract else '',
                'patent_number': patent_number,
                'url': url
            }

        except Exception as e:
            print(f"특허 상세 정보 조회 실패: {e}")
            return None
