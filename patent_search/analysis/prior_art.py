"""
선행기술 비교 분석 모듈
Prior Art Comparison and Analysis Module
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from collections import Counter
import re

from ..models.patent import Patent


@dataclass
class SimilarityScore:
    """유사도 점수"""
    overall: float  # 전체 유사도 (0-100)
    title: float  # 제목 유사도
    abstract: float  # 초록 유사도
    ipc: float  # IPC 분류 유사도
    applicant: float  # 출원인 유사도


@dataclass
class ComparisonResult:
    """특허 비교 결과"""
    patent1: Patent
    patent2: Patent
    similarity: SimilarityScore
    common_keywords: List[str]
    common_ipc: List[str]
    differences: Dict[str, Any]


class PriorArtAnalyzer:
    """선행기술 분석 클래스"""

    def __init__(self):
        """분석기 초기화"""
        self.stop_words = self._load_stop_words()

    def _load_stop_words(self) -> set:
        """불용어 로드"""
        # 기본 불용어 (실제로는 파일에서 로드하거나 더 확장 가능)
        korean_stop_words = {
            '이', '그', '저', '것', '수', '등', '및', '또는', '이다', '있다',
            '하다', '되다', '위한', '통해', '대한', '관한', '따른', '의한'
        }
        english_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are'
        }
        return korean_stop_words | english_stop_words

    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """
        텍스트에서 키워드 추출

        Args:
            text: 입력 텍스트
            min_length: 최소 키워드 길이

        Returns:
            키워드 리스트
        """
        if not text:
            return []

        # 소문자 변환 및 특수문자 제거
        text = text.lower()
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        # 단어 분리
        words = text.split()

        # 불용어 제거 및 최소 길이 필터링
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) >= min_length
        ]

        return keywords

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트의 유사도 계산 (Jaccard similarity)

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트

        Returns:
            유사도 (0-100)
        """
        if not text1 or not text2:
            return 0.0

        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = keywords1 & keywords2
        union = keywords1 | keywords2

        jaccard_similarity = len(intersection) / len(union) if union else 0
        return round(jaccard_similarity * 100, 2)

    def calculate_ipc_similarity(self, ipc_list1: List[str], ipc_list2: List[str]) -> float:
        """
        IPC 분류 유사도 계산

        Args:
            ipc_list1: 첫 번째 IPC 리스트
            ipc_list2: 두 번째 IPC 리스트

        Returns:
            유사도 (0-100)
        """
        if not ipc_list1 or not ipc_list2:
            return 0.0

        # IPC 코드를 계층적으로 비교
        def normalize_ipc(ipc: str) -> List[str]:
            """IPC를 계층 레벨로 분리"""
            # 예: H04L29/06 -> ['H', 'H04', 'H04L', 'H04L29', 'H04L29/06']
            levels = []
            if len(ipc) >= 1:
                levels.append(ipc[0])  # Section
            if len(ipc) >= 3:
                levels.append(ipc[:3])  # Class
            if len(ipc) >= 4:
                levels.append(ipc[:4])  # Subclass
            if '/' in ipc:
                main_group = ipc.split('/')[0]
                levels.append(main_group)
            levels.append(ipc)  # Full IPC
            return levels

        # 모든 계층 레벨 추출
        set1 = set()
        for ipc in ipc_list1:
            set1.update(normalize_ipc(ipc))

        set2 = set()
        for ipc in ipc_list2:
            set2.update(normalize_ipc(ipc))

        if not set1 or not set2:
            return 0.0

        intersection = set1 & set2
        union = set1 | set2

        similarity = len(intersection) / len(union) if union else 0
        return round(similarity * 100, 2)

    def compare_patents(self, patent1: Patent, patent2: Patent) -> ComparisonResult:
        """
        두 특허 비교

        Args:
            patent1: 첫 번째 특허
            patent2: 두 번째 특허

        Returns:
            비교 결과
        """
        # 제목 유사도
        title_sim = self.calculate_text_similarity(
            patent1.title,
            patent2.title
        )

        # 초록 유사도
        abstract_sim = self.calculate_text_similarity(
            patent1.abstract or '',
            patent2.abstract or ''
        )

        # IPC 유사도
        ipc_sim = self.calculate_ipc_similarity(
            patent1.get_ipc_codes(),
            patent2.get_ipc_codes()
        )

        # 출원인 유사도
        applicant1_names = {a.name.lower() for a in patent1.applicants}
        applicant2_names = {a.name.lower() for a in patent2.applicants}

        if applicant1_names and applicant2_names:
            applicant_intersection = applicant1_names & applicant2_names
            applicant_union = applicant1_names | applicant2_names
            applicant_sim = (len(applicant_intersection) / len(applicant_union)) * 100
        else:
            applicant_sim = 0.0

        # 전체 유사도 (가중 평균)
        overall_sim = (
            title_sim * 0.3 +
            abstract_sim * 0.4 +
            ipc_sim * 0.2 +
            applicant_sim * 0.1
        )

        similarity = SimilarityScore(
            overall=round(overall_sim, 2),
            title=title_sim,
            abstract=abstract_sim,
            ipc=ipc_sim,
            applicant=round(applicant_sim, 2)
        )

        # 공통 키워드
        keywords1 = set(self.extract_keywords(
            f"{patent1.title} {patent1.abstract or ''}"
        ))
        keywords2 = set(self.extract_keywords(
            f"{patent2.title} {patent2.abstract or ''}"
        ))
        common_keywords = list(keywords1 & keywords2)

        # 공통 IPC
        common_ipc = list(
            set(patent1.get_ipc_codes()) & set(patent2.get_ipc_codes())
        )

        # 차이점
        differences = {
            'country': (patent1.country, patent2.country),
            'status': (patent1.status, patent2.status),
            'application_date': (patent1.application_date, patent2.application_date),
        }

        return ComparisonResult(
            patent1=patent1,
            patent2=patent2,
            similarity=similarity,
            common_keywords=common_keywords[:20],  # 상위 20개만
            common_ipc=common_ipc,
            differences=differences
        )

    def find_similar_patents(
        self,
        target_patent: Patent,
        patent_list: List[Patent],
        threshold: float = 30.0,
        limit: int = 10
    ) -> List[Tuple[Patent, float]]:
        """
        유사 특허 찾기

        Args:
            target_patent: 대상 특허
            patent_list: 비교할 특허 리스트
            threshold: 최소 유사도 임계값
            limit: 최대 결과 개수

        Returns:
            (특허, 유사도) 튜플 리스트
        """
        similarities = []

        for patent in patent_list:
            if patent.id == target_patent.id:
                continue

            comparison = self.compare_patents(target_patent, patent)
            if comparison.similarity.overall >= threshold:
                similarities.append((patent, comparison.similarity.overall))

        # 유사도 내림차순 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:limit]

    def analyze_patent_family(
        self,
        patents: List[Patent]
    ) -> Dict[str, Any]:
        """
        특허군 분석

        Args:
            patents: 특허 리스트

        Returns:
            분석 결과 딕셔너리
        """
        if not patents:
            return {}

        # 전체 키워드 추출
        all_keywords = []
        for patent in patents:
            text = f"{patent.title} {patent.abstract or ''}"
            keywords = self.extract_keywords(text)
            all_keywords.extend(keywords)

        # 키워드 빈도 분석
        keyword_freq = Counter(all_keywords)
        top_keywords = keyword_freq.most_common(30)

        # IPC 분류 분석
        all_ipc = []
        for patent in patents:
            all_ipc.extend(patent.get_ipc_codes())

        ipc_freq = Counter(all_ipc)
        top_ipc = ipc_freq.most_common(10)

        # 출원인 분석
        all_applicants = []
        for patent in patents:
            for applicant in patent.applicants:
                all_applicants.append(applicant.name)

        applicant_freq = Counter(all_applicants)
        top_applicants = applicant_freq.most_common(10)

        # 연도별 분석
        year_freq = Counter()
        for patent in patents:
            if patent.application_date:
                year = patent.application_date[:4]
                year_freq[year] += 1

        return {
            'total_patents': len(patents),
            'top_keywords': top_keywords,
            'top_ipc_classes': top_ipc,
            'top_applicants': top_applicants,
            'year_distribution': dict(year_freq.most_common()),
            'countries': Counter([p.country for p in patents if p.country]).most_common(),
            'status_distribution': Counter([p.status for p in patents if p.status]).most_common()
        }

    def generate_comparison_report(
        self,
        comparison: ComparisonResult
    ) -> str:
        """
        비교 리포트 생성

        Args:
            comparison: 비교 결과

        Returns:
            텍스트 리포트
        """
        p1 = comparison.patent1
        p2 = comparison.patent2
        sim = comparison.similarity

        report = []
        report.append("=" * 80)
        report.append("특허 비교 분석 리포트")
        report.append("=" * 80)
        report.append("")

        report.append("■ 특허 1")
        report.append(f"  ID: {p1.id}")
        report.append(f"  제목: {p1.title}")
        report.append(f"  출원번호: {p1.application_number}")
        report.append(f"  출원일: {p1.application_date}")
        report.append("")

        report.append("■ 특허 2")
        report.append(f"  ID: {p2.id}")
        report.append(f"  제목: {p2.title}")
        report.append(f"  출원번호: {p2.application_number}")
        report.append(f"  출원일: {p2.application_date}")
        report.append("")

        report.append("■ 유사도 분석")
        report.append(f"  전체 유사도: {sim.overall}%")
        report.append(f"  제목 유사도: {sim.title}%")
        report.append(f"  초록 유사도: {sim.abstract}%")
        report.append(f"  IPC 유사도: {sim.ipc}%")
        report.append(f"  출원인 유사도: {sim.applicant}%")
        report.append("")

        if comparison.common_keywords:
            report.append("■ 공통 키워드")
            report.append(f"  {', '.join(comparison.common_keywords)}")
            report.append("")

        if comparison.common_ipc:
            report.append("■ 공통 IPC 분류")
            report.append(f"  {', '.join(comparison.common_ipc)}")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)
