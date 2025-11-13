"""
Google Patents 검색 클라이언트
(웹 스크래핑 기반 - 공식 API는 제한적)
"""

from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from .base import PatentAPIBase


class GooglePatentsAPI(PatentAPIBase):
    """Google Patents 검색 클라이언트"""

    def __init__(self, base_url: str = "https://patents.google.com"):
        """
        Google Patents API 클라이언트 초기화

        Args:
            base_url: Google Patents 기본 URL
        """
        super().__init__(base_url=base_url)
        self.search_url = f"{base_url}/"

    def search(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Google Patents에서 특허 검색

        Args:
            query: 검색 쿼리
                - keyword: 검색 키워드
                - assignee: 양수인 (출원인)
                - inventor: 발명자
                - before: 이전 날짜 (YYYYMMDD)
                - after: 이후 날짜 (YYYYMMDD)
                - status: 특허 상태 (GRANT, APPLICATION)
            limit: 최대 결과 개수

        Returns:
            검색된 특허 정보 리스트
        """
        # 검색 쿼리 구성
        search_terms = []

        if 'keyword' in query:
            search_terms.append(query['keyword'])

        if 'assignee' in query:
            search_terms.append(f"assignee:({query['assignee']})")

        if 'inventor' in query:
            search_terms.append(f"inventor:({query['inventor']})")

        if 'before' in query:
            search_terms.append(f"before:{query['before']}")

        if 'after' in query:
            search_terms.append(f"after:{query['after']}")

        if 'status' in query:
            search_terms.append(f"status:{query['status']}")

        if not search_terms:
            return []

        query_string = ' '.join(search_terms)

        try:
            # 간단한 검색 구현 (실제로는 API 제한으로 제한적)
            # 실제 프로덕션에서는 공식 API 또는 라이센스가 필요
            params = {
                'q': query_string,
                'oq': query_string
            }

            response = self._make_request('GET', self.search_url, params=params)
            return self._parse_search_response(response, limit)

        except Exception as e:
            print(f"Google Patents 검색 오류: {str(e)}")
            return []

    def _parse_search_response(self, response: requests.Response, limit: int) -> List[Dict[str, Any]]:
        """
        검색 응답 파싱 (HTML 파싱)

        Args:
            response: HTTP 응답
            limit: 최대 결과 개수

        Returns:
            파싱된 특허 정보 리스트
        """
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            results = []

            # Google Patents HTML 구조에 따라 파싱
            # 실제 구조는 변경될 수 있으므로 주의 필요
            search_results = soup.find_all('search-result-item', limit=limit)

            for item in search_results:
                try:
                    patent_info = self._extract_patent_info(item)
                    if patent_info:
                        results.append(patent_info)
                except Exception as e:
                    continue

            return results

        except Exception as e:
            print(f"응답 파싱 오류: {str(e)}")
            return []

    def _extract_patent_info(self, element) -> Optional[Dict[str, Any]]:
        """
        HTML 요소에서 특허 정보 추출

        Args:
            element: BeautifulSoup 요소

        Returns:
            특허 정보 딕셔너리
        """
        try:
            # 기본 정보 추출 (실제 구조에 따라 조정 필요)
            patent_id = element.get('data-result-id', '')
            title_elem = element.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else ''

            abstract_elem = element.find('div', class_='abstract')
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''

            assignee_elem = element.find('span', class_='assignee')
            assignee = assignee_elem.get_text(strip=True) if assignee_elem else ''

            date_elem = element.find('span', class_='filing-date')
            filing_date = date_elem.get_text(strip=True) if date_elem else ''

            return {
                'id': patent_id,
                'title': title,
                'application_number': patent_id,
                'application_date': filing_date,
                'assignee': assignee,
                'abstract': abstract,
                'url': f"{self.base_url}/patent/{patent_id}",
                'source': 'Google Patents'
            }

        except Exception as e:
            return None

    def get_patent_detail(self, patent_id: str) -> Dict[str, Any]:
        """
        특허 상세 정보 조회

        Args:
            patent_id: 특허 ID (예: US1234567A)

        Returns:
            특허 상세 정보
        """
        url = f"{self.base_url}/patent/{patent_id}"

        try:
            response = self._make_request('GET', url)
            return self._parse_patent_detail(response, patent_id)

        except Exception as e:
            print(f"특허 상세 정보 조회 오류: {str(e)}")
            return {}

    def _parse_patent_detail(self, response: requests.Response, patent_id: str) -> Dict[str, Any]:
        """
        특허 상세 페이지 파싱

        Args:
            response: HTTP 응답
            patent_id: 특허 ID

        Returns:
            특허 상세 정보
        """
        try:
            soup = BeautifulSoup(response.text, 'lxml')

            # 제목
            title_elem = soup.find('meta', {'name': 'DC.title'})
            title = title_elem.get('content', '') if title_elem else ''

            # 초록
            abstract_elem = soup.find('meta', {'name': 'DC.description'})
            abstract = abstract_elem.get('content', '') if abstract_elem else ''

            # 발명자
            inventor_elem = soup.find('meta', {'name': 'DC.contributor'})
            inventor = inventor_elem.get('content', '') if inventor_elem else ''

            # 날짜
            date_elem = soup.find('meta', {'name': 'DC.date'})
            date = date_elem.get('content', '') if date_elem else ''

            return {
                'id': patent_id,
                'title': title,
                'abstract': abstract,
                'inventor': inventor,
                'publication_date': date,
                'url': f"{self.base_url}/patent/{patent_id}",
                'source': 'Google Patents'
            }

        except Exception as e:
            print(f"상세 정보 파싱 오류: {str(e)}")
            return {}

    def search_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        키워드로 특허 검색

        Args:
            keyword: 검색 키워드
            limit: 최대 결과 개수

        Returns:
            검색 결과 리스트
        """
        return self.search({'keyword': keyword}, limit)

    def search_by_assignee(self, assignee: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        양수인(출원인)으로 특허 검색

        Args:
            assignee: 양수인명
            limit: 최대 결과 개수

        Returns:
            검색 결과 리스트
        """
        return self.search({'assignee': assignee}, limit)
