"""
특허 데이터 모델
Patent Data Model
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Inventor:
    """발명자 정보"""
    name: str
    country: Optional[str] = None
    address: Optional[str] = None


@dataclass
class Applicant:
    """출원인 정보"""
    name: str
    country: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None  # individual, company, university, etc.


@dataclass
class Classification:
    """특허 분류 정보"""
    ipc: Optional[List[str]] = field(default_factory=list)  # International Patent Classification
    cpc: Optional[List[str]] = field(default_factory=list)  # Cooperative Patent Classification
    uspc: Optional[List[str]] = field(default_factory=list)  # US Patent Classification


@dataclass
class Citation:
    """인용 특허 정보"""
    patent_number: str
    title: Optional[str] = None
    date: Optional[str] = None
    type: str = "patent"  # patent, non-patent


@dataclass
class Claim:
    """청구항 정보"""
    number: int
    text: str
    dependent_on: Optional[int] = None  # 종속항인 경우 독립항 번호


@dataclass
class Patent:
    """특허 정보 클래스"""

    # 기본 식별 정보
    id: str
    title: str
    application_number: str
    application_date: str

    # 선택적 기본 정보
    publication_number: Optional[str] = None
    publication_date: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[str] = None

    # 내용 정보
    abstract: Optional[str] = None
    description: Optional[str] = None
    claims_text: Optional[str] = None

    # 관계자 정보
    inventors: List[Inventor] = field(default_factory=list)
    applicants: List[Applicant] = field(default_factory=list)

    # 분류 정보
    classifications: Optional[Classification] = None

    # 법적 상태
    status: Optional[str] = None  # pending, granted, expired, rejected, withdrawn
    country: Optional[str] = None

    # 인용 정보
    citations: List[Citation] = field(default_factory=list)
    cited_by: List[Citation] = field(default_factory=list)

    # 청구항
    claims: List[Claim] = field(default_factory=list)

    # 기타 정보
    priority_date: Optional[str] = None
    priority_number: Optional[str] = None
    family_id: Optional[str] = None
    url: Optional[str] = None
    source: str = "Unknown"  # KIPRIS, Google Patents, USPTO, etc.

    # 메타데이터
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patent':
        """딕셔너리로부터 Patent 객체 생성"""
        # 중첩된 객체 변환
        if 'inventors' in data and isinstance(data['inventors'], list):
            data['inventors'] = [
                Inventor(**inv) if isinstance(inv, dict) else inv
                for inv in data['inventors']
            ]

        if 'applicants' in data and isinstance(data['applicants'], list):
            data['applicants'] = [
                Applicant(**app) if isinstance(app, dict) else app
                for app in data['applicants']
            ]

        if 'classifications' in data and isinstance(data['classifications'], dict):
            data['classifications'] = Classification(**data['classifications'])

        if 'citations' in data and isinstance(data['citations'], list):
            data['citations'] = [
                Citation(**cit) if isinstance(cit, dict) else cit
                for cit in data['citations']
            ]

        if 'cited_by' in data and isinstance(data['cited_by'], list):
            data['cited_by'] = [
                Citation(**cit) if isinstance(cit, dict) else cit
                for cit in data['cited_by']
            ]

        if 'claims' in data and isinstance(data['claims'], list):
            data['claims'] = [
                Claim(**clm) if isinstance(clm, dict) else clm
                for clm in data['claims']
            ]

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Patent':
        """JSON 문자열로부터 Patent 객체 생성"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_inventor(self, name: str, country: Optional[str] = None) -> 'Patent':
        """발명자 추가"""
        self.inventors.append(Inventor(name=name, country=country))
        return self

    def add_applicant(self, name: str, country: Optional[str] = None,
                     applicant_type: Optional[str] = None) -> 'Patent':
        """출원인 추가"""
        self.applicants.append(Applicant(name=name, country=country, type=applicant_type))
        return self

    def add_citation(self, patent_number: str, title: Optional[str] = None) -> 'Patent':
        """인용 특허 추가"""
        self.citations.append(Citation(patent_number=patent_number, title=title))
        return self

    def add_claim(self, number: int, text: str, dependent_on: Optional[int] = None) -> 'Patent':
        """청구항 추가"""
        self.claims.append(Claim(number=number, text=text, dependent_on=dependent_on))
        return self

    def get_ipc_codes(self) -> List[str]:
        """IPC 코드 목록 반환"""
        if self.classifications and self.classifications.ipc:
            return self.classifications.ipc
        return []

    def get_main_ipc(self) -> Optional[str]:
        """주 IPC 코드 반환"""
        ipc_codes = self.get_ipc_codes()
        return ipc_codes[0] if ipc_codes else None

    def is_granted(self) -> bool:
        """등록 여부 확인"""
        return self.status == 'granted' or bool(self.registration_number)

    def get_age_in_days(self) -> Optional[int]:
        """출원 후 경과 일수"""
        try:
            app_date = datetime.fromisoformat(self.application_date.replace('/', '-'))
            return (datetime.now() - app_date).days
        except:
            return None

    def __str__(self) -> str:
        """문자열 표현"""
        return f"Patent(id={self.id}, title={self.title[:50]}...)"

    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return (f"Patent(id={self.id}, application_number={self.application_number}, "
                f"title={self.title[:30]}...)")
