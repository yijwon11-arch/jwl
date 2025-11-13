"""
KIPRIS (Korea Intellectual Property Rights Information Service) API 클라이언트
한국 특허청 특허정보검색서비스 API
"""

from typing import Dict, List, Optional, Any
import requests
from urllib.parse import urlencode
from .base import PatentAPIBase


class KiprisAPI(PatentAPIBase):
    """KIPRIS Open API 클라이언트"""

    def __init__(self, api_key: str, base_url: str = "http://plus.kipris.or.kr/openapi/rest"):
        """
        KIPRIS API 클라이언트 초기화

        Args:
            api_key: KIPRIS API 인증키
            base_url: API 기본 URL
        """
        super().__init__(api_key, base_url)
        self.search_endpoint = f"{base_url}/patUtiModInfoSearchSevice/patUtilModInfoSearch"

    def search(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        KIPRIS에서 특허 검색

        Args:
            query: 검색 쿼리
                - keyword: 검색 키워드
                - applicant: 출원인
                - inventor: 발명자
                - ipc: IPC 분류
                - application_date_start: 출원일 시작
                - application_date_end: 출원일 종료
            limit: 최대 결과 개수 (기본 100)

        Returns:
            검색된 특허 정보 리스트
        """
        params = {
            'ServiceKey': self.api_key,
            'numOfRows': limit,
            'pageNo': 1
        }

        # 검색 조건 추가
        if 'keyword' in query:
            params['word'] = query['keyword']

        if 'applicant' in query:
            params['applicant'] = query['applicant']

        if 'inventor' in query:
            params['inventor'] = query['inventor']

        if 'ipc' in query:
            params['ipc'] = query['ipc']

        if 'application_date_start' in query:
            params['applicationDateStart'] = query['application_date_start']

        if 'application_date_end' in query:
            params['applicationDateEnd'] = query['application_date_end']

        try:
            response = self._make_request('GET', self.search_endpoint, params=params)
            return self._parse_search_response(response)
        except Exception as e:
            print(f"KIPRIS 검색 오류: {str(e)}")
            return []

    def _parse_search_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        KIPRIS 검색 응답 파싱

        Args:
            response: API 응답 객체

        Returns:
            파싱된 특허 정보 리스트
        """
        try:
            data = response.json()

            # KIPRIS API 응답 구조에 따라 파싱
            if 'response' in data and 'body' in data['response']:
                items = data['response']['body'].get('items', {}).get('item', [])

                # 단일 결과인 경우 리스트로 변환
                if isinstance(items, dict):
                    items = [items]

                results = []
                for item in items:
                    patent_info = {
                        'id': item.get('applicationNumber', ''),
                        'title': item.get('inventionTitle', ''),
                        'application_number': item.get('applicationNumber', ''),
                        'application_date': item.get('applicationDate', ''),
                        'registration_number': item.get('registrationNumber', ''),
                        'registration_date': item.get('registrationDate', ''),
                        'applicant': item.get('applicantName', ''),
                        'inventor': item.get('inventorName', ''),
                        'ipc': item.get('ipcNumber', ''),
                        'abstract': item.get('astrtCont', ''),
                        'status': item.get('applicationStatus', ''),
                        'source': 'KIPRIS'
                    }
                    results.append(patent_info)

                return results

            return []
        except Exception as e:
            print(f"응답 파싱 오류: {str(e)}")
            return []

    def get_patent_detail(self, patent_id: str) -> Dict[str, Any]:
        """
        특허 상세 정보 조회

        Args:
            patent_id: 특허 출원번호

        Returns:
            특허 상세 정보
        """
        params = {
            'ServiceKey': self.api_key,
            'applicationNumber': patent_id
        }

        try:
            response = self._make_request('GET', self.search_endpoint, params=params)
            results = self._parse_search_response(response)
            return results[0] if results else {}
        except Exception as e:
            print(f"특허 상세 정보 조회 오류: {str(e)}")
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

    def search_by_applicant(self, applicant: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        출원인으로 특허 검색

        Args:
            applicant: 출원인명
            limit: 최대 결과 개수

        Returns:
            검색 결과 리스트
        """
        return self.search({'applicant': applicant}, limit)

    def search_by_ipc(self, ipc: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        IPC 분류로 특허 검색

        Args:
            ipc: IPC 분류 코드
            limit: 최대 결과 개수

        Returns:
            검색 결과 리스트
        """
        return self.search({'ipc': ipc}, limit)
