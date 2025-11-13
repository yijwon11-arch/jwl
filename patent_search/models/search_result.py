"""
검색 결과 데이터 모델
Search Result Data Model
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from .patent import Patent


@dataclass
class SearchMetadata:
    """검색 메타데이터"""
    query: Dict[str, Any]
    total_results: int
    retrieved_count: int
    search_time: float  # 초 단위
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    page: int = 1
    limit: int = 100


@dataclass
class SearchResult:
    """검색 결과 클래스"""

    # 검색 메타데이터
    metadata: SearchMetadata

    # 검색된 특허 목록
    patents: List[Patent] = field(default_factory=list)

    # 검색 ID (고유 식별자)
    search_id: Optional[str] = None

    # 필터 및 정렬 정보
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    sort_by: Optional[str] = None

    # 추가 통계 정보
    statistics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """초기화 후 처리"""
        if self.search_id is None:
            # 타임스탬프 기반 검색 ID 생성
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            source = self.metadata.source[:3].upper()
            self.search_id = f"{source}_{timestamp}"

    def add_patent(self, patent: Patent) -> 'SearchResult':
        """특허 추가"""
        self.patents.append(patent)
        self.metadata.retrieved_count = len(self.patents)
        return self

    def get_patents(self) -> List[Patent]:
        """특허 목록 반환"""
        return self.patents

    def get_patent_by_id(self, patent_id: str) -> Optional[Patent]:
        """ID로 특허 검색"""
        for patent in self.patents:
            if patent.id == patent_id:
                return patent
        return None

    def filter_by_country(self, country: str) -> List[Patent]:
        """국가별 필터링"""
        return [p for p in self.patents if p.country == country.upper()]

    def filter_by_status(self, status: str) -> List[Patent]:
        """상태별 필터링"""
        return [p for p in self.patents if p.status == status]

    def filter_by_year(self, year: int) -> List[Patent]:
        """연도별 필터링"""
        return [
            p for p in self.patents
            if p.application_date and p.application_date.startswith(str(year))
        ]

    def sort_by_date(self, ascending: bool = False) -> 'SearchResult':
        """날짜순 정렬"""
        self.patents.sort(
            key=lambda p: p.application_date or '',
            reverse=not ascending
        )
        self.sort_by = f"date_{'asc' if ascending else 'desc'}"
        return self

    def sort_by_relevance(self) -> 'SearchResult':
        """관련성순 정렬 (기본 순서 유지)"""
        self.sort_by = "relevance"
        return self

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 생성"""
        stats = {
            'total_patents': len(self.patents),
            'countries': {},
            'status': {},
            'years': {},
            'ipc_classes': {},
        }

        for patent in self.patents:
            # 국가별 통계
            if patent.country:
                stats['countries'][patent.country] = \
                    stats['countries'].get(patent.country, 0) + 1

            # 상태별 통계
            if patent.status:
                stats['status'][patent.status] = \
                    stats['status'].get(patent.status, 0) + 1

            # 연도별 통계
            if patent.application_date:
                year = patent.application_date[:4]
                stats['years'][year] = stats['years'].get(year, 0) + 1

            # IPC 분류별 통계
            for ipc in patent.get_ipc_codes():
                main_class = ipc.split('/')[0] if '/' in ipc else ipc[:4]
                stats['ipc_classes'][main_class] = \
                    stats['ipc_classes'].get(main_class, 0) + 1

        self.statistics = stats
        return stats

    def get_top_applicants(self, limit: int = 10) -> List[tuple]:
        """주요 출원인 목록"""
        applicant_counts = {}

        for patent in self.patents:
            for applicant in patent.applicants:
                name = applicant.name
                applicant_counts[name] = applicant_counts.get(name, 0) + 1

        sorted_applicants = sorted(
            applicant_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_applicants[:limit]

    def get_top_inventors(self, limit: int = 10) -> List[tuple]:
        """주요 발명자 목록"""
        inventor_counts = {}

        for patent in self.patents:
            for inventor in patent.inventors:
                name = inventor.name
                inventor_counts[name] = inventor_counts.get(name, 0) + 1

        sorted_inventors = sorted(
            inventor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_inventors[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'search_id': self.search_id,
            'metadata': asdict(self.metadata),
            'patents': [p.to_dict() for p in self.patents],
            'filters_applied': self.filters_applied,
            'sort_by': self.sort_by,
            'statistics': self.statistics
        }

    def to_json(self, indent: int = 2) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """딕셔너리로부터 SearchResult 객체 생성"""
        metadata = SearchMetadata(**data['metadata'])
        patents = [Patent.from_dict(p) for p in data.get('patents', [])]

        return cls(
            metadata=metadata,
            patents=patents,
            search_id=data.get('search_id'),
            filters_applied=data.get('filters_applied', {}),
            sort_by=data.get('sort_by'),
            statistics=data.get('statistics', {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'SearchResult':
        """JSON 문자열로부터 SearchResult 객체 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def export_to_csv(self, filepath: str) -> None:
        """CSV 파일로 내보내기"""
        import csv

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if not self.patents:
                return

            # CSV 헤더
            fieldnames = [
                'id', 'title', 'application_number', 'application_date',
                'registration_number', 'registration_date',
                'status', 'country', 'source'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for patent in self.patents:
                row = {
                    'id': patent.id,
                    'title': patent.title,
                    'application_number': patent.application_number,
                    'application_date': patent.application_date,
                    'registration_number': patent.registration_number or '',
                    'registration_date': patent.registration_date or '',
                    'status': patent.status or '',
                    'country': patent.country or '',
                    'source': patent.source
                }
                writer.writerow(row)

    def __len__(self) -> int:
        """검색 결과 개수"""
        return len(self.patents)

    def __iter__(self):
        """반복자"""
        return iter(self.patents)

    def __getitem__(self, index: int) -> Patent:
        """인덱스로 특허 접근"""
        return self.patents[index]

    def __str__(self) -> str:
        """문자열 표현"""
        return (f"SearchResult(search_id={self.search_id}, "
                f"total={self.metadata.total_results}, "
                f"retrieved={self.metadata.retrieved_count})")

    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return (f"SearchResult(search_id={self.search_id}, "
                f"source={self.metadata.source}, "
                f"patents={len(self.patents)})")
