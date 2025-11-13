"""
특허 검색 쿼리 빌더
Patent Search Query Builder
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from enum import Enum


class SearchField(Enum):
    """검색 필드 열거형"""
    KEYWORD = "keyword"
    TITLE = "title"
    ABSTRACT = "abstract"
    CLAIMS = "claims"
    APPLICANT = "applicant"
    INVENTOR = "inventor"
    IPC = "ipc"
    CPC = "cpc"
    APPLICATION_NUMBER = "application_number"
    REGISTRATION_NUMBER = "registration_number"


class PatentStatus(Enum):
    """특허 상태 열거형"""
    APPLICATION = "application"
    GRANT = "grant"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"


class QueryBuilder:
    """특허 검색 쿼리 빌더 클래스"""

    def __init__(self):
        """쿼리 빌더 초기화"""
        self.query: Dict[str, Any] = {}
        self.filters: List[Dict[str, Any]] = []

    def keyword(self, keyword: str, field: Optional[SearchField] = None) -> 'QueryBuilder':
        """
        키워드 검색 조건 추가

        Args:
            keyword: 검색 키워드
            field: 검색 필드 (없으면 전체 검색)

        Returns:
            QueryBuilder 인스턴스 (체이닝용)
        """
        if field:
            self.query[field.value] = keyword
        else:
            self.query['keyword'] = keyword
        return self

    def applicant(self, applicant_name: str) -> 'QueryBuilder':
        """
        출원인 검색 조건 추가

        Args:
            applicant_name: 출원인명

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['applicant'] = applicant_name
        return self

    def inventor(self, inventor_name: str) -> 'QueryBuilder':
        """
        발명자 검색 조건 추가

        Args:
            inventor_name: 발명자명

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['inventor'] = inventor_name
        return self

    def ipc_classification(self, ipc_code: str) -> 'QueryBuilder':
        """
        IPC 분류 검색 조건 추가

        Args:
            ipc_code: IPC 분류 코드 (예: H04L29/06)

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['ipc'] = ipc_code
        return self

    def cpc_classification(self, cpc_code: str) -> 'QueryBuilder':
        """
        CPC 분류 검색 조건 추가

        Args:
            cpc_code: CPC 분류 코드

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['cpc'] = cpc_code
        return self

    def application_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> 'QueryBuilder':
        """
        출원일 범위 검색 조건 추가

        Args:
            start_date: 시작일 (YYYYMMDD 또는 YYYY-MM-DD)
            end_date: 종료일 (YYYYMMDD 또는 YYYY-MM-DD)

        Returns:
            QueryBuilder 인스턴스
        """
        if start_date:
            self.query['application_date_start'] = self._normalize_date(start_date)
        if end_date:
            self.query['application_date_end'] = self._normalize_date(end_date)
        return self

    def registration_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> 'QueryBuilder':
        """
        등록일 범위 검색 조건 추가

        Args:
            start_date: 시작일
            end_date: 종료일

        Returns:
            QueryBuilder 인스턴스
        """
        if start_date:
            self.query['registration_date_start'] = self._normalize_date(start_date)
        if end_date:
            self.query['registration_date_end'] = self._normalize_date(end_date)
        return self

    def status(self, patent_status: PatentStatus) -> 'QueryBuilder':
        """
        특허 상태 조건 추가

        Args:
            patent_status: 특허 상태

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['status'] = patent_status.value.upper()
        return self

    def application_number(self, app_number: str) -> 'QueryBuilder':
        """
        출원번호로 검색

        Args:
            app_number: 출원번호

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['application_number'] = app_number
        return self

    def registration_number(self, reg_number: str) -> 'QueryBuilder':
        """
        등록번호로 검색

        Args:
            reg_number: 등록번호

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['registration_number'] = reg_number
        return self

    def country(self, country_code: str) -> 'QueryBuilder':
        """
        국가 코드 조건 추가

        Args:
            country_code: 국가 코드 (KR, US, JP, EP 등)

        Returns:
            QueryBuilder 인스턴스
        """
        self.query['country'] = country_code.upper()
        return self

    def add_custom_filter(self, field: str, value: Any) -> 'QueryBuilder':
        """
        사용자 정의 필터 추가

        Args:
            field: 필드명
            value: 값

        Returns:
            QueryBuilder 인스턴스
        """
        self.query[field] = value
        return self

    def _normalize_date(self, date_str: str) -> str:
        """
        날짜 문자열 정규화 (YYYYMMDD 형식으로 변환)

        Args:
            date_str: 날짜 문자열

        Returns:
            정규화된 날짜 문자열
        """
        # 하이픈 제거
        date_str = date_str.replace('-', '').replace('/', '')

        # 이미 YYYYMMDD 형식이면 그대로 반환
        if len(date_str) == 8 and date_str.isdigit():
            return date_str

        # YYYY 형식이면 0101 추가
        if len(date_str) == 4 and date_str.isdigit():
            return f"{date_str}0101"

        return date_str

    def build(self) -> Dict[str, Any]:
        """
        쿼리 딕셔너리 생성

        Returns:
            쿼리 딕셔너리
        """
        return self.query.copy()

    def reset(self) -> 'QueryBuilder':
        """
        쿼리 초기화

        Returns:
            QueryBuilder 인스턴스
        """
        self.query.clear()
        self.filters.clear()
        return self

    def __repr__(self) -> str:
        """문자열 표현"""
        return f"QueryBuilder(query={self.query})"


class AdvancedQueryBuilder(QueryBuilder):
    """고급 쿼리 빌더 (복잡한 검색 조건 지원)"""

    def __init__(self):
        """고급 쿼리 빌더 초기화"""
        super().__init__()
        self.boolean_operators: List[str] = []

    def and_keyword(self, keyword: str) -> 'AdvancedQueryBuilder':
        """
        AND 조건으로 키워드 추가

        Args:
            keyword: 검색 키워드

        Returns:
            AdvancedQueryBuilder 인스턴스
        """
        if 'keyword' in self.query:
            self.query['keyword'] = f"{self.query['keyword']} AND {keyword}"
        else:
            self.query['keyword'] = keyword
        return self

    def or_keyword(self, keyword: str) -> 'AdvancedQueryBuilder':
        """
        OR 조건으로 키워드 추가

        Args:
            keyword: 검색 키워드

        Returns:
            AdvancedQueryBuilder 인스턴스
        """
        if 'keyword' in self.query:
            self.query['keyword'] = f"{self.query['keyword']} OR {keyword}"
        else:
            self.query['keyword'] = keyword
        return self

    def not_keyword(self, keyword: str) -> 'AdvancedQueryBuilder':
        """
        NOT 조건으로 키워드 추가 (제외)

        Args:
            keyword: 제외할 키워드

        Returns:
            AdvancedQueryBuilder 인스턴스
        """
        if 'keyword' in self.query:
            self.query['keyword'] = f"{self.query['keyword']} NOT {keyword}"
        else:
            self.query['keyword'] = f"NOT {keyword}"
        return self

    def phrase(self, phrase: str) -> 'AdvancedQueryBuilder':
        """
        구문 검색 (완전 일치)

        Args:
            phrase: 검색 구문

        Returns:
            AdvancedQueryBuilder 인스턴스
        """
        quoted_phrase = f'"{phrase}"'
        if 'keyword' in self.query:
            self.query['keyword'] = f"{self.query['keyword']} {quoted_phrase}"
        else:
            self.query['keyword'] = quoted_phrase
        return self

    def proximity(self, word1: str, word2: str, distance: int = 5) -> 'AdvancedQueryBuilder':
        """
        근접 검색 (두 단어가 특정 거리 내에 있는 경우)

        Args:
            word1: 첫 번째 단어
            word2: 두 번째 단어
            distance: 최대 거리 (단어 수)

        Returns:
            AdvancedQueryBuilder 인스턴스
        """
        proximity_query = f'"{word1}" NEAR/{distance} "{word2}"'
        if 'keyword' in self.query:
            self.query['keyword'] = f"{self.query['keyword']} {proximity_query}"
        else:
            self.query['keyword'] = proximity_query
        return self
