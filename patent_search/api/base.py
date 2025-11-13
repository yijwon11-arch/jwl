"""
특허 검색 API 기본 클래스
Base class for patent search APIs
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime


class PatentAPIBase(ABC):
    """특허 검색 API 추상 기본 클래스"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        API 클라이언트 초기화

        Args:
            api_key: API 인증 키
            base_url: API 기본 URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """세션 설정"""
        self.session.headers.update({
            'User-Agent': 'PatentSearchSystem/0.1.0',
            'Accept': 'application/json'
        })

    @abstractmethod
    def search(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        특허 검색 수행

        Args:
            query: 검색 쿼리 딕셔너리
            limit: 최대 결과 개수

        Returns:
            검색 결과 리스트
        """
        pass

    @abstractmethod
    def get_patent_detail(self, patent_id: str) -> Dict[str, Any]:
        """
        특허 상세 정보 조회

        Args:
            patent_id: 특허 ID

        Returns:
            특허 상세 정보 딕셔너리
        """
        pass

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        HTTP 요청 수행

        Args:
            method: HTTP 메소드 (GET, POST 등)
            url: 요청 URL
            **kwargs: requests 추가 파라미터

        Returns:
            응답 객체

        Raises:
            requests.exceptions.RequestException: 요청 실패시
        """
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 요청 실패: {str(e)}")

    def close(self):
        """세션 종료"""
        self.session.close()

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
