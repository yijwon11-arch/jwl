"""
리포트 생성 모듈

선행기술 조사 결과를 다양한 형식으로 출력합니다.
"""

from typing import List, Dict
import json
from datetime import datetime


class ReportGenerator:
    """선행기술 조사 결과 리포트를 생성하는 클래스"""

    def __init__(self):
        """ReportGenerator 초기화"""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_console_report(
        self,
        source_patent: Dict,
        results: List[Dict],
        top_n: int = 10
    ) -> str:
        """
        콘솔 출력용 리포트를 생성합니다.

        Args:
            source_patent: 원본 특허 정보
            results: 검색 결과 리스트 (유사도 점수 포함)
            top_n: 출력할 결과 수

        Returns:
            포맷팅된 리포트 문자열
        """
        lines = []
        lines.append("=" * 80)
        lines.append("특허 선행기술 조사 결과")
        lines.append("=" * 80)
        lines.append(f"조사 일시: {self.timestamp}")
        lines.append("")

        # 원본 특허 정보
        lines.append("[ 조사 대상 특허 ]")
        lines.append(f"제목: {source_patent.get('title', 'N/A')}")
        lines.append(f"초록: {source_patent.get('abstract', 'N/A')[:200]}...")
        lines.append("")

        # 검색 결과
        lines.append(f"[ 발견된 선행기술 ({len(results)}건 중 상위 {min(top_n, len(results))}건) ]")
        lines.append("")

        for i, patent in enumerate(results[:top_n], 1):
            lines.append(f"{i}. {patent.get('title', 'N/A')}")
            lines.append(f"   특허번호: {patent.get('patent_number', 'N/A')}")
            lines.append(f"   유사도: {patent.get('similarity_percentage', 'N/A')}")
            lines.append(f"   출처: {patent.get('source', 'N/A')}")

            # 초록 (일부만)
            abstract = patent.get('abstract', 'N/A')
            if len(abstract) > 150:
                abstract = abstract[:150] + "..."
            lines.append(f"   초록: {abstract}")

            # URL
            if patent.get('url'):
                lines.append(f"   URL: {patent.get('url')}")

            lines.append("")

        # 통계
        lines.append("=" * 80)
        lines.append("[ 통계 ]")
        lines.append(f"총 발견 특허 수: {len(results)}")

        if results:
            avg_similarity = sum(r.get('similarity_score', 0) for r in results) / len(results)
            lines.append(f"평균 유사도: {avg_similarity * 100:.2f}%")

            high_similarity = [r for r in results if r.get('similarity_score', 0) > 0.5]
            lines.append(f"고유사도 특허 (>50%): {len(high_similarity)}건")

        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_json_report(
        self,
        source_patent: Dict,
        results: List[Dict]
    ) -> str:
        """
        JSON 형식의 리포트를 생성합니다.

        Args:
            source_patent: 원본 특허 정보
            results: 검색 결과 리스트

        Returns:
            JSON 문자열
        """
        report = {
            'timestamp': self.timestamp,
            'source_patent': {
                'title': source_patent.get('title', ''),
                'abstract': source_patent.get('abstract', ''),
                'claims': source_patent.get('claims', []),
                'keywords': source_patent.get('keywords', [])
            },
            'results': results,
            'statistics': {
                'total_results': len(results),
                'average_similarity': self._calculate_average_similarity(results),
                'high_similarity_count': len([r for r in results if r.get('similarity_score', 0) > 0.5])
            }
        }

        return json.dumps(report, ensure_ascii=False, indent=2)

    def generate_markdown_report(
        self,
        source_patent: Dict,
        results: List[Dict],
        top_n: int = 10
    ) -> str:
        """
        Markdown 형식의 리포트를 생성합니다.

        Args:
            source_patent: 원본 특허 정보
            results: 검색 결과 리스트
            top_n: 출력할 결과 수

        Returns:
            Markdown 문자열
        """
        lines = []
        lines.append("# 특허 선행기술 조사 결과")
        lines.append("")
        lines.append(f"**조사 일시**: {self.timestamp}")
        lines.append("")

        # 원본 특허 정보
        lines.append("## 조사 대상 특허")
        lines.append("")
        lines.append(f"**제목**: {source_patent.get('title', 'N/A')}")
        lines.append("")
        lines.append(f"**초록**: {source_patent.get('abstract', 'N/A')}")
        lines.append("")

        if source_patent.get('keywords'):
            lines.append(f"**키워드**: {', '.join(source_patent['keywords'][:10])}")
            lines.append("")

        # 검색 결과
        lines.append(f"## 발견된 선행기술 (상위 {min(top_n, len(results))}건)")
        lines.append("")

        for i, patent in enumerate(results[:top_n], 1):
            lines.append(f"### {i}. {patent.get('title', 'N/A')}")
            lines.append("")
            lines.append(f"- **특허번호**: {patent.get('patent_number', 'N/A')}")
            lines.append(f"- **유사도**: {patent.get('similarity_percentage', 'N/A')}")
            lines.append(f"- **출처**: {patent.get('source', 'N/A')}")

            if patent.get('url'):
                lines.append(f"- **URL**: [{patent['url']}]({patent['url']})")

            lines.append("")
            lines.append(f"**초록**: {patent.get('abstract', 'N/A')}")
            lines.append("")

        # 통계
        lines.append("## 통계")
        lines.append("")
        lines.append(f"- **총 발견 특허 수**: {len(results)}건")

        if results:
            avg_similarity = self._calculate_average_similarity(results)
            lines.append(f"- **평균 유사도**: {avg_similarity * 100:.2f}%")

            high_similarity = [r for r in results if r.get('similarity_score', 0) > 0.5]
            lines.append(f"- **고유사도 특허** (>50%): {len(high_similarity)}건")

        lines.append("")

        return "\n".join(lines)

    def save_report(
        self,
        report_content: str,
        filename: str,
        format: str = 'txt'
    ) -> None:
        """
        리포트를 파일로 저장합니다.

        Args:
            report_content: 리포트 내용
            filename: 파일명 (확장자 제외)
            format: 파일 형식 ('txt', 'json', 'md')
        """
        extension = format if format.startswith('.') else f'.{format}'
        full_filename = f"{filename}{extension}"

        with open(full_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"리포트가 저장되었습니다: {full_filename}")

    def _calculate_average_similarity(self, results: List[Dict]) -> float:
        """
        결과의 평균 유사도를 계산합니다.

        Args:
            results: 검색 결과 리스트

        Returns:
            평균 유사도
        """
        if not results:
            return 0.0

        total = sum(r.get('similarity_score', 0) for r in results)
        return total / len(results)

    def generate_summary(self, results: List[Dict]) -> Dict:
        """
        결과 요약을 생성합니다.

        Args:
            results: 검색 결과 리스트

        Returns:
            요약 정보 딕셔너리
        """
        if not results:
            return {
                'total': 0,
                'high_similarity': 0,
                'medium_similarity': 0,
                'low_similarity': 0,
                'average_similarity': 0.0
            }

        high = len([r for r in results if r.get('similarity_score', 0) > 0.7])
        medium = len([r for r in results if 0.4 <= r.get('similarity_score', 0) <= 0.7])
        low = len([r for r in results if r.get('similarity_score', 0) < 0.4])

        return {
            'total': len(results),
            'high_similarity': high,
            'medium_similarity': medium,
            'low_similarity': low,
            'average_similarity': self._calculate_average_similarity(results)
        }
