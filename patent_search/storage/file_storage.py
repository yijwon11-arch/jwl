"""
파일 기반 저장 모듈
File-based Storage Module
"""

import json
import csv
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from ..models.patent import Patent
from ..models.search_result import SearchResult


class FileStorage:
    """파일 기반 저장 관리 클래스"""

    def __init__(self, base_path: str = "data/exports"):
        """
        파일 저장소 초기화

        Args:
            base_path: 기본 저장 경로
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_search_result_json(
        self,
        search_result: SearchResult,
        filename: Optional[str] = None
    ) -> str:
        """
        검색 결과를 JSON 파일로 저장

        Args:
            search_result: SearchResult 객체
            filename: 파일명 (없으면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"search_result_{timestamp}.json"

        filepath = self.base_path / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(search_result.to_dict(), f, ensure_ascii=False, indent=2)

            print(f"검색 결과 저장 완료: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"JSON 저장 오류: {str(e)}")
            raise

    def load_search_result_json(self, filepath: str) -> Optional[SearchResult]:
        """
        JSON 파일에서 검색 결과 로드

        Args:
            filepath: 파일 경로

        Returns:
            SearchResult 객체 또는 None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return SearchResult.from_dict(data)

        except Exception as e:
            print(f"JSON 로드 오류: {str(e)}")
            return None

    def save_patents_csv(
        self,
        patents: List[Patent],
        filename: Optional[str] = None,
        fields: Optional[List[str]] = None
    ) -> str:
        """
        특허 목록을 CSV 파일로 저장

        Args:
            patents: Patent 객체 리스트
            filename: 파일명 (없으면 자동 생성)
            fields: 저장할 필드 목록 (없으면 기본 필드 사용)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"patents_{timestamp}.csv"

        filepath = self.base_path / filename

        if fields is None:
            fields = [
                'id', 'title', 'application_number', 'application_date',
                'registration_number', 'registration_date',
                'status', 'country', 'abstract', 'source'
            ]

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()

                for patent in patents:
                    patent_dict = patent.to_dict()
                    # 리스트 필드를 문자열로 변환
                    row = {}
                    for field in fields:
                        value = patent_dict.get(field, '')
                        if isinstance(value, list):
                            row[field] = ', '.join(str(v) for v in value)
                        else:
                            row[field] = value
                    writer.writerow(row)

            print(f"CSV 저장 완료: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"CSV 저장 오류: {str(e)}")
            raise

    def save_patents_excel(
        self,
        patents: List[Patent],
        filename: Optional[str] = None
    ) -> str:
        """
        특허 목록을 Excel 파일로 저장

        Args:
            patents: Patent 객체 리스트
            filename: 파일명 (없으면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"patents_{timestamp}.xlsx"

        filepath = self.base_path / filename

        try:
            import pandas as pd

            # DataFrame 생성
            data = []
            for patent in patents:
                patent_dict = patent.to_dict()

                # 복잡한 객체를 간단한 문자열로 변환
                row = {
                    'ID': patent.id,
                    '제목': patent.title,
                    '출원번호': patent.application_number,
                    '출원일': patent.application_date,
                    '등록번호': patent.registration_number or '',
                    '등록일': patent.registration_date or '',
                    '상태': patent.status or '',
                    '국가': patent.country or '',
                    '초록': patent.abstract or '',
                    '출원인': ', '.join([a.name for a in patent.applicants]),
                    '발명자': ', '.join([i.name for i in patent.inventors]),
                    'IPC': ', '.join(patent.get_ipc_codes()),
                    '출처': patent.source
                }
                data.append(row)

            df = pd.DataFrame(data)

            # Excel 저장
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='특허 목록')

                # 열 너비 자동 조정
                worksheet = writer.sheets['특허 목록']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

            print(f"Excel 저장 완료: {filepath}")
            return str(filepath)

        except ImportError:
            print("pandas 또는 openpyxl이 설치되지 않았습니다.")
            raise
        except Exception as e:
            print(f"Excel 저장 오류: {str(e)}")
            raise

    def save_patent_detail_text(
        self,
        patent: Patent,
        filename: Optional[str] = None
    ) -> str:
        """
        특허 상세 정보를 텍스트 파일로 저장

        Args:
            patent: Patent 객체
            filename: 파일명 (없으면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            safe_id = patent.id.replace('/', '_').replace('\\', '_')
            filename = f"patent_{safe_id}.txt"

        filepath = self.base_path / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"특허 상세 정보\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"ID: {patent.id}\n")
                f.write(f"제목: {patent.title}\n\n")

                f.write(f"출원번호: {patent.application_number}\n")
                f.write(f"출원일: {patent.application_date}\n")

                if patent.registration_number:
                    f.write(f"등록번호: {patent.registration_number}\n")
                if patent.registration_date:
                    f.write(f"등록일: {patent.registration_date}\n")

                f.write(f"상태: {patent.status or 'N/A'}\n")
                f.write(f"국가: {patent.country or 'N/A'}\n\n")

                # 출원인
                if patent.applicants:
                    f.write("출원인:\n")
                    for applicant in patent.applicants:
                        f.write(f"  - {applicant.name}")
                        if applicant.country:
                            f.write(f" ({applicant.country})")
                        f.write("\n")
                    f.write("\n")

                # 발명자
                if patent.inventors:
                    f.write("발명자:\n")
                    for inventor in patent.inventors:
                        f.write(f"  - {inventor.name}")
                        if inventor.country:
                            f.write(f" ({inventor.country})")
                        f.write("\n")
                    f.write("\n")

                # IPC 분류
                ipc_codes = patent.get_ipc_codes()
                if ipc_codes:
                    f.write(f"IPC 분류: {', '.join(ipc_codes)}\n\n")

                # 초록
                if patent.abstract:
                    f.write("-" * 80 + "\n")
                    f.write("초록\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"{patent.abstract}\n\n")

                # 청구항
                if patent.claims:
                    f.write("-" * 80 + "\n")
                    f.write("청구항\n")
                    f.write("-" * 80 + "\n")
                    for claim in patent.claims:
                        f.write(f"[청구항 {claim.number}]\n")
                        f.write(f"{claim.text}\n\n")

                # URL
                if patent.url:
                    f.write(f"\nURL: {patent.url}\n")

                f.write(f"\n출처: {patent.source}\n")
                f.write("=" * 80 + "\n")

            print(f"텍스트 저장 완료: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"텍스트 저장 오류: {str(e)}")
            raise

    def list_saved_files(self, extension: Optional[str] = None) -> List[str]:
        """
        저장된 파일 목록 조회

        Args:
            extension: 파일 확장자 필터 (예: '.json', '.csv')

        Returns:
            파일 경로 리스트
        """
        try:
            if extension:
                files = list(self.base_path.glob(f"*{extension}"))
            else:
                files = list(self.base_path.glob("*"))

            return [str(f) for f in files if f.is_file()]

        except Exception as e:
            print(f"파일 목록 조회 오류: {str(e)}")
            return []

    def delete_file(self, filename: str) -> bool:
        """
        파일 삭제

        Args:
            filename: 파일명

        Returns:
            삭제 성공 여부
        """
        try:
            filepath = self.base_path / filename
            if filepath.exists():
                filepath.unlink()
                return True
            return False

        except Exception as e:
            print(f"파일 삭제 오류: {str(e)}")
            return False
